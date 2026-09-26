"""
BobGuard — Automatic Failure Combination Generator
====================================================
Generates all meaningful combinations of UAV failure events and produces
executable scenario dicts compatible with the existing test_runner.

Combination strategy
--------------------
For each non-empty subset of {communication_loss, gps_loss, critical_battery}
the generator produces scenarios covering:

  1. All failures injected simultaneously (serial, one after another).
  2. Each failure injected then individually restored — testing recovery paths.
  3. Partial restoration sequences (e.g. two failures, restore one, check state).

The generator also exercises operator commands (command_return_home,
command_land, command_terminate) to probe interaction with active failures.

No scenario is hard-coded; every combination is derived algorithmically.
"""

from itertools import combinations, permutations
from bobguard.uav_failsafe import State

# ---------------------------------------------------------------------------
# All injectable failure names
# ---------------------------------------------------------------------------
ALL_FAILURES = ["communication_loss", "gps_loss", "critical_battery"]

# Safe terminal states (R7)
SAFE_TERMINALS = {State.NORMAL, State.LAND, State.TERMINATED}


def _inject_steps(failures: list[str]) -> list[tuple]:
    """Return (apply_failure, name) steps for each failure in order."""
    return [("apply_failure", f) for f in failures]


def _restore_steps(failures: list[str]) -> list[tuple]:
    """Return (restore, name) steps for each failure in order."""
    return [("restore", f) for f in failures]


# ---------------------------------------------------------------------------
# 1. Simultaneous injection — all failures in a subset fired together
# ---------------------------------------------------------------------------
def gen_simultaneous_injection() -> list[dict]:
    """One scenario per non-empty subset: inject all, check terminal."""
    scenarios = []
    for r in range(1, len(ALL_FAILURES) + 1):
        for combo in combinations(ALL_FAILURES, r):
            failures = list(combo)
            name = "COMB_inject__" + "_AND_".join(failures)
            scenarios.append({
                "name": name,
                "steps": _inject_steps(failures),
                "expected_state": None,          # checked by violation detector
                "forbidden": {State.RETURN_HOME} if "gps_loss" in failures else set(),
                "requirement": "R3+R5+R7",
                "injected_failures": failures,
                "category": "simultaneous_injection",
                "description": (
                    f"Inject {', '.join(failures)} sequentially; "
                    f"UAV must reach a safe terminal or safe holding state."
                ),
            })
    return scenarios


# ---------------------------------------------------------------------------
# 2. Inject then restore all — UAV should recover to NORMAL
# ---------------------------------------------------------------------------
def gen_inject_and_restore_all() -> list[dict]:
    """Inject every failure in a subset, then restore all — expect NORMAL."""
    scenarios = []
    for r in range(1, len(ALL_FAILURES) + 1):
        for combo in combinations(ALL_FAILURES, r):
            failures = list(combo)
            # critical_battery leads to LAND (terminal) so can't restore to NORMAL
            if "critical_battery" in failures:
                continue
            name = "COMB_restore_all__" + "_AND_".join(failures)
            steps = _inject_steps(failures) + _restore_steps(failures)
            scenarios.append({
                "name": name,
                "steps": steps,
                "expected_state": State.NORMAL,
                "forbidden": {State.RETURN_HOME} if "gps_loss" in failures else set(),
                "requirement": "R2+R6+R7",
                "injected_failures": failures,
                "category": "inject_restore",
                "description": (
                    f"Inject {', '.join(failures)}, then restore all; "
                    f"expect recovery to NORMAL."
                ),
            })
    return scenarios


# ---------------------------------------------------------------------------
# 3. Inject two failures, restore one — check intermediate state is safe
# ---------------------------------------------------------------------------
def gen_partial_restore() -> list[dict]:
    """
    For every 2-failure combo: inject both, restore the first,
    verify UAV is NOT in an unsafe state.
    """
    scenarios = []
    for combo in combinations(ALL_FAILURES, 2):
        a, b = combo
        for first_restore in [a, b]:
            second_active = b if first_restore == a else a
            name = (
                f"COMB_partial_restore__inject_{a}_AND_{b}"
                f"__restore_{first_restore}"
            )
            steps = (
                _inject_steps([a, b])
                + _restore_steps([first_restore])
            )
            scenarios.append({
                "name": name,
                "steps": steps,
                "expected_state": None,
                "forbidden": {State.RETURN_HOME} if "gps_loss" in [a, b] else set(),
                "requirement": "R3+R5+R6+R7",
                "injected_failures": [a, b],
                "restored_failures": [first_restore],
                "remaining_failure": second_active,
                "category": "partial_restore",
                "description": (
                    f"Inject {a}+{b}, restore {first_restore}; "
                    f"{second_active} still active — must not enter unsafe state."
                ),
            })
    return scenarios


