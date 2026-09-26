"""
BobGuard — Failure Scenarios
==============================
Defines structured test scenarios that exercise UAV failsafe logic.
Each scenario is a sequence of (action, arg) steps plus expected final state
and a set of states that must NOT be visited.
"""

from bobguard.uav_failsafe import State

# ---------------------------------------------------------------------------
# Scenario format:
#   name          : human-readable label
#   steps         : list of (method_name, argument_or_None)
#   expected_state: State the machine must be in after all steps
#   forbidden     : set of States that must never appear in history
#   requirement   : safety requirement tag being validated
# ---------------------------------------------------------------------------

SCENARIOS = [
    # ---- R1: Communication loss → LOITER ----
    {
        "name": "R1_comm_loss_transitions_to_loiter",
        "steps": [
            ("apply_failure", "communication_loss"),
        ],
        "expected_state": State.LOITER,
        "forbidden": set(),
        "requirement": "R1",
    },

    # ---- R2: Communication restored, battery safe → back to NORMAL ----
    {
        "name": "R2_comm_restored_returns_to_normal",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("restore", "communication_loss"),
        ],
        "expected_state": State.NORMAL,
        "forbidden": set(),
        "requirement": "R2",
    },

    # ---- R3: Critical battery eventually leads to LAND ----
    {
        "name": "R3_critical_battery_leads_to_land",
        "steps": [
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R3",
    },

    # ---- R4: Critical battery has higher priority than LOITER ----
    # UAV in LOITER (due to comm loss) then battery becomes critical.
    # Should go to LAND, not stay in LOITER.
    {
        "name": "R4_critical_battery_overrides_loiter",
        "steps": [
            ("apply_failure", "communication_loss"),   # → LOITER
            ("apply_failure", "critical_battery"),     # → must go to LAND
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R4",
    },

    # ---- R4b: Critical battery from NORMAL with comm_loss active ----
    # Both failures arrive simultaneously (comm first, then battery).
    # Battery priority must win — end state LAND.
    {
        "name": "R4b_comm_loss_then_critical_battery_lands",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R4",
    },

    # ---- R5: GPS loss prevents RETURN_HOME ----
    {
        "name": "R5_gps_loss_blocks_return_home",
        "steps": [
            ("apply_failure", "gps_loss"),
            ("command_return_home", None),
        ],
        "expected_state": State.LOITER,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R5",
    },

    # ---- R5b: GPS loss while already in RETURN_HOME ----
    {
        "name": "R5b_gps_loss_during_return_home",
        "steps": [
            ("command_return_home", None),
            ("apply_failure", "gps_loss"),
        ],
        "expected_state": State.LOITER,
        "forbidden": set(),
        "requirement": "R5",
    },

    # ---- R6: comm_loss + gps_loss must NOT leave UAV stuck in LOITER ----
    # After both failures are restored the UAV should reach NORMAL.
    {
        "name": "R6_comm_and_gps_loss_not_stuck_in_loiter",
        "steps": [
            ("apply_failure", "communication_loss"),  # → LOITER
            ("apply_failure", "gps_loss"),
            ("restore", "communication_loss"),
            ("restore", "gps_loss"),
        ],
        "expected_state": State.NORMAL,
        "forbidden": set(),
        "requirement": "R6",
    },

    # ---- R7: Every failure scenario reaches a safe terminal ----
    # worst-case: all three failures fire, comms+gps never restore.
    # Battery critical → must land.
    {
        "name": "R7_all_failures_reach_safe_terminal",
        "steps": [
            ("apply_failure", "communication_loss"),
            ("apply_failure", "gps_loss"),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R7",
    },

    # ---- R7b: Return-home with critical battery must land ----
    {
        "name": "R7b_return_home_critical_battery_must_land",
        "steps": [
            ("command_return_home", None),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R7",
    },
]
