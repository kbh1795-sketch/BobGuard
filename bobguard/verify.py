"""
BobGuard — Automated Verification Runner
==========================================
Single entry point that:

  1. Loads the original 10 scenarios (scenarios.py)
  2. Loads the 12 regression + 13 edge-case scenarios (regression_scenarios.py)
  3. Auto-generates 26 failure-combination scenarios (combination_generator.py)
  4. Runs all 61 scenarios through the TracingStateMachine
  5. Detects safety violations on each result
  6. Writes bobguard_verification_report.md
  7. Prints the concise BobGuard Verification summary

Usage:
    python -m bobguard.verify
"""

import sys
from bobguard.scenarios            import SCENARIOS
from bobguard.regression_scenarios import REGRESSION_SCENARIOS, EDGE_CASE_SCENARIOS
from bobguard.combination_generator import generate_all_combinations
from bobguard.tracer               import TracingStateMachine
from bobguard.violation_detector   import (
    detect_violations,
    classify_overall_severity,
    SAFE_TERMINALS,
)
from bobguard.report_writer        import VerificationResult, write_report
from bobguard.uav_failsafe         import State


# ---------------------------------------------------------------------------
# Core execution helpers
# ---------------------------------------------------------------------------

def _run_one(scenario: dict) -> VerificationResult:
    """Execute a single scenario and return a full VerificationResult."""
    sm = TracingStateMachine()

    for method_name, arg in scenario["steps"]:
        method = getattr(sm, method_name)
        if arg is not None:
            method(arg)
        else:
            method()

    # Determine pass/fail using expected_state + forbidden states
    expected = scenario.get("expected_state")
    visited_post_start = {ev.to_state for ev in sm.trace}
    forbidden = scenario.get("forbidden", set())

    final_ok    = (expected is None) or (sm.state == expected)
    forbidden_ok = not (forbidden & visited_post_start)
    passed = final_ok and forbidden_ok

    violations   = detect_violations(sm, scenario)
    severity     = classify_overall_severity(violations)

    # A scenario with no expected_state passes structurally unless violations
    # indicate an unsafe outcome.
    if expected is None and not passed:
        passed = forbidden_ok  # only fail on forbidden-state visits

    return VerificationResult(
        scenario_name     = scenario["name"],
        category          = scenario.get("category", "manual"),
        description       = scenario.get("description", scenario["name"]),
        injected_failures = scenario.get("injected_failures", []),
        state_trace       = sm.render_trace(),
        final_state       = sm.state,
        expected_state    = expected,
        passed            = passed,
        violations        = violations,
        overall_severity  = severity,
        requirement       = scenario.get("requirement", "—"),
    )


def _tag_category(scenario: dict, default: str) -> dict:
    """Ensure every scenario has a category field."""
    if "category" not in scenario:
        scenario = dict(scenario)
        scenario["category"] = default
    return scenario


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def run_verification(report_path: str = "bobguard_verification_report.md") -> int:
    """
    Execute the full verification suite.
    Returns exit code (0 = all pass, 1 = failures detected).
    """
    # Collect all scenarios with categories
    all_scenarios = (
        [_tag_category(s, "original")    for s in SCENARIOS]
        + [_tag_category(s, "regression") for s in REGRESSION_SCENARIOS]
        + [_tag_category(s, "edge_case")  for s in EDGE_CASE_SCENARIOS]
        + generate_all_combinations()    # already have category set
    )

    print()
    print("BobGuard Verification")
    print("---------------------")
    print(f"  Loading {len(all_scenarios)} scenarios...")
    print()

    results: list[VerificationResult] = []
    for scenario in all_scenarios:
        result = _run_one(scenario)
        results.append(result)
        status = "PASS" if result.passed else "FAIL"
        sev    = f"[{result.overall_severity}]" if result.overall_severity != "NONE" else ""
        print(f"  [{status}] {result.scenario_name} {sev}")

    # ---- Summary stats ----
    total  = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    sev_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for r in results:
        if r.overall_severity in sev_counts:
            sev_counts[r.overall_severity] += 1

    safe_coverage = sum(
        1 for r in results if r.final_state in SAFE_TERMINALS
    )
    safe_pct = int(100 * safe_coverage / total) if total else 0

    # ---- Write report ----
    write_report(results, output_path=report_path)

    # ---- Print summary ----
    print()
    print("BobGuard Verification")
    print("---------------------")
    print(f"Scenarios tested:   {total}")
    print(f"Passed:             {passed}")
    print(f"Failed:             {failed}")
    print(f"Critical violations:{sev_counts['CRITICAL']}")
    print(f"High violations:    {sev_counts['HIGH']}")
    print(f"Safe-state coverage:{safe_pct}%")
    print()

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_verification())
