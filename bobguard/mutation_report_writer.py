"""
BobGuard — Mutation Report Writer
===================================
Writes bobguard_mutation_report.md from a list of MutationResult objects.
"""

from bobguard.mutation_runner import MutationResult


def write_mutation_report(
    results: list[MutationResult],
    original_passed: int,
    original_total: int,
    output_path: str = "bobguard_mutation_report.md",
) -> None:
    detected = sum(1 for r in results if r.detected)
    total = len(results)
    rate = int(100 * detected / total) if total else 0

    lines: list[str] = []

    # ---- Header ----
    lines += [
        "# BobGuard — Mutation Testing Report",
        "",
        "> **Built with IBM Bob** — Agentic UAV Failsafe Verification System  ",
        "> Mutation testing validates that BobGuard actively detects previously",
        "> unseen defects, not just a passing implementation.",
        "",
        "---",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Injected mutations | {total} |",
        f"| Detected mutations | {detected} |",
        f"| Missed mutations | {total - detected} |",
        f"| Mutation Detection Rate | **{rate}%** |",
        f"| Original suite (post-mutation) | {original_passed}/{original_total} PASS |",
        "",
        "---",
        "",
    ]

    # ---- Summary table ----
    lines += [
        "## Mutation Detection Table",
        "",
        "| Mutation | Bug Description | Detected? | "
        "Triggering Scenario | Violation | Severity |",
        "|----------|----------------|-----------|"
        "--------------------|-----------|----------|",
    ]

    for r in results:
        m = r.mutation
        detected_str = "**YES**" if r.detected else "**NO**"
        if r.first_exposure:
            ex = r.first_exposure
            scen  = f"`{ex.scenario_name}`"
            viols = ", ".join(ex.violation_types) or "—"
            sevs  = ", ".join(sorted(ex.severities)) or "—"
        else:
            scen = "—"
            viols = "—"
            sevs  = "—"
        lines.append(
            f"| **{m.id}** — {m.name} | {m.description[:60]}… | "
            f"{detected_str} | {scen} | {viols} | {sevs} |"
        )

    lines += ["", "---", ""]

    # ---- Per-mutation detail ----
    lines += ["## Detailed Mutation Results", ""]

    for r in results:
        m = r.mutation
        status = "DETECTED" if r.detected else "MISSED"
        badge  = "DETECTED" if r.detected else "MISSED"

        lines += [
            f"### {m.id} — {m.name}  `[{badge}]`",
            "",
            f"| Field | Detail |",
            f"|-------|--------|",
            f"| Mutation ID | `{m.id}` |",
            f"| Status | **{status}** |",
            f"| Requirement violated | {m.requirement_violated} |",
            f"| Patched method | `UAVStateMachine.{m.patch_target}()` |",
            f"| Expected violations | {', '.join(m.expected_violations)} |",
            f"| Expected severities | {', '.join(m.expected_severities)} |",
            "",
            f"**Bug description:**  ",
            f"{m.description}",
            "",
        ]

        if r.first_exposure:
            ex = r.first_exposure
            lines += [
                f"**First triggering scenario:** `{ex.scenario_name}`",
                "",
                "**State Transition Trace:**",
                "",
                "```",
                ex.state_trace,
                "```",
                "",
                f"**Violations detected:** {', '.join(ex.violation_types)}  ",
                f"**Severities:** {', '.join(sorted(ex.severities))}  ",
                f"**Final state:** `{ex.final_state.value}`",
                "",
            ]
            if len(r.exposures) > 1:
                lines += [
                    f"**Additional triggering scenarios** ({len(r.exposures) - 1} more):",
                    "",
                ]
                for ex2 in r.exposures[1:6]:   # show up to 5 extras
                    lines.append(
                        f"- `{ex2.scenario_name}` — "
                        f"violations: {', '.join(ex2.violation_types)}"
                    )
                lines.append("")
        else:
            lines += [
                "> **WARNING:** This mutation was NOT detected by BobGuard.",
                "> The verification suite requires enhancement to catch this defect.",
                "",
            ]

        lines += ["---", ""]

    # ---- Post-mutation original verification ----
    orig_status = "PASS" if original_passed == original_total else "FAIL"
    lines += [
        "## Original Implementation Verification (Post-Mutation)",
        "",
        "After all mutations were tested, the original unmodified implementation",
        "was run through the full scenario suite to confirm zero regressions.",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Scenarios run | {original_total} |",
        f"| Passed | {original_passed} |",
        f"| Failed | {original_total - original_passed} |",
        f"| Status | **{orig_status}** |",
        "",
        "---",
        "",
    ]

    # ---- Interpretation ----
    lines += [
        "## Interpretation",
        "",
        "A **100% Mutation Detection Rate** means BobGuard does not merely",
        "pass a correct implementation — it actively discovers every class of",
        "realistic UAV failsafe defect injected by the mutation suite.",
        "",
        "Each detected mutation corresponds to a real-world failure mode:",
        "",
        "| Mutation | Real-World Risk |",
        "|----------|-----------------|",
        "| M1 | UAV loiters until battery exhaustion → uncontrolled crash |",
        "| M2 | Autonomous navigation without GPS → loss of vehicle / collision |",
        "| M3 | UAV resumes flight with no ground link → unrecoverable loss |",
        "| M4 | Stuck in unsafe navigation state → collision or out-of-bounds |",
        "| M5 | Silent battery drain in normal flight → crash without warning |",
        "",
        "---",
        "",
        "*Generated by IBM Bob — BobGuard Mutation Testing Workflow*",
    ]

    content = "\n".join(lines)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(content)

    print(f"  [report] Written to {output_path}")
