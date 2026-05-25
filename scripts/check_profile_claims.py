#!/usr/bin/env python3

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ClaimCheck:
    label: str
    pattern: str
    reason: str


REQUIRED = (
    ClaimCheck("vivenu-current-role", r"Software engineer at \[vivenu\]\(https://vivenu\.com\)", "The profile should identify the current vivenu SWE role near the top."),
    ClaimCheck("catch-hook", r"## Now.*not that I use AI; it is that I track where it changes the shape of the work", "The profile should open with a real hook, not a generic start table."),
    ClaimCheck("current-work", r"## Current Work", "The profile should show current work before deep telemetry."),
    ClaimCheck("active-private-builder", r"private projects|private systems|public and private repos|private product", "The profile should show private/public builder activity."),
    ClaimCheck("project-links", r"https://github\.com/edhor1608/pi-tools.*https://github\.com/edhor1608/qwer-q.*https://github\.com/edhor1608/passepartout", "The profile should link important public projects and sites."),
    ClaimCheck("systems-overview", r"## How I Build", "The profile should include an overview of technologies and workflow."),
    ClaimCheck("codex-app-default", r"Codex App.*default lane|Using the Codex App for most work", "Codex App should be the default lane."),
    ClaimCheck("codex-why", r"stable, long-running|long-running coding work|feature velocity", "The profile should explain why Codex is the default."),
    ClaimCheck("pi-raw-custom", r"Pi.*clean/raw|Pi.*raw/custom|cleaner/rawer harness", "Pi should be framed as raw/custom tooling."),
    ClaimCheck("gpt-image-ui", r"GPT Image.*UI|UI-heavy work.*GPT Image", "GPT Image should cover UI/visual work."),
    ClaimCheck("latest-gpt-image", r"gpt-image-2", "The current GPT Image model context should be present."),
    ClaimCheck("cursor-pro", r"Cursor Pro", "Cursor Pro should be active editor-side AI."),
    ClaimCheck("claude-through-cursor", r"Claude.*Cursor|Cursor.*Claude", "Current Claude access should go through Cursor."),
    ClaimCheck("claude-historical", r"Claude.*historical|historical.*Claude", "Standalone Claude should be historical."),
    ClaimCheck("opencode-not-active", r"Opencode Go.*historical|historical.*Opencode Go", "Opencode Go should not be active."),
    ClaimCheck("activity-counters", r"952.*Codex|17\.\d+B|2,399.*contributions", "The profile should show activity counters."),
    ClaimCheck("dashboard", r"## AI Snapshot", "The profile should include the AI/GitHub dashboard."),
    ClaimCheck("history", r"2026-05.*2026-04.*2026-03", "The profile should show history or trends, not just current totals."),
    ClaimCheck("markdown-visuals", r"!\[.*?\]\(https://img\.shields\.io|<table>|<details>", "The profile should include useful Markdown visual affordances."),
    ClaimCheck("connect-links", r"## Connect", "The profile should include public connection links."),
    ClaimCheck("linkedin-link", r"https://www\.linkedin\.com/in/jonas-rohde/", "The profile should link the public LinkedIn profile."),
)

BANNED = (
    ClaimCheck("claude-code-badge", r"Claude_Code", "Top badge should not imply standalone Claude Code is active."),
    ClaimCheck("old-claude-model", r"Opus 4\.6", "Old Claude setup should not be current profile copy."),
    ClaimCheck("old-codex-default", r"Codex.*GPT-5\.4.*default|GPT-5\.4.*Codex.*default", "Codex default should not drift back to GPT-5.4."),
    ClaimCheck("opencode-active-default", r"Opencode Go[^\n]*(active default|default lane)|(active default|default lane)[^\n]*Opencode Go", "Opencode Go should not be presented as active."),
)


def check_required(text: str) -> list[ClaimCheck]:
    return [check for check in REQUIRED if not re.search(check.pattern, text, flags=re.I | re.S)]


def check_banned(text: str) -> list[ClaimCheck]:
    return [check for check in BANNED if re.search(check.pattern, text, flags=re.I | re.S)]


def render_results(missing: list[ClaimCheck], stale: list[ClaimCheck]) -> str:
    lines = ["# Profile Claim Check", ""]
    if not missing and not stale:
        lines.append("OK: all required current-workflow claims are present and no stale claims were found.")
        return "\n".join(lines)

    if missing:
        lines.extend(["Missing required claims:", ""])
        for check in missing:
            lines.append(f"- `{check.label}`: {check.reason}")
        lines.append("")

    if stale:
        lines.extend(["Stale or banned claims:", ""])
        for check in stale:
            lines.append(f"- `{check.label}`: {check.reason}")

    return "\n".join(lines).rstrip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("readme", nargs="?", default="README.md")
    args = parser.parse_args()

    text = Path(args.readme).read_text()
    missing = check_required(text)
    stale = check_banned(text)
    print(render_results(missing, stale))
    if missing or stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
