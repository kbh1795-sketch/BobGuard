"""
BobGuard — Verification Report Generator
==========================================
Consumes a list of VerificationResult objects produced by the automated
runner and writes bobguard_verification_report.md.
"""

from dataclasses import dataclass, field
from typing import Optional
from bobguard.uav_failsafe import State
from bobguard.violation_detector import ViolationReport


@dataclass
class VerificationResult:
    """One entry per scenario in the final report."""
    scenario_name: str
    category: str
    description: str
    injected_failures: list[str]
    state_trace: str           # rendered multi-line trace string
    final_state: State
    expected_state: Optional[State]
    passed: bool
    violations: list[ViolationReport]
    overall_severity: str      # NONE | LOW | MEDIUM | HIGH | CRITICAL
    requirement: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SEV_EMOJI = {
    "NONE":     "OK",
    "LOW":      "LOW",
    "MEDIUM":   "MED",
    "HIGH":     "HIGH",
    "CRITICAL": "CRIT",
}

_PASS_MARK = {True: "PASS", False: "FAIL"}


def _toc_anchor(name: str) -> str:
    """Convert a scenario name to a markdown anchor slug."""
    return name.lower().replace(" ", "-").replace("_", "-").replace("/", "")


# ---------------------------------------------------------------------------
# Main writer
# ---------------------------------------------------------------------------

def write_report(
    results: list[VerificationResult],
    output_path: str = "bobguard_verification_report.md",
) -> None:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed

    crit_count = sum(1 for r in results if r.overall_severity == "CRITICAL")
    high_count = sum(1 for r in results if r.overall_severity == "HIGH")
    med_count  = sum(1 for r in results if r.overall_severity == "MEDIUM")
    # LOW severity includes LOITER_ACTIVE_FAILURE operational diagnostics —
    # counted separately so the summary distinguishes them from true defects.
    low_count  = sum(1 for r in results if r.overall_severity == "LOW")
    op_diag_count = sum(
        1 for r in results
        for v in r.violations if v.violation_type == "LOITER_ACTIVE_FAILURE"
    )

    safe_terminal_states = {State.NORMAL, State.LAND, State.TERMINATED}
    safe_coverage = sum(
        1 for r in results if r.final_state in safe_terminal_states
    )
    safe_pct = int(100 * safe_coverage / total) if total else 0

    # Group by category
    categories: dict[str, list[VerificationResult]] = {}
    for r in results:
        categories.setdefault(r.category, []).append(r)

    lines: list[str] = []

    # ---- Title & summary ----
    lines += [
        "# BobGuard — Automated Failsafe Verification Report",
        "",
        "> **Built with IBM Bob** — Agentic UAV Failsafe Verification System  ",
        "> Software-only state-machine simulator. No real UAV is controlled.",
        "",
        "---",
        "",
        "## Verification Methodology",
        "",
        "**PASS** means the scenario's final state matches the requirement defined for it "
        "and no safety violation was detected. A PASS on a scenario that ends in LOITER "
        "means LOITER is the *explicitly required* outcome for that failure condition.",
        "",
        "**Operational diagnostics** (`LOITER_ACTIVE_FAILURE`) are informational notes "
        "generated when the UAV ends in LOITER while active failure flags remain. "
        "LOITER is the *intended contingency state* in those conditions (R1, R5, R8); "
        "these diagnostics are **not safety violations** and are not counted as HIGH/CRITICAL.",
        "",
        "**Undefined policy** means the scenario exercises a situation for which no "
        "explicit requirement exists. The outcome is noted but is not classified as a "
        "defect unless a defined requirement is demonstrably breached.",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total scenarios tested | {total} |",
        f"| Passed (requirement-compliant) | {passed} |",
        f"| Failed (requirement violated) | {failed} |",
        f"| Critical violations | {crit_count} |",
        f"| High violations | {high_count} |",
        f"| Medium violations | {med_count} |",
        f"| Low violations (incl. operational diagnostics) | {low_count} |",
        f"| &nbsp;&nbsp; of which: expected LOITER diagnostics | {op_diag_count} |",
        f"| Safe-state coverage | {safe_pct}% ({safe_coverage}/{total}) |",
        "",
        "---",
        "",
    ]

    # ---- Category index ----
    lines += ["## Scenario Categories", ""]
    for cat, cat_results in categories.items():
        cat_passed = sum(1 for r in cat_results if r.passed)
        lines.append(
            f"- **{cat}** — {len(cat_results)} scenarios, "
            f"{cat_passed} passed, {len(cat_results)-cat_passed} failed"
        )
    lines += ["", "---", ""]

    # ---- Per-scenario detail (grouped by category) ----
    lines += ["## Detailed Results", ""]
    for cat, cat_results in categories.items():
        lines += [f"### {cat}", ""]
        for r in cat_results:
            status = _PASS_MARK[r.passed]
            sev    = r.overall_severity
            lines += [
                f"#### `{r.scenario_name}`",
                "",
                f"| Field | Value |",
                f"|-------|-------|",
                f"| Result | **{status}** |",
                f"| Requirement | {r.requirement} |",
                f"| Category | {r.category} |",
                f"| Injected failures | {', '.join(r.injected_failures) or 'none'} |",
                f"| Final state | `{r.final_state.value}` |",
                f"| Expected state | `{r.expected_state.value if r.expected_state else 'any-safe'}` |",
                f"| Severity | **{sev}** |",
                "",
                f"**Description:** {r.description}",
                "",
                "**State Transition Trace:**",
                "",
                "```",
                r.state_trace,
                "```",
                "",
            ]
            if r.violations:
                lines += ["**Violations Detected:**", ""]
                for v in r.violations:
                    lines += [
                        f"- **[{v.severity}] {v.violation_type}**  ",
                        f"  {v.description}  ",
                        f"  *Fix:* {v.recommended_fix}  ",
                        f"  *Evidence:* `{v.evidence}`",
                        "",
                    ]
            else:
                lines += ["**Violations:** none", ""]
            lines += ["---", ""]

    # ---- Violations-only index ----
    failing = [r for r in results if not r.passed or r.violations]
    if failing:
        lines += ["## Violation Index", ""]
        lines += [
            "| Scenario | Severity | Violation | Recommended Fix |",
            "|----------|----------|-----------|-----------------|",
        ]
        for r in failing:
            for v in r.violations:
                fix_short = v.recommended_fix[:80] + ("..." if len(v.recommended_fix) > 80 else "")
                lines.append(
                    f"| `{r.scenario_name}` | **{v.severity}** | "
                    f"{v.violation_type} | {fix_short} |"
                )
        lines += ["", "---", ""]

    # ---- Footer ----
    lines += [
        "",
        "---",
        "",
        "*Generated by IBM Bob — BobGuard Automated Verification Workflow*",
    ]

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(content)

    print(f"  [report] Written to {output_path}")
