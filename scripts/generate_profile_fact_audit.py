#!/usr/bin/env python3

from __future__ import annotations

import argparse
from datetime import datetime

from fetch_openai_product_context import SourceResult, check_sources
from generate_ai_dashboard import DashboardData, build_data, format_int, format_tokens_billions


CURRENT_SETUP = (
    ("Codex App", "Default lane via GPT-5.5 for most work; user-confirmed as stable with strong feature velocity."),
    ("Pi", "Clean/raw harness and custom pi-tools work; currently lower-volume than Codex."),
    ("GPT Image", "UI and visual exploration lane when interface direction needs generated assets."),
    ("Cursor Pro", "Active editor-side AI tier and current Claude access path."),
    ("Claude", "Standalone subscription cancelled; historical metrics remain useful but are not active paid usage."),
    ("Opencode Go", "No longer active; old traces are archival footprint only."),
)


def render_source_rows(results: list[SourceResult]) -> list[str]:
    rows = [
        "| Source | Status | Matched facts | Missing facts |",
        "| --- | --- | --- | --- |",
    ]
    for result in results:
        matched = [check.label for check in result.checks if check.matched]
        missing = [check.label for check in result.checks if not check.matched]
        status = "OK" if result.ok else "CHECK"
        if result.error:
            status = "NOT CHECKED" if result.error == "offline mode" else "ERROR"
        rows.append(
            f"| [{result.title}]({result.url}) | {status} | {', '.join(matched) or '-'} | {', '.join(missing) or '-'} |"
        )
    return rows


def render_dashboard_evidence(data: DashboardData | None, error: str | None) -> list[str]:
    if data is None:
        return [
            "## Local Telemetry",
            "",
            f"Local telemetry could not be loaded: `{error or 'unknown error'}`.",
        ]

    return [
        "## Local Telemetry",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
        f"| Codex threads | {format_int(data.codex_threads)} |",
        f"| Codex tokens | {format_tokens_billions(data.codex_tokens)} |",
        f"| Codex working directories | {format_int(data.codex_workdirs)} |",
        f"| Claude history entries | {format_int(data.claude_entries)} |",
        f"| Pi sessions | {format_int(data.pi_sessions)} |",
        f"| Pi message entries | {format_int(data.pi_messages)} |",
        f"| Cursor ACP sessions | {format_int(data.cursor_sessions)} |",
        f"| Cursor AI code hashes | {format_int(data.cursor_code_hashes)} |",
        f"| GitHub contributions | {format_int(data.github_contributions)} |",
        "",
        "Current local readings support Codex as the heavy execution lane, Pi as a smaller custom/raw lane, Cursor as a separate editor-side footprint, and Claude as historical usage evidence.",
    ]


def render_project_evidence(data: DashboardData | None) -> list[str]:
    if data is None:
        return []

    lines = [
        "## Project Evidence",
        "",
        "**Codex top projects**",
        "",
        "| Project | Threads | Tokens |",
        "| --- | ---: | ---: |",
    ]
    for project, threads, tokens_m in data.codex_projects:
        lines.append(f"| {project} | {threads} | {tokens_m:.1f}M |")

    lines.extend(
        [
            "",
            "**Pi top projects**",
            "",
            "| Project | Sessions |",
            "| --- | ---: |",
        ]
    )
    for project, sessions in data.pi_projects_top:
        lines.append(f"| {project} | {sessions} |")

    lines.extend(
        [
            "",
            "**Cursor top workdirs**",
            "",
            "| Workdir | ACP Sessions |",
            "| --- | ---: |",
        ]
    )
    for workdir, sessions in data.cursor_projects_top:
        lines.append(f"| {workdir} | {sessions} |")

    lines.extend(
        [
            "",
            "Cursor ACP metadata remains a footprint signal, not a reliable source for project priority.",
        ]
    )
    return lines


def render_markdown(data: DashboardData | None, error: str | None, product_results: list[SourceResult]) -> str:
    product_note = (
        "Official OpenAI sources support mentioning current Codex App feature momentum and GPT Image model context. They do not prove personal usage volume; local telemetry and user-confirmed setup do that."
        if all(result.ok for result in product_results)
        else "Official OpenAI sources were not fully verified in this run. Re-run without `--offline` before changing public product-context claims."
    )

    lines = [
        "# Profile Fact Audit",
        "",
        f"Generated on `{datetime.now().strftime('%Y-%m-%d')}`.",
        "",
        "## Current Setup",
        "",
        "| Tool | Current role |",
        "| --- | --- |",
    ]
    for tool, role in CURRENT_SETUP:
        lines.append(f"| {tool} | {role} |")

    lines.extend(["", *render_dashboard_evidence(data, error), "", *render_project_evidence(data)])

    lines.extend(
        [
            "",
            "## Official Product Context",
            "",
            *render_source_rows(product_results),
            "",
            product_note,
            "",
            "## Claim Boundaries",
            "",
            "- Codex App can be described as the default lane because both local usage and user-confirmed workflow support it.",
            "- Pi should be described as raw/custom and lower-volume, not as the main lane.",
            "- GPT Image can be described as the UI/visual lane; model names should be checked against OpenAI docs before publishing.",
            "- Cursor Pro can be described as active editor-side AI and the current Claude access path.",
            "- Claude metrics should be labeled historical because the standalone subscription is cancelled.",
            "- Opencode Go should be labeled historical footprint only.",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="edhor1608")
    parser.add_argument("--months", type=int, default=7)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout", type=int, default=15)
    args = parser.parse_args()

    data = None
    error = None
    try:
        data = build_data(args.user, args.months)
    except Exception as exc:
        error = str(exc)

    product_results = check_sources(timeout=args.timeout, offline=args.offline)
    print(render_markdown(data, error, product_results))


if __name__ == "__main__":
    main()
