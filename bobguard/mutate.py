"""
BobGuard — Mutation Testing Entry Point
========================================
Usage:
    python -m bobguard.mutate

Workflow:
  1. Run all 5 mutations against the full scenario pool
  2. Write bobguard_mutation_report.md
  3. Verify the original implementation still passes everything
  4. Print final summary
"""

import sys
from bobguard.mutation_runner import (
    run_all_mutations,
    verify_original_unmodified,
    _all_scenarios,
)
from bobguard.mutation_report_writer import write_mutation_report


def main() -> int:
    scenarios = _all_scenarios()

    # --- Phase 1: Run mutations ---
    results = run_all_mutations(scenarios)

    # --- Phase 2: Write report ---
    orig_passed, orig_total = verify_original_unmodified(scenarios)
    write_mutation_report(
        results,
        original_passed=orig_passed,
        original_total=orig_total,
        output_path="bobguard_mutation_report.md",
    )

    # --- Phase 3: Final summary ---
    detected = sum(1 for r in results if r.detected)
    total = len(results)
    rate = int(100 * detected / total) if total else 0

    print()
    print("=" * 45)
    print("  BobGuard Mutation Testing — Final Results")
    print("=" * 45)
    print(f"  Injected mutations:      {total}")
    print(f"  Detected mutations:      {detected}")
    print(f"  Missed mutations:        {total - detected}")
    print(f"  Mutation Detection Rate: {rate}%")
    print()
    print(f"  Original suite (post):   {orig_passed}/{orig_total} scenarios PASS")
    print("=" * 45)
    print()

    # Fail if any mutation was missed or original suite regressed
    if detected < total:
        print("  RESULT: INCOMPLETE — some mutations were not detected.")
        return 1
    if orig_passed < orig_total:
        print("  RESULT: REGRESSION — original suite failed after mutation testing.")
        return 1

    print("  RESULT: ALL MUTATIONS DETECTED. ORIGINAL SUITE INTACT.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
