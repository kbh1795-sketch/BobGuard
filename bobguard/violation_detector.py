"""
BobGuard — Safety Violation Detector & Risk Classifier
========================================================
Analyses a completed TracingStateMachine execution and returns a list of
ViolationReport objects describing every detected safety issue.

Violation types
---------------
STUCK_IN_LOITER         — scenario ends in LOITER with no active failures
                          (no clear exit path; unexpected state)
LOITER_ACTIVE_FAILURE   — scenario ends in LOITER while failures remain;
                          LOITER is the intended contingency — operational info
RETURN_HOME_WITHOUT_GPS — RETURN_HOME state entered while gps_loss is active
AIRBORNE_CRITICAL_BATT  — critical_battery active but UAV never reached LAND
NO_SAFE_TERMINAL        — final state is not in {NORMAL, LAND, TERMINATED}
UNEXPECTED_TRANSITION   — state changed in a way that violates a known rule

Risk levels
-----------
LOW      — informational; no immediate safety impact
MEDIUM   — degrades safety margin; should be addressed
HIGH     — likely unsafe operation; fix required
CRITICAL — immediate danger; unacceptable in deployed system
"""

from dataclasses import dataclass, field
from typing import Optional
from bobguard.uav_failsafe import State
from bobguard.tracer import TracingStateMachine, TraceEvent

# Safe terminal and safe holding states
SAFE_TERMINALS = {State.NORMAL, State.LAND, State.TERMINATED}


@dataclass
class ViolationReport:
    violation_type: str
    severity: str          # LOW | MEDIUM | HIGH | CRITICAL
    description: str
    recommended_fix: str
    evidence: str = ""     # relevant trace snippet


