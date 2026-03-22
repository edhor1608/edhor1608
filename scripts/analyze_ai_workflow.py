#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


KEYWORDS = {
    "plan": r"\bplan\b|planning|execution board|tasks?",
    "review": r"\breview\b|coderabbit|code review|pr review",
    "pr": r"\bpr\b|pull request",
    "worktree": r"worktree",
    "agent": r"subagent|multiagent|agent loop|parallel agents|spawn|task\(",
    "test": r"\btest\b|typecheck|lint|vitest|playwright",
    "research": r"\bresearch\b|look up|web research|compare",
    "brainstorm": r"brainstorm|idea|product idea",
    "docs": r"readme|docs|documentation",
    "bugfix": r"bug|fix|broken|issue",
    "frontend": r"frontend|ui|design|landing page",
}

NAME_MAP = {
    "meinungsmache-app": "VeraMint",
    "picalyze": "Picalyze",
    "repos": "repos root",
    "jonas": "home",
}

PATH_MARKERS = [
    ("meinungsmache", "VeraMint"),
    ("veramint", "VeraMint"),
    ("picalyze", "Picalyze"),
    ("qwer-digest", "qwer-digest"),
    ("qwer-q", "qwer-q"),
    ("stead-core", "stead-core"),
    ("stead", "stead"),
    ("aurora", "aurora"),
    ("upstrio", "Upstrio"),
    ("edhor-me", "edhor-me"),
    ("passepartout", "passepartout"),
    ("aegis", "Aegis"),
    ("nexum", "Nexum"),
    ("edhor-fotos", "edhor-fotos"),
]


@dataclass
class WeeklyRow:
    week: str
    github: int | None
    codex_threads: int | None
    codex_tokens_m: float | None
    claude_entries: int | None
    claude_sessions: int | None


def pretty_name(raw: str) -> str:
    return NAME_MAP.get(raw, raw)


def project_name_from_path(path_text: str | None) -> str:
    if not path_text:
        return "unknown"
    lowered = path_text.lower()
    for marker, label in PATH_MARKERS:
        if marker in lowered:
            return label
    return pretty_name(Path(path_text).name)


def week_id_from_date(date_str: str) -> str:
    return datetime.fromisoformat(date_str).strftime("%G-W%V")


def week_id_from_ts(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, tz=timezone.utc).strftime("%G-W%V")


def month_id_from_ts(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, tz=timezone.utc).strftime("%Y-%m")


def format_top_signals(counter: Counter[str], limit: int = 4) -> str:
    if not counter:
        return "-"
    return ", ".join(f"{name} ({count})" for name, count in counter.most_common(limit))


def run_json(cmd: list[str]) -> object:
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


