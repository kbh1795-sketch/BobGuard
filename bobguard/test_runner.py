"""
BobGuard — Test Runner
=======================
Executes all scenarios against the UAV state machine and reports results.
"""

import sys
from bobguard.uav_failsafe import UAVStateMachine, State
from bobguard.scenarios import SCENARIOS


def run_scenario(scenario: dict) -> dict:
    """Run a single scenario; return a result dict."""
    sm = UAVStateMachine()
    visited: list[State] = []  # only post-step states; initial state excluded

    for method_name, arg in scenario["steps"]:
        method = getattr(sm, method_name)
        if arg is not None:
            method(arg)
        else:
            method()
        visited.append(sm.state)

    # Check expected final state
    final_ok = sm.state == scenario["expected_state"]

    # Check forbidden states never visited (initial NORMAL start is not counted)
    forbidden_visited = [s for s in scenario["forbidden"] if s in visited]
    forbidden_ok = len(forbidden_visited) == 0

    passed = final_ok and forbidden_ok

    return {
        "name": scenario["name"],
        "requirement": scenario["requirement"],
        "passed": passed,
        "final_state": sm.state,
        "expected_state": scenario["expected_state"],
        "forbidden_visited": forbidden_visited,
        "history": sm.history,
        "visited_states": visited,
    }


def run_all(scenarios=None, label="") -> list[dict]:
    if scenarios is None:
        scenarios = SCENARIOS

    results = []
    header = f"=== BobGuard Test Run {label} ==="
    print(header)
    print("=" * len(header))

    for scenario in scenarios:
        result = run_scenario(scenario)
        results.append(result)
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"  [{status}] {result['name']} "
            f"(req={result['requirement']}) "
            f"final={result['final_state'].value} "
            f"expected={result['expected_state'].value}"
        )
        if not result["passed"]:
            if result["final_state"] != result["expected_state"]:
                print(
                    f"         -> final state mismatch: "
                    f"got {result['final_state'].value}, "
                    f"expected {result['expected_state'].value}"
                )
            if result["forbidden_visited"]:
                print(
                    f"         -> forbidden states visited: "
                    f"{[s.value for s in result['forbidden_visited']]}"
                )
            print(f"         -> history: {result['history']}")

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print()
    print(f"  Result: {passed}/{total} passed  ({100*passed//total}%)")
    print()
    return results


if __name__ == "__main__":
    results = run_all(label="(initial)")
    any_fail = any(not r["passed"] for r in results)
    sys.exit(1 if any_fail else 0)