def detect_violations(sm: TracingStateMachine, scenario: dict) -> list[ViolationReport]:
    """
    Inspect a fully-executed TracingStateMachine and return all violations.

    Parameters
    ----------
    sm       : executed TracingStateMachine (steps already run)
    scenario : the scenario dict that drove the execution
    """
    violations: list[ViolationReport] = []
    final_state = sm.state
    injected = set(scenario.get("injected_failures", []))

    # Expected final state — if the scenario explicitly expects LOITER or
    # RETURN_HOME those are intentional test assertions, not violations.
    expected = scenario.get("expected_state")

    # ------------------------------------------------------------------
    # V1 — UAV in LOITER at end of scenario
    #      Two sub-cases:
    #        (a) Active failures present → LOITER is the intended contingency
    #            state (R1 comm_loss, R5 gps_loss, R8 RTH+comm_loss+gps).
    #            Emit LOW informational diagnostic only.
    #        (b) No active failures → UAV is genuinely stuck; emit HIGH.
    #      Skip entirely when the scenario explicitly expects LOITER.
    # ------------------------------------------------------------------
    if final_state == State.LOITER and expected != State.LOITER:
        active_flags_at_end = sm.trace[-1].active_flags if sm.trace else {}
        has_active_failure = any(
            active_flags_at_end.get(f)
            for f in ("communication_loss", "gps_loss", "critical_battery")
        )

        if has_active_failure:
            violations.append(ViolationReport(
                violation_type="LOITER_ACTIVE_FAILURE",
                severity="LOW",
                description=(
                    "UAV ended scenario in LOITER while active failures remain. "
                    "LOITER is the defined contingency state for this condition "
                    "(R1 / R5 / R8). This is expected operational behaviour, "
                    "not a safety defect."
                ),
                recommended_fix=(
                    "No corrective action required. Consider a timeout-to-LAND "
                    "requirement if failures persist beyond battery endurance."
                ),
                evidence=(
                    f"Final state: {final_state.value}. "
                    f"Active failures: "
                    f"{ {k: v for k, v in active_flags_at_end.items() if v} }"
                ),
            ))
        else:
            violations.append(ViolationReport(
                violation_type="STUCK_IN_LOITER",
                severity="HIGH",
                description=(
                    "UAV ended scenario in LOITER with no active failures. "
                    "All failure conditions are clear but the UAV has not "
                    "returned to NORMAL. Indefinite loitering depletes battery "
                    "and may cause an uncontrolled crash."
                ),
                recommended_fix=(
                    "Ensure every LOITER state has a timed or condition-based "
                    "exit — either to NORMAL (on full recovery) or to LAND "
                    "(on timeout / battery threshold)."
                ),
                evidence=f"Final state: {final_state.value}. No active failures detected.",
            ))

    # ------------------------------------------------------------------
    # V2 — RETURN_HOME entered while GPS unavailable
    #      Skip when the scenario explicitly tests that blocking works
    #      (expected_state == LOITER means the block is the desired outcome).
    # ------------------------------------------------------------------
    rth_without_gps = [
        ev for ev in sm.trace
        if ev.to_state == State.RETURN_HOME and ev.active_flags.get("gps_loss")
    ]
    if rth_without_gps and expected != State.LOITER:
        ev = rth_without_gps[0]
        violations.append(ViolationReport(
            violation_type="RETURN_HOME_WITHOUT_GPS",
            severity="CRITICAL",
            description=(
                "UAV entered RETURN_HOME while gps_loss was active. "
                "Autonomous navigation without GPS will result in loss "
                "of vehicle or collision."
            ),
            recommended_fix=(
                "Guard every path into RETURN_HOME (both operator commands "
                "and automatic transitions) against the gps_loss flag. "
                "Divert to LOITER or LAND when GPS is unavailable."
            ),
            evidence=(
                f"Step {ev.step_index}: "
                f"{ev.from_state.value} -> RETURN_HOME "
                f"(trigger={ev.trigger})"
            ),
        ))

    # ------------------------------------------------------------------
    # V3 — Critical battery active but UAV never reached LAND
    # ------------------------------------------------------------------
    if "critical_battery" in injected and final_state not in {State.LAND, State.TERMINATED}:
        violations.append(ViolationReport(
            violation_type="AIRBORNE_CRITICAL_BATT",
            severity="CRITICAL",
            description=(
                "critical_battery was injected but the UAV never reached "
                "LAND or TERMINATED. An airborne UAV on empty battery will "
                "crash uncontrollably."
            ),
            recommended_fix=(
                "Ensure critical_battery triggers an immediate LAND "
                "transition from every airborne state: NORMAL, LOITER, "
                "and RETURN_HOME."
            ),
            evidence=f"Injected failures: {injected}. Final state: {final_state.value}",
        ))

    # ------------------------------------------------------------------
    # V4 — Final state is not a recognised safe state
    #      LOITER already covered by V1; skip when explicitly expected
    # ------------------------------------------------------------------
    if final_state not in SAFE_TERMINALS and final_state != State.LOITER and expected != final_state:
        # LOITER is already covered by V1; this catches truly unknown states
        violations.append(ViolationReport(
            violation_type="NO_SAFE_TERMINAL",
            severity="HIGH",
            description=(
                f"Scenario ended in {final_state.value}, which is not a "
                "recognised safe terminal state (NORMAL, LAND, TERMINATED). "
                "The UAV is in an undefined operational condition."
            ),
            recommended_fix=(
                "Every scenario must terminate in NORMAL, LAND, or "
                "TERMINATED. Add catch-all transitions from unexpected "
                "states to LAND."
            ),
            evidence=f"Final state: {final_state.value}",
        ))

    # ------------------------------------------------------------------
    # V5 — RETURN_HOME reached with critical battery (no land transition)
    # ------------------------------------------------------------------
    rth_with_batt = [
        ev for ev in sm.trace
        if ev.to_state == State.RETURN_HOME
        and ev.active_flags.get("critical_battery")
    ]
    if rth_with_batt:
        violations.append(ViolationReport(
            violation_type="AIRBORNE_CRITICAL_BATT",
            severity="CRITICAL",
            description=(
                "UAV entered or remained in RETURN_HOME while "
                "critical_battery was active. Battery will expire before "
                "reaching home."
            ),
            recommended_fix=(
                "Intercept critical_battery in the RETURN_HOME state and "
                "immediately transition to LAND."
            ),
            evidence=(
                f"Step {rth_with_batt[0].step_index}: "
                f"transitioned to RETURN_HOME with critical_battery=True"
            ),
        ))

    # ------------------------------------------------------------------
    # V6 — explicit expected_state mismatch (scenario-defined assertion)
    # ------------------------------------------------------------------
    if expected is not None and final_state != expected:
        sev = "CRITICAL" if expected in {State.LAND} else "HIGH"
        violations.append(ViolationReport(
            violation_type="UNEXPECTED_TRANSITION",
            severity=sev,
            description=(
                f"Scenario expected final state {expected.value} "
                f"but got {final_state.value}."
            ),
            recommended_fix=(
                "Review the transition logic for the failure sequence "
                f"{scenario.get('injected_failures', [])} and ensure "
                f"it always reaches {expected.value}."
            ),
            evidence=(
                f"Expected={expected.value}, "
                f"Actual={final_state.value}, "
                f"Trace: {sm.history[-3:]}"
            ),
        ))

    # ------------------------------------------------------------------
    # V7 — forbidden state visited during scenario
    # ------------------------------------------------------------------
    visited_post_start = {ev.to_state for ev in sm.trace}
    forbidden = scenario.get("forbidden", set())
    for bad_state in forbidden & visited_post_start:
        violations.append(ViolationReport(
            violation_type="FORBIDDEN_STATE_VISITED",
            severity="CRITICAL",
            description=(
                f"UAV entered the forbidden state {bad_state.value} "
                "during this scenario."
            ),
            recommended_fix=(
                f"Add guards to prevent transitions into {bad_state.value} "
                "when the active failure context makes it unsafe."
            ),
            evidence=f"Forbidden state {bad_state.value} appeared in trace.",
        ))

    return violations


def classify_overall_severity(violations: list[ViolationReport]) -> str:
    """Return the highest severity across all violations."""
    order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    if not violations:
        return "NONE"
    return max(violations, key=lambda v: order.get(v.severity, 0)).severity
