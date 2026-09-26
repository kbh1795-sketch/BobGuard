"""
BobGuard — Full Test Suite Entry Point
========================================
Runs original scenarios + regression scenarios and reports combined results.
"""

import sys
from bobguard.test_runner import run_all
from bobguard.scenarios import SCENARIOS
from bobguard.regression_scenarios import REGRESSION_SCENARIOS

if __name__ == "__main__":
    print("=" * 50)
    print("  BobGuard — Full Test Suite")
    print("=" * 50)
    print()

    original_results = run_all(SCENARIOS, label="[Original Scenarios]")
    regression_results = run_all(REGRESSION_SCENARIOS, label="[Regression Scenarios]")

    all_results = original_results + regression_results
    passed = sum(1 for r in all_results if r["passed"])
    total = len(all_results)

    print("=" * 50)
    print(f"  TOTAL: {passed}/{total} passed  ({100*passed//total}%)")
    print("=" * 50)

    any_fail = any(not r["passed"] for r in all_results)
    sys.exit(1 if any_fail else 0)
