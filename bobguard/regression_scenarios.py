"""
BobGuard — Regression Tests: Simultaneous Failures
====================================================
Additional scenarios covering combinations of two or more concurrent failures.
These exercise the fixed state machine to ensure no regression.
"""

from bobguard.uav_failsafe import State

REGRESSION_SCENARIOS = [
    # ---- Simultaneous comm_loss + gps_loss ----
    # Both failures fire; no battery issue. After restoration UAV must return to NORMAL.
    {
        "name": "REG1_simultaneous_comm_and_gps_loss_then_restore",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("apply_failure", "gps_loss"),
            ("restore", "gps_loss"),
            ("restore", "communication_loss"),
        ],
        "expected_state": State.NORMAL,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R6+R7",
    },

    # ---- Simultaneous comm_loss + critical_battery ----
    # Battery beats loiter — must land regardless of comms.
    {
        "name": "REG2_simultaneous_comm_loss_and_critical_battery",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R4+R3",
    },

    # ---- Simultaneous gps_loss + critical_battery ----
    # Battery critical while GPS is out — must land.
    {
        "name": "REG3_simultaneous_gps_loss_and_critical_battery",
        "steps": [
            ("apply_failure", "gps_loss"),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R3+R5",
    },

    # ---- All three failures simultaneously ----
    {
        "name": "REG4_all_three_failures_simultaneously",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("apply_failure", "gps_loss"),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R3+R4+R5+R7",
    },

    # ---- GPS lost during RETURN_HOME, then battery also critical ----
    {
        "name": "REG5_return_home_gps_loss_then_critical_battery",
        "steps": [
            ("command_return_home", None),  # -> RETURN_HOME
            ("apply_failure", "gps_loss"),  # -> LOITER (gps_loss)
            ("apply_failure", "critical_battery"),  # -> LAND
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R3+R5",
    },

    # ---- Comm restored but gps still out — must NOT return to NORMAL ----
    # (UAV should stay in LOITER until GPS is also restored)
    {
        "name": "REG6_comm_restored_gps_still_lost_stays_loiter",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("apply_failure", "gps_loss"),
            ("restore", "communication_loss"),   # comm ok, but gps still lost
        ],
        "expected_state": State.LOITER,
        "forbidden": {State.NORMAL, State.RETURN_HOME},
        "requirement": "R6",
    },

    # ---- Return-home blocked when GPS lost; battery then critical → LAND ----
    {
        "name": "REG7_gps_loss_blocks_rth_then_critical_battery_lands",
        "steps": [
            ("apply_failure", "gps_loss"),
            ("command_return_home", None),    # blocked -> LOITER
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R3+R5",
    },

    # ---- Operator kill-switch always reachable from any state ----
    {
        "name": "REG8_terminate_from_loiter",
        "steps": [
            ("apply_failure", "communication_loss"),  # -> LOITER
            ("command_terminate", None),
        ],
        "expected_state": State.TERMINATED,
        "forbidden": set(),
        "requirement": "R7",
    },

    # ---- No further transitions from LAND (terminal) ----
    {
        "name": "REG9_no_transition_from_land_terminal",
        "steps": [
            ("apply_failure", "critical_battery"),    # -> LAND
            ("apply_failure", "communication_loss"),  # must be ignored
        ],
        "expected_state": State.LAND,
        "forbidden": {State.LOITER, State.RETURN_HOME},
        "requirement": "R7",
    },

    # ---- No further transitions from TERMINATED (terminal) ----
    {
        "name": "REG10_no_transition_from_terminated_terminal",
        "steps": [
            ("command_terminate", None),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.TERMINATED,
        "forbidden": {State.LAND, State.LOITER},
        "requirement": "R7",
    },

    # ---- Comm loss, partial restoration still leaves loiter until fully safe ----
    {
        "name": "REG11_battery_critical_comm_restored_stays_land",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("apply_failure", "critical_battery"),    # -> LAND (via LOITER)
            ("restore", "communication_loss"),        # already LAND, no change
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R3+R7",
    },

    # ---- GPS loss then restore, UAV returns to NORMAL ----
    {
        "name": "REG12_gps_loss_restore_returns_to_normal",
        "steps": [
            ("apply_failure", "gps_loss"),
            ("restore", "gps_loss"),
        ],
        "expected_state": State.NORMAL,
        "forbidden": {State.LOITER, State.RETURN_HOME},
        "requirement": "R7",
    },
]

# ---------------------------------------------------------------------------
# Edge-case regression tests — added by independent analysis
# ---------------------------------------------------------------------------

EDGE_CASE_SCENARIOS = [

    # ---- ECT1 — comm_loss while in RETURN_HOME, GPS available (R8 policy) ----
    # R8 explicitly permits RETURN_HOME to continue when comm is lost but
    # GPS remains available.  With GPS intact the UAV has full navigation
    # capability; interrupting the return would be more hazardous.
    # EXPECTED: UAV stays in RETURN_HOME (correct per R8, not a defect).
    {
        "name": "ECT1_comm_loss_during_return_home_gps_ok",
        "steps": [
            ("command_return_home", None),            # NORMAL → RETURN_HOME
            ("apply_failure", "communication_loss"),  # GPS available → stays RETURN_HOME (R8)
        ],
        "expected_state": State.RETURN_HOME,          # compliant with R8
        "forbidden": set(),
        "requirement": "R8",
        "description": (
            "R8 policy: comm_loss during RETURN_HOME with GPS available. "
            "RETURN_HOME must continue — GPS provides full navigation capability. "
            "Forcing LOITER here would violate R8 and increase risk. "
            "Expected result: UAV remains in RETURN_HOME (PASS, policy-compliant)."
        ),
    },

    # ---- ECT2 — comm_loss applied twice (idempotent) ----
    # Applying the same failure a second time must not corrupt state.
    {
        "name": "ECT2_duplicate_comm_loss_idempotent",
        "steps": [
            ("apply_failure", "communication_loss"),  # → LOITER
            ("apply_failure", "communication_loss"),  # duplicate; must stay LOITER
        ],
        "expected_state": State.LOITER,
        "forbidden": {State.NORMAL, State.RETURN_HOME},
        "requirement": "R1",
        "description": (
            "Applying communication_loss twice must not change state beyond "
            "the initial LOITER transition — idempotency check."
        ),
    },

    # ---- ECT3 — gps_loss applied twice (idempotent from NORMAL) ----
    # GPS loss alone from NORMAL leaves state in NORMAL (no transition).
    # A second application must not trigger any new transition.
    {
        "name": "ECT3_duplicate_gps_loss_idempotent",
        "steps": [
            ("apply_failure", "gps_loss"),   # NORMAL stays NORMAL
            ("apply_failure", "gps_loss"),   # duplicate; must stay NORMAL
        ],
        "expected_state": State.NORMAL,
        "forbidden": {State.LOITER, State.RETURN_HOME, State.LAND},
        "requirement": "R5",
        "description": (
            "GPS loss alone from NORMAL leaves UAV in NORMAL. "
            "A duplicate injection must not cause any unexpected transition."
        ),
    },

    # ---- ECT4 — repeated comm_loss / restore cycle ----
    # Two full oscillations: the state must finish at NORMAL and must
    # never visit RETURN_HOME.
    {
        "name": "ECT4_repeated_comm_loss_restore_cycle",
        "steps": [
            ("apply_failure", "communication_loss"),   # → LOITER
            ("restore", "communication_loss"),          # → NORMAL
            ("apply_failure", "communication_loss"),   # → LOITER (second cycle)
            ("restore", "communication_loss"),          # → NORMAL
        ],
        "expected_state": State.NORMAL,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R1+R2",
        "description": (
            "Two full comm_loss/restore cycles. "
            "Each restore must cleanly return to NORMAL (R2); "
            "final state must be NORMAL."
        ),
    },

    # ---- ECT5 — restore a failure that was never injected ----
    # restore("gps_loss") called from NORMAL without prior injection.
    # Flag is already False; _evaluate fires but no flags are active →
    # LOITER→NORMAL guard doesn't fire (not in LOITER). Must stay NORMAL.
    {
        "name": "ECT5_restore_never_injected_failure",
        "steps": [
            ("restore", "gps_loss"),   # clears already-False flag; no-op
        ],
        "expected_state": State.NORMAL,
        "forbidden": {State.LOITER, State.RETURN_HOME, State.LAND},
        "requirement": "R7",
        "description": (
            "Calling restore() for a failure that was never injected must be "
            "a safe no-op — UAV must remain in NORMAL."
        ),
    },

    # ---- ECT6 — command_terminate overrides LAND terminal ----
    # LAND is listed in TERMINAL_STATES but command_terminate has no
    # terminal guard.  This tests whether terminate can escape LAND.
    {
        "name": "ECT6_terminate_overrides_land_terminal",
        "steps": [
            ("apply_failure", "critical_battery"),  # → LAND (terminal)
            ("command_terminate", None),             # → TERMINATED?
        ],
        "expected_state": State.TERMINATED,
        "forbidden": set(),
        "requirement": "R7",
        "description": (
            "command_terminate has no TERMINAL_STATES guard; kill-switch "
            "applied after LAND should transition to TERMINATED. "
            "Verifies the kill-switch always takes precedence."
        ),
    },

    # ---- ECT7 — full recovery after GPS disruption during RTH ----
    # RTH → GPS lost → LOITER; GPS restored → NORMAL.
    # Combines R5b with the LOITER→NORMAL recovery path.
    {
        "name": "ECT7_rth_gps_loss_recover_to_normal",
        "steps": [
            ("command_return_home", None),   # → RETURN_HOME
            ("apply_failure", "gps_loss"),   # → LOITER (gps_loss branch)
            ("restore", "gps_loss"),         # → NORMAL (all flags clear)
        ],
        "expected_state": State.NORMAL,
        "forbidden": {State.LAND},
        "requirement": "R2+R5",
        "description": (
            "GPS lost during RTH → LOITER, then GPS restored → NORMAL. "
            "Tests the complete recovery path after partial RTH failure."
        ),
    },

    # ---- ECT8 — operator command_land from RETURN_HOME ----
    # Operator issues land command mid-flight during RTH.
    # No existing scenario tests command_land from RETURN_HOME.
    {
        "name": "ECT8_command_land_from_return_home",
        "steps": [
            ("command_return_home", None),  # → RETURN_HOME
            ("command_land", None),          # → LAND (operator override)
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R7",
        "description": (
            "Operator issues command_land while UAV is in RETURN_HOME. "
            "Immediate land must be respected (R7 operator override)."
        ),
    },

    # ---- ECT9 — operator command_land from LOITER ----
    # Operator issues land command while UAV is loitering due to comm_loss.
    {
        "name": "ECT9_command_land_from_loiter",
        "steps": [
            ("apply_failure", "communication_loss"),  # → LOITER
            ("command_land", None),                    # → LAND
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R7",
        "description": (
            "Operator issues command_land while UAV is in LOITER. "
            "Must immediately transition to LAND."
        ),
    },

    # ---- ECT10 — restore comm_loss during RETURN_HOME with GPS available (R8 recovery) ----
    # Per R8: comm_loss during RETURN_HOME with GPS available does not interrupt
    # the return.  When comm is subsequently restored, no state transition
    # should occur — the UAV was and remains in RETURN_HOME throughout.
    # This verifies R8 symmetry: entry is safe, exit (restore) is also clean.
    {
        "name": "ECT10_restore_comm_loss_while_in_rth_gps_ok",
        "steps": [
            ("command_return_home", None),            # → RETURN_HOME
            ("apply_failure", "communication_loss"),  # GPS ok → stays RETURN_HOME (R8)
            ("restore", "communication_loss"),        # comm restored → stays RETURN_HOME
        ],
        "expected_state": State.RETURN_HOME,
        "forbidden": set(),
        "requirement": "R8",
        "description": (
            "R8 policy: comm_loss then comm-restore while in RETURN_HOME with GPS available. "
            "Neither event should interrupt the return journey. "
            "State must remain RETURN_HOME throughout (PASS, policy-compliant)."
        ),
    },

    # ---- ECT11 — comm_loss + critical_battery from NORMAL (BUG-1 path) ----
    # BUG-1: critical_battery arrives simultaneously with comm_loss.
    # From NORMAL with comm_loss: → LOITER (BUG-1 doesn't re-check battery).
    # Then critical_battery flag is set, _evaluate called: comm_loss=True,
    # state=LOITER, critical_battery=True → LAND.  So the two-step path
    # does eventually reach LAND — but only because critical_battery was
    # the second event.  This is already tested by R4b; add reversed order.
    # Reversed: critical_battery FIRST (from NORMAL) → LAND immediately,
    # then comm_loss fires → terminal guard ignores it.
    {
        "name": "ECT11_critical_battery_first_then_comm_loss",
        "steps": [
            ("apply_failure", "critical_battery"),   # NORMAL → LAND (terminal)
            ("apply_failure", "communication_loss"), # terminal guard → ignored
        ],
        "expected_state": State.LAND,
        "forbidden": {State.LOITER},
        "requirement": "R3+R4",
        "description": (
            "Critical battery fires before comm_loss. "
            "UAV must land immediately from NORMAL without visiting LOITER. "
            "Subsequent comm_loss must be ignored (terminal guard)."
        ),
    },

    # ---- ECT12 — restore after LAND terminal does nothing ----
    {
        "name": "ECT12_restore_all_from_land_terminal",
        "steps": [
            ("apply_failure", "critical_battery"),    # → LAND
            ("restore", "critical_battery"),          # terminal guard → no change
            ("restore", "communication_loss"),        # terminal guard → no change
            ("restore", "gps_loss"),                  # terminal guard → no change
        ],
        "expected_state": State.LAND,
        "forbidden": {State.NORMAL, State.LOITER, State.RETURN_HOME},
        "requirement": "R7",
        "description": (
            "Once LAND (terminal) is reached, all restore() calls must be "
            "no-ops. UAV must remain in LAND regardless of flag clearing."
        ),
    },

    # ---- ECT13 — comm_loss during RETURN_HOME with GPS also unavailable (R8 abort) ----
    # R8 second branch: comm_loss arrives during RTH while GPS is also unavailable.
    # The machine first goes RETURN_HOME → LOITER on gps_loss (R5 branch), then
    # comm_loss arriving in LOITER must not escape to NORMAL or re-enter RETURN_HOME.
    # RETURN_HOME is an intentional waypoint here; only the *final* landing in
    # LOITER (with active failures) matters.
    {
        "name": "ECT13_comm_loss_during_rth_gps_unavailable_aborts_to_loiter",
        "steps": [
            ("command_return_home", None),           # NORMAL → RETURN_HOME (intended)
            ("apply_failure", "gps_loss"),           # RETURN_HOME → LOITER (R5 gps branch)
            ("apply_failure", "communication_loss"), # LOITER + comm_loss → stays LOITER (R8)
        ],
        "expected_state": State.LOITER,
        "forbidden": {State.NORMAL},   # must not falsely recover to NORMAL while failures active
        "requirement": "R8",
        "description": (
            "R8 second branch: GPS unavailable when RTH is disrupted. "
            "GPS loss during RTH correctly moves to LOITER (R5); subsequent "
            "comm_loss must not escape LOITER or trigger a false NORMAL transition. "
            "Verifies both branches of R8 are covered and consistent."
        ),
    },
]