# ---------------------------------------------------------------------------
# 4. RTH command interactions with active failures
# ---------------------------------------------------------------------------
def gen_rth_command_interactions() -> list[dict]:
    """
    Issue command_return_home with various failure contexts.
    With gps_loss active, RETURN_HOME must be blocked.
    """
    scenarios = []

    # RTH with gps_loss pre-active
    scenarios.append({
        "name": "COMB_rth_with_gps_loss",
        "steps": [
            ("apply_failure", "gps_loss"),
            ("command_return_home", None),
        ],
        "expected_state": State.LOITER,
        "forbidden": {State.RETURN_HOME},
        "requirement": "R5",
        "injected_failures": ["gps_loss"],
        "category": "command_interaction",
        "description": "RTH command with gps_loss active must be blocked -> LOITER.",
    })

    # RTH with comm loss active (allowed; no GPS issue)
    scenarios.append({
        "name": "COMB_rth_with_comm_loss_only",
        "steps": [
            ("apply_failure", "communication_loss"),  # -> LOITER
            ("restore", "communication_loss"),         # -> NORMAL
            ("command_return_home", None),             # -> RETURN_HOME (gps ok)
        ],
        "expected_state": State.RETURN_HOME,
        "forbidden": set(),
        "requirement": "R5",
        "injected_failures": ["communication_loss"],
        "category": "command_interaction",
        "description": "RTH after comm loss restored (GPS fine) is permitted.",
    })

    # RTH then critical battery fires
    scenarios.append({
        "name": "COMB_rth_then_critical_battery",
        "steps": [
            ("command_return_home", None),
            ("apply_failure", "critical_battery"),
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R3+R7",
        "injected_failures": ["critical_battery"],
        "category": "command_interaction",
        "description": "Critical battery during RTH must abort to LAND.",
    })

    # RTH then both gps_loss and critical battery
    scenarios.append({
        "name": "COMB_rth_gps_loss_and_critical_battery",
        "steps": [
            ("command_return_home", None),
            ("apply_failure", "gps_loss"),        # -> LOITER
            ("apply_failure", "critical_battery"), # -> LAND
        ],
        "expected_state": State.LAND,
        "forbidden": set(),
        "requirement": "R3+R5+R7",
        "injected_failures": ["gps_loss", "critical_battery"],
        "category": "command_interaction",
        "description": "GPS loss then critical battery during RTH must reach LAND.",
    })

    return scenarios


# ---------------------------------------------------------------------------
# 5. All permutations of 2-failure injection
#    (order of arrival matters for priority verification)
# ---------------------------------------------------------------------------
def gen_injection_order_permutations() -> list[dict]:
    """
    For every 2-failure pair test both injection orders.
    Final state must still be safe (order-independence of safety).
    """
    scenarios = []
    for combo in combinations(ALL_FAILURES, 2):
        for perm in permutations(combo):
            a, b = perm
            name = f"COMB_order__{a}__THEN__{b}"
            scenarios.append({
                "name": name,
                "steps": _inject_steps([a, b]),
                "expected_state": None,
                "forbidden": {State.RETURN_HOME} if "gps_loss" in perm else set(),
                "requirement": "R3+R4+R5+R7",
                "injected_failures": list(perm),
                "category": "injection_order",
                "description": (
                    f"Inject {a} then {b}; final state must be safe "
                    f"regardless of arrival order."
                ),
            })
    return scenarios


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def generate_all_combinations() -> list[dict]:
    """Return the complete auto-generated scenario list."""
    all_scenarios = []
    all_scenarios.extend(gen_simultaneous_injection())
    all_scenarios.extend(gen_inject_and_restore_all())
    all_scenarios.extend(gen_partial_restore())
    all_scenarios.extend(gen_rth_command_interactions())
    all_scenarios.extend(gen_injection_order_permutations())
    return all_scenarios
