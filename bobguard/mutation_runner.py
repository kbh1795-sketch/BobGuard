"""
BobGuard — Mutation Runner
===========================
Orchestrates the full mutation testing cycle:

  For each mutation in MUTATIONS:
    1. Monkey-patch UAVStateMachine with the mutant method (class-level)
    2. Run all auto-generated failure combination scenarios through
       the TracingStateMachine + violation detector
    3. Collect the first scenario that exposes the bug
    4. Restore the original method
    5. Record a MutationResult

After all mutations are tested the original implementation is run once
more to confirm zero regressions.

No source file is ever written or modified.
"""

import types
from dataclasses import dataclass, field
from typing import Optional

from bobguard.uav_failsafe import UAVStateMachine, State
from bobguard.tracer import TracingStateMachine
from bobguard.violation_detector import detect_violations, classify_overall_severity
from bobguard.combination_generator import generate_all_combinations
from bobguard.scenarios import SCENARIOS
from bobguard.regression_scenarios import REGRESSION_SCENARIOS
from bobguard.mutations import Mutation, MUTATIONS


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class ExposureRecord:
    """A single scenario that exposed the mutation."""
    scenario_name: str
    state_trace: str
    violation_types: list[str]
    severities: list[str]
    final_state: State


@dataclass
class MutationResult:
    mutation: Mutation
    detected: bool
    exposures: list[ExposureRecord]   # all scenarios that caught it
    first_exposure: Optional[ExposureRecord]  # convenience shortcut


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def _all_scenarios() -> list[dict]:
    """Return the complete scenario pool used for mutation probing."""
    def _tag(s, cat):
        if "category" not in s:
            s = dict(s)
            s["category"] = cat
        return s

    return (
        [_tag(s, "original")    for s in SCENARIOS]
        + [_tag(s, "regression") for s in REGRESSION_SCENARIOS]
        + generate_all_combinations()
    )


def _run_scenario_with_mutation(scenario: dict) -> tuple[bool, Optional[ExposureRecord]]:
    """
    Execute one scenario against the (already-patched) TracingStateMachine.
    Returns (violation_found, ExposureRecord | None).
    """
    sm = TracingStateMachine()
    for method_name, arg in scenario["steps"]:
        method = getattr(sm, method_name)
        if arg is not None:
            method(arg)
        else:
            method()

    violations = detect_violations(sm, scenario)
    if not violations:
        return False, None

    record = ExposureRecord(
        scenario_name=scenario["name"],
        state_trace=sm.render_trace(),
        violation_types=[v.violation_type for v in violations],
        severities=list({v.severity for v in violations}),
        final_state=sm.state,
    )
    return True, record


def _patch_method(target: str, mutant_fn) -> callable:
    """
    Replace UAVStateMachine.<target> with mutant_fn (bound as instance method).
    Returns the original method so it can be restored.
    """
    original = getattr(UAVStateMachine, target)
    setattr(UAVStateMachine, target, mutant_fn)
    return original


def _restore_method(target: str, original) -> None:
    setattr(UAVStateMachine, target, original)


# ---------------------------------------------------------------------------
# Main mutation runner
# ---------------------------------------------------------------------------

def run_mutation(mutation: Mutation, scenarios: list[dict]) -> MutationResult:
    """
    Inject mutation, run all scenarios, restore, return result.
    Never touches any source file.
    """
    print(f"  [{mutation.id}] Injecting: {mutation.name}")

    # 1 — Inject
    original = _patch_method(mutation.patch_target, mutation.mutant_fn)

    exposures: list[ExposureRecord] = []
    try:
        # 2 — Probe
        for scenario in scenarios:
            found, record = _run_scenario_with_mutation(scenario)
            if found and record:
                # Check if this exposure matches expected violation types
                hits = set(record.violation_types) & set(mutation.expected_violations)
                sev_hits = set(record.severities) & set(mutation.expected_severities)
                if hits or sev_hits:
                    exposures.append(record)
    finally:
        # 3 — Always restore, even on exception
        _restore_method(mutation.patch_target, original)

    detected = len(exposures) > 0
    status = "DETECTED" if detected else "MISSED"
    n = len(exposures)
    print(f"         {status} — {n} triggering scenario(s)")

    return MutationResult(
        mutation=mutation,
        detected=detected,
        exposures=exposures,
        first_exposure=exposures[0] if exposures else None,
    )


def run_all_mutations(scenarios: list[dict] | None = None) -> list[MutationResult]:
    if scenarios is None:
        scenarios = _all_scenarios()

    print()
    print("BobGuard Mutation Testing")
    print("-------------------------")
    print(f"  Scenarios in probe pool: {len(scenarios)}")
    print(f"  Mutations to test:       {len(MUTATIONS)}")
    print()

    results = []
    for mutation in MUTATIONS:
        result = run_mutation(mutation, scenarios)
        results.append(result)

    detected = sum(1 for r in results if r.detected)
    total = len(results)
    rate = int(100 * detected / total) if total else 0

    print()
    print(f"  Detected: {detected}/{total}  ({rate}%)")
    print()
    return results


# ---------------------------------------------------------------------------
# Post-mutation sanity check — original implementation must still pass all
# ---------------------------------------------------------------------------

def verify_original_unmodified(scenarios: list[dict] | None = None) -> tuple[int, int]:
    """
    Run all scenarios against the unmodified TracingStateMachine.
    Returns (passed, total).
    """
    if scenarios is None:
        scenarios = _all_scenarios()

    passed = 0
    total = len(scenarios)
    for scenario in scenarios:
        sm = TracingStateMachine()
        for method_name, arg in scenario["steps"]:
            method = getattr(sm, method_name)
            if arg is not None:
                method(arg)
            else:
                method()

        expected = scenario.get("expected_state")
        visited_post = {ev.to_state for ev in sm.trace}
        forbidden = scenario.get("forbidden", set())
        final_ok = (expected is None) or (sm.state == expected)
        forbidden_ok = not (forbidden & visited_post)
        if final_ok and forbidden_ok:
            passed += 1

    return passed, total