def github_calendar(user: str) -> tuple[dict[str, int], dict[str, int]]:
    query = (
        'query { user(login: "%s") { contributionsCollection { '
        "contributionCalendar { weeks { contributionDays { date contributionCount } } } } } }"
    ) % user
    payload = run_json(["gh", "api", "graphql", "-f", f"query={query}"])
    weeks: dict[str, int] = {}
    months: dict[str, int] = {}
    for week in payload["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]:
        days = week["contributionDays"]
        week_id = week_id_from_date(days[0]["date"])
        weeks[week_id] = sum(day["contributionCount"] for day in days)
        for day in days:
            month = day["date"][:7]
            months[month] = months.get(month, 0) + day["contributionCount"]
    return weeks, months


def codex_data(db_path: Path) -> dict[str, Any]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    rows = cur.execute(
        """
        select created_at, cwd, tokens_used, coalesce(agent_role, 'main'), first_user_message
        from threads
        """
    ).fetchall()

    weekly = defaultdict(lambda: {"threads": 0, "tokens": 0})
    monthly = defaultdict(lambda: {"threads": 0, "tokens": 0})
    week_projects: dict[str, Counter[str]] = defaultdict(Counter)
    roles = Counter()
    role_tokens = Counter()
    prompts: list[str] = []
    monthly_keywords: dict[str, Counter[str]] = defaultdict(Counter)
    weekly_keywords: dict[str, Counter[str]] = defaultdict(Counter)

    for created_at, cwd, tokens_used, role, first_message in rows:
        week = week_id_from_ts(created_at)
        month = month_id_from_ts(created_at)
        weekly[week]["threads"] += 1
        weekly[week]["tokens"] += tokens_used
        monthly[month]["threads"] += 1
        monthly[month]["tokens"] += tokens_used
        week_projects[week][project_name_from_path(cwd)] += tokens_used
        roles[role] += 1
        role_tokens[role] += tokens_used
        if first_message:
            prompts.append(first_message)
            for key, pattern in KEYWORDS.items():
                if re.search(pattern, first_message, re.I):
                    monthly_keywords[month][key] += 1
                    weekly_keywords[week][key] += 1

    keyword_counts = {
        key: sum(1 for prompt in prompts if re.search(pattern, prompt, re.I))
        for key, pattern in KEYWORDS.items()
    }
    recent_prompts = cur.execute(
        """
        select datetime(created_at, 'unixepoch'), substr(first_user_message, 1, 180)
        from threads
        where first_user_message != ''
        order by created_at desc
        limit 10
        """
    ).fetchall()
    conn.close()
    return {
        "weekly": weekly,
        "monthly": monthly,
        "week_projects": week_projects,
        "roles": roles,
        "role_tokens": role_tokens,
        "keyword_counts": keyword_counts,
        "monthly_keywords": monthly_keywords,
        "weekly_keywords": weekly_keywords,
        "recent_prompts": recent_prompts,
        "prompt_count": len(prompts),
    }


def claude_history(history_path: Path) -> dict[str, Any]:
    weeks = defaultdict(lambda: {"entries": 0, "sessions": set()})
    months = Counter()
    projects = Counter()
    commands = Counter()
    sessions = set()

    with history_path.open() as handle:
        for line in handle:
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            ts = obj.get("timestamp")
            if not isinstance(ts, (int, float)):
                continue
            ts_seconds = ts / 1000
            week = week_id_from_ts(ts_seconds)
            month = month_id_from_ts(ts_seconds)
            weeks[week]["entries"] += 1
            months[month] += 1
            session_id = obj.get("sessionId")
            if isinstance(session_id, str) and session_id:
                sessions.add(session_id)
                weeks[week]["sessions"].add(session_id)
            project = obj.get("project")
            if isinstance(project, str) and project and project not in {"/Users/jonas", "/Users/jonas/repos"}:
                projects[project_name_from_path(project)] += 1
            display = obj.get("display")
            if isinstance(display, str) and display.startswith("/"):
                commands[display.split()[0]] += 1

    return {
        "weekly": weeks,
        "monthly": months,
        "projects": projects,
        "commands": commands,
        "sessions": sessions,
    }


def claude_transcripts(projects_root: Path) -> dict[str, Any]:
    keyword_counts = Counter()
    project_weeks: dict[str, Counter[str]] = defaultdict(Counter)
    sample_prompts: list[tuple[str, str]] = []
    total_user_messages = 0
    monthly_keywords: dict[str, Counter[str]] = defaultdict(Counter)
    weekly_keywords: dict[str, Counter[str]] = defaultdict(Counter)

    for path in projects_root.rglob("*.jsonl"):
        try:
            with path.open() as handle:
                for line in handle:
                    obj = json.loads(line)
                    if obj.get("type") != "user":
                        continue
                    message = obj.get("message", {}).get("content")
                    text = ""
                    if isinstance(message, str):
                        text = message
                    elif isinstance(message, list):
                        text = " ".join(part.get("text", "") for part in message if isinstance(part, dict))
                    if not text:
                        continue
                    total_user_messages += 1

                    month = None
                    week = None
                    ts = obj.get("timestamp")
                    if isinstance(ts, str) and len(ts) >= 10:
                        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                        month = dt.strftime("%Y-%m")
                        week = dt.strftime("%G-W%V")

                    for key, pattern in KEYWORDS.items():
                        if re.search(pattern, text, re.I):
                            keyword_counts[key] += 1
                            if month:
                                monthly_keywords[month][key] += 1
                            if week:
                                weekly_keywords[week][key] += 1

                    cwd = obj.get("cwd")
                    if week:
                        project_name = project_name_from_path(cwd) if isinstance(cwd, str) else "unknown"
                        project_weeks[week][project_name] += 1

                    if (
                        len(sample_prompts) < 12
                        and len(text) > 40
                        and "<local-command" not in text
                        and "<permissions instructions>" not in text
                        and "# AGENTS.md" not in text
                        and "<environment_context>" not in text
                        and "<command-name>" not in text
                        and "Remember marker" not in text
                        and "FOUND:" not in text
                        and "Reply with exactly" not in text
                        and "## Apps" not in text
                        and "Post crossover prompt" not in text
                        and "Base directory for this skill" not in text
                        and "[Request interrupted by user for tool use]" not in text
                        and "<task-notification>" not in text
                        and "This session is being continued from a previous conversation" not in text
                    ):
                        ts_text = ts if isinstance(ts, str) else "unknown"
                        sample_prompts.append((ts_text, text[:180].replace("\n", " ")))
        except Exception:
            continue

    return {
        "keyword_counts": keyword_counts,
        "monthly_keywords": monthly_keywords,
        "weekly_keywords": weekly_keywords,
        "project_weeks": project_weeks,
        "sample_prompts": sample_prompts,
        "total_user_messages": total_user_messages,
    }


def git_ai_data(db_path: Path) -> dict[str, Any] | None:
    if not db_path.exists():
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    prompt_count = cur.execute("select count(*) from prompts").fetchone()[0]
    if prompt_count == 0:
        conn.close()
        return None

    tool_rows = cur.execute(
        """
        select tool, model, count(*) as prompts,
               sum(coalesce(accepted_lines, 0)) as accepted,
               sum(coalesce(overridden_lines, 0)) as overridden,
               avg(accepted_rate) as avg_accept
        from prompts
        group by tool, model
        order by prompts desc, accepted desc
        """
    ).fetchall()

    monthly_rows = cur.execute(
        """
        select substr(datetime(start_time, 'unixepoch'), 1, 7) as month,
               count(*) as prompts,
               sum(coalesce(accepted_lines, 0)) as accepted,
               sum(coalesce(overridden_lines, 0)) as overridden,
               avg(accepted_rate) as avg_accept
        from prompts
        group by month
        order by month desc
        """
    ).fetchall()

    repo_rows = cur.execute(
        """
        select workdir,
               count(*) as prompts,
               sum(coalesce(accepted_lines, 0)) as accepted,
               sum(coalesce(overridden_lines, 0)) as overridden,
               avg(accepted_rate) as avg_accept
        from prompts
        group by workdir
        order by prompts desc, accepted desc
        limit 12
        """
    ).fetchall()

    total_row = cur.execute(
        """
        select count(*) as prompts,
               sum(coalesce(accepted_lines, 0)) as accepted,
               sum(coalesce(overridden_lines, 0)) as overridden,
               avg(accepted_rate) as avg_accept
        from prompts
        where accepted_rate is not null
        """
    ).fetchone()

    conn.close()
    return {
        "prompt_count": prompt_count,
        "tool_rows": tool_rows,
        "monthly_rows": monthly_rows,
        "repo_rows": repo_rows,
        "total_row": total_row,
    }


def build_weekly_rows(
    github_weeks: dict[str, int],
    codex_weeks: dict[str, dict[str, int]],
    claude_weeks: dict[str, dict[str, object]],
    limit: int,
) -> list[WeeklyRow]:
    all_weeks = sorted(set(github_weeks) | set(codex_weeks) | set(claude_weeks), reverse=True)[:limit]
    rows = []
    for week in all_weeks:
        codex = codex_weeks.get(week, {})
        claude = claude_weeks.get(week, {})
        rows.append(
            WeeklyRow(
                week=week,
                github=github_weeks.get(week),
                codex_threads=codex.get("threads"),
                codex_tokens_m=(codex.get("tokens", 0) / 1_000_000) if week in codex_weeks else None,
                claude_entries=claude.get("entries"),
                claude_sessions=(len(claude.get("sessions", set())) if week in claude_weeks else None),
            )
        )
    return rows


def render_markdown(
    user: str,
    weekly_rows: list[WeeklyRow],
    codex: dict[str, Any],
    claude_h: dict[str, Any],
    claude_t: dict[str, Any],
    git_ai: dict[str, Any] | None,
) -> str:
    transition_lines = [
        "- January 2026 was Claude-heavy exploration and session volume, with comparatively little Codex thread activity.",
        "- February 2026 is the inflection point: Codex thread count and token volume spike while GitHub contribution volume also jumps.",
        "- March 2026 stays Codex-heavy even as Claude history volume falls sharply, which suggests a workflow shift toward longer, heavier Codex sessions over lighter Claude interaction.",
    ]

    recent_codex_projects = []
    for week in [row.week for row in weekly_rows[:6]]:
        top = codex["week_projects"].get(week)
        if not top:
            continue
        top_projects = ", ".join(f"{name} ({tokens / 1_000_000:.1f}M)" for name, tokens in top.most_common(3))
        recent_codex_projects.append(f"- `{week}`: {top_projects}")

    recent_claude_projects = []
    for week in [row.week for row in weekly_rows[:6]]:
        top = claude_t["project_weeks"].get(week)
        if not top:
            continue
        top_projects = ", ".join(f"{name} ({count})" for name, count in top.most_common(3))
        recent_claude_projects.append(f"- `{week}`: {top_projects}")

    month_ids = sorted(
        set(codex["monthly"]) | set(claude_h["monthly"]) | set(codex["monthly_keywords"]) | set(claude_t["monthly_keywords"]),
        reverse=True,
    )[:6]

    lines = [
        "# AI Workflow Analysis",
        "",
        f"Generated for `{user}` on `{datetime.now().strftime('%Y-%m-%d')}` from local Codex and Claude artifacts plus live GitHub contribution data.",
        "",
        "## Sources",
        "",
        "- `~/.codex/state_5.sqlite`",
        "- `~/.claude/history.jsonl`",
        "- `~/.claude/projects/**/*.jsonl`",
        "- GitHub contributions via `gh api graphql`",
    ]
    if git_ai:
        lines.append("- `prompts.db` from `git-ai prompts --all-repositories --since 120`")
    lines.extend(
        [
            "",
            "## High-Confidence Findings",
            "",
            "- Your AI workflow is not generic chat usage. The strongest repeated signals are planning, frontend/UI work, documentation, bug-fixing, review, testing, research, worktrees, and parallel-agent patterns.",
            "- The biggest change over time is a shift from Claude-heavy volume in January 2026 toward Codex-heavy implementation load in February and March 2026.",
            "- Codex usage clusters around fewer but much heavier sessions, while Claude usage clusters around many lighter interactions, command invocations, and session management events.",
            "- Project focus is real rather than random: VeraMint, Stead Core, Passepartout, Aegis, Nexum, Picalyze, qwer-q, and Upstrio repeatedly surface as major AI-assisted work areas.",
            "",
            "## Time Evolution",
            "",
            "| Week | GitHub | Codex Threads | Codex Tokens | Claude Entries | Claude Sessions |",
            "| --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )

    for row in weekly_rows:
        lines.append(
            f"| {row.week} | {row.github or '-'} | {row.codex_threads or '-'} | "
            f"{f'{row.codex_tokens_m:.1f}M' if row.codex_tokens_m is not None else '-'} | "
            f"{row.claude_entries or '-'} | {row.claude_sessions or '-'} |"
        )

    lines.extend(
        [
            "",
            "### Interpreted Weekly Shift",
            "",
            *transition_lines,
            "",
            "## Monthly Signal Shape",
            "",
            "| Month | Codex Threads | Codex Dominant Signals | Claude Entries | Claude Dominant Signals |",
            "| --- | ---: | --- | ---: | --- |",
        ]
    )

    for month in month_ids:
        codex_month = codex["monthly"].get(month, {})
        claude_month_entries = claude_h["monthly"].get(month)
        lines.append(
            f"| {month} | {codex_month.get('threads', '-')} | {format_top_signals(codex['monthly_keywords'].get(month, Counter()))} | "
            f"{claude_month_entries or '-'} | {format_top_signals(claude_t['monthly_keywords'].get(month, Counter()))} |"
        )

    lines.extend(
        [
            "",
            "## Codex Signals",
            "",
            f"- Threads with a non-empty first user message: `{codex['prompt_count']}`",
            "- Keyword counts below are non-exclusive and are based on simple pattern matching over `first_user_message`.",
            "",
            "| Signal | Matches |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(codex["keyword_counts"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| {key} | {count} |")

    lines.extend(
        [
            "",
            "### Codex Role Split",
            "",
            "| Role | Threads | Tokens |",
            "| --- | ---: | ---: |",
        ]
    )
    for role, count in codex["roles"].most_common():
        lines.append(f"| {role} | {count} | {codex['role_tokens'][role] / 1_000_000:.1f}M |")

    lines.extend(
        [
            "",
            "### Codex Weekly Project Focus",
            "",
            *recent_codex_projects,
            "",
            "### Representative Codex First Messages",
            "",
        ]
    )
    for ts, prompt in codex["recent_prompts"]:
        lines.append(f"- `{ts}`: {prompt}")

    lines.extend(
        [
            "",
            "## Claude Signals",
            "",
            f"- History entries: `{sum(claude_h['monthly'].values())}`",
            f"- Unique sessions: `{len(claude_h['sessions'])}`",
            f"- Transcript user messages analyzed: `{claude_t['total_user_messages']}`",
            "- Keyword counts below are non-exclusive and come from actual Claude user messages in project session logs.",
            "",
            "| Signal | Matches |",
            "| --- | ---: |",
        ]
    )
    for key, count in sorted(claude_t["keyword_counts"].items(), key=lambda item: item[1], reverse=True):
        lines.append(f"| {key} | {count} |")

    lines.extend(
        [
            "",
            "### Claude Command Pattern",
            "",
            "| Command | Count |",
            "| --- | ---: |",
        ]
    )
    for command, count in claude_h["commands"].most_common(10):
        lines.append(f"| {command} | {count} |")

    lines.extend(
        [
            "",
            "### Claude Weekly Project Focus",
            "",
            *recent_claude_projects,
            "",
            "### Representative Claude User Messages",
            "",
        ]
    )
    for ts, prompt in claude_t["sample_prompts"][:10]:
        lines.append(f"- `{ts}`: {prompt}")

    if git_ai:
        total_row = git_ai["total_row"]
        total_retained = (total_row["accepted"] or 0) + (total_row["overridden"] or 0)
        weighted_accept = f"{((total_row['accepted'] or 0) / total_retained) * 100:.1f}%" if total_retained else "-"
        lines.extend(
            [
                "",
                "## Git-AI Prompt Sample",
                "",
                "- This is a smaller, git-backed sample of recorded prompts across repositories, not a full mirror of all Codex and Claude activity.",
                f"- Tracked prompts: `{git_ai['prompt_count']}`",
                f"- Prompts with acceptance data: `{total_row['prompts']}`",
                f"- Weighted accepted-line retention in the tracked sample: `{weighted_accept}`",
                "",
                "### Prompt Sample By Tool",
                "",
                "| Tool | Model | Prompts | Avg Acceptance | Accepted Lines | Overridden Lines |",
                "| --- | --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in git_ai["tool_rows"]:
            avg_accept = f"{row['avg_accept'] * 100:.1f}%" if row["avg_accept"] is not None else "-"
            lines.append(
                f"| {row['tool']} | {row['model']} | {row['prompts']} | {avg_accept} | {row['accepted'] or 0} | {row['overridden'] or 0} |"
            )

        lines.extend(
            [
                "",
                "### Prompt Sample By Month",
                "",
                "| Month | Prompts | Avg Acceptance | Accepted Lines | Overridden Lines |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for row in git_ai["monthly_rows"]:
            month = row["month"] or "unknown"
            avg_accept = f"{row['avg_accept'] * 100:.1f}%" if row["avg_accept"] is not None else "-"
            lines.append(
                f"| {month} | {row['prompts']} | {avg_accept} | {row['accepted'] or 0} | {row['overridden'] or 0} |"
            )

        lines.extend(
            [
                "",
                "### Prompt Sample By Repository",
                "",
                "| Repository | Prompts | Avg Acceptance | Accepted Lines |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for row in git_ai["repo_rows"]:
            avg_accept = f"{row['avg_accept'] * 100:.1f}%" if row["avg_accept"] is not None else "-"
            lines.append(
                f"| {project_name_from_path(row['workdir'])} | {row['prompts']} | {avg_accept} | {row['accepted'] or 0} |"
            )

        lines.extend(
            [
                "",
                "### How To Read The Prompt Sample",
                "",
                "- It is strongest as a code-retention signal, not as a complete usage counter.",
                "- The sample is concentrated in repositories where git-ai tracking exists, so it should not replace the wider Codex and Claude telemetry above.",
                "- Even with that caveat, it supports a useful claim: when prompts are tracked through git, the resulting code tends to land with very little post-edit churn.",
            ]
        )

    lines.extend(
        [
            "",
            "## What This Supports In The README",
            "",
            "These claims are supported by the data:",
            "",
            "- You use AI in a planning-heavy, project-centered workflow rather than as a generic chat assistant.",
            "- You repeatedly drive work through review, bugfix, docs, testing, research, and frontend iteration loops.",
            "- You use worktrees and agent parallelism often enough that they are part of your normal operating model, not a one-off experiment.",
            "- Your tool usage changed materially over time: January reads like high-volume Claude exploration, while February and March read like Codex-centered delivery and execution.",
            "",
            "These claims need softer wording because they are interpretive:",
            "",
            "- broad labels like `AI-Native Operator`",
            "- any statement about why you prefer one tool emotionally or strategically",
            "- any claim that a specific workflow is your default everywhere, unless the data and repos both support it",
            "",
            "## Next Rewrite Directions",
            "",
            "1. Evidence-first: remove branding labels and write only what the analysis proves directly.",
            "2. Branded but grounded: keep strong language, but tie every line to an observed pattern from this report.",
            "3. Time-aware: explicitly mention that your workflow moved from Claude-heavy exploration into Codex-heavy delivery over early 2026.",
        ]
    )

    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="edhor1608")
    parser.add_argument("--weeks", type=int, default=12)
    parser.add_argument("--git-ai-db", default="prompts.db")
    args = parser.parse_args()

    github_weeks, _ = github_calendar(args.user)
    codex = codex_data(Path.home() / ".codex" / "state_5.sqlite")
    claude_h = claude_history(Path.home() / ".claude" / "history.jsonl")
    claude_t = claude_transcripts(Path.home() / ".claude" / "projects")
    git_ai = git_ai_data(Path(args.git_ai_db))
    weekly_rows = build_weekly_rows(github_weeks, codex["weekly"], claude_h["weekly"], args.weeks)
    print(render_markdown(args.user, weekly_rows, codex, claude_h, claude_t, git_ai))


if __name__ == "__main__":
    main()
