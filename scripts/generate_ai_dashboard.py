#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sqlite3
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


NAME_MAP = {
    "jonas": "home",
    "meinungsmache-app": "VeraMint",
    "repos": "repos root",
    "picalyze": "Picalyze",
}

MonthlyRow = tuple[str, int | None, int | None, float | None, int | None, int | None, int | None]


@dataclass
class DashboardData:
    snapshot_date: str
    codex_threads: int
    codex_tokens: int
    codex_workdirs: int
    claude_entries: int
    claude_sessions: int
    claude_projects: int
    pi_sessions: int
    pi_messages: int
    pi_projects: int
    cursor_sessions: int
    cursor_workdirs: int
    cursor_code_hashes: int
    cursor_conversations: int
    github_contributions: int
    github_prs: int
    github_private: int
    repo_total: int
    repo_public: int
    repo_private: int
    repos_pushed_this_year: int
    monthly_rows: list[MonthlyRow]
    load_rows: list[MonthlyRow]
    codex_projects: list[tuple[str, int, float]]
    claude_projects_top: list[tuple[str, int]]
    pi_projects_top: list[tuple[str, int]]
    cursor_projects_top: list[tuple[str, int]]
    codex_roles: list[tuple[str, int, float]]
    claude_commands: list[tuple[str, int]]
    pi_models: list[tuple[str, int]]
    cursor_models: list[tuple[str, int]]


def run_json(cmd: list[str]) -> object:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def run_text(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def month_from_ms(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%Y-%m")


def month_from_seconds(timestamp_seconds: float) -> str:
    return datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc).strftime("%Y-%m")


def pretty_name(raw: str) -> str:
    return NAME_MAP.get(raw, raw)


def project_name_from_path(path_text: str) -> str:
    return pretty_name(Path(path_text).name or path_text)


def format_int(value: int) -> str:
    return f"{value:,}"


def format_tokens_billions(value: int) -> str:
    return f"{value / 1_000_000_000:.2f}B"


def format_tokens_millions(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.1f}M"


def format_optional_int(value: int | None) -> str:
    if value is None:
        return "-"
    return str(value)


def bar(value: int | float | None, max_value: int | float | None, width: int = 20) -> str:
    if not value or not max_value:
        filled = 0
    else:
        filled = max(1, round((value / max_value) * width))
    filled = min(width, filled)
    return "#" * filled + "." * (width - filled)


def github_stats(user: str) -> tuple[int, int, int, dict[str, int]]:
    query = (
        "query { user(login: \"%s\") { contributionsCollection { "
        "contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } "
        "restrictedContributionsCount totalPullRequestContributions } } }"
    ) % user
    payload = run_json(["gh", "api", "graphql", "-f", f"query={query}"])
    collection = payload["data"]["user"]["contributionsCollection"]
    months: dict[str, int] = {}
    for week in collection["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            month = day["date"][:7]
            months[month] = months.get(month, 0) + day["contributionCount"]
    return (
        collection["contributionCalendar"]["totalContributions"],
        collection["totalPullRequestContributions"],
        collection["restrictedContributionsCount"],
        months,
    )


def repo_stats(user: str, year: int) -> tuple[int, int, int, int]:
    repos = run_json(
        [
            "gh",
            "repo",
            "list",
            user,
            "--limit",
            "200",
            "--json",
            "isPrivate,pushedAt",
        ]
    )
    total = len(repos)
    private = sum(1 for repo in repos if repo["isPrivate"])
    public = total - private
    pushed = sum(
        1
        for repo in repos
        if repo["pushedAt"] and repo["pushedAt"] >= f"{year}-01-01T00:00:00Z"
    )
    return total, public, private, pushed


def codex_stats(db_path: Path) -> tuple[int, int, int, dict[str, tuple[int, float]], list[tuple[str, int, float]], list[tuple[str, int, float]]]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    codex_threads, codex_tokens, codex_workdirs = cur.execute(
        "select count(*), coalesce(sum(tokens_used), 0), count(distinct cwd) from threads"
    ).fetchone()

    monthly_rows = cur.execute(
        """
        select substr(datetime(created_at, 'unixepoch'), 1, 7) as month,
               count(*) as threads,
               round(sum(tokens_used) / 1000000.0, 1) as tokens_m
        from threads
        group by month
        order by month desc
        """
    ).fetchall()
    monthly = {month: (threads, tokens_m) for month, threads, tokens_m in monthly_rows}

    project_rows = cur.execute(
        """
        select cwd, count(*) as threads, round(sum(tokens_used) / 1000000.0, 1) as tokens_m
        from threads
        group by cwd
        order by sum(tokens_used) desc
        limit 6
        """
    ).fetchall()
    projects = [(pretty_name(Path(cwd).name), threads, tokens_m) for cwd, threads, tokens_m in project_rows]

    role_rows = cur.execute(
        """
        select coalesce(agent_role, 'main'), count(*), round(sum(tokens_used) / 1000000.0, 1)
        from threads
        group by coalesce(agent_role, 'main')
        order by sum(tokens_used) desc
        limit 8
        """
    ).fetchall()

    conn.close()
    return codex_threads, codex_tokens, codex_workdirs, monthly, projects, role_rows


def claude_stats(history_path: Path) -> tuple[int, int, int, dict[str, int], list[tuple[str, int]], list[tuple[str, int]]]:
    entry_count = 0
    sessions: set[str] = set()
    projects_all: set[str] = set()
    months: Counter[str] = Counter()
    project_counter: Counter[str] = Counter()
    command_counter: Counter[str] = Counter()

    with history_path.open() as handle:
        for line in handle:
            entry_count += 1
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            timestamp = obj.get("timestamp")
            if isinstance(timestamp, (int, float)):
                months[month_from_ms(int(timestamp))] += 1
            session_id = obj.get("sessionId")
            if isinstance(session_id, str) and session_id:
                sessions.add(session_id)
            project = obj.get("project")
            if isinstance(project, str) and project:
                projects_all.add(project)
                if project not in {"/Users/jonas", "/Users/jonas/repos"}:
                    project_counter[pretty_name(Path(project).name)] += 1
            display = obj.get("display")
            if isinstance(display, str) and display.startswith("/"):
                command_counter[display.split()[0]] += 1

    return (
        entry_count,
        len(sessions),
        len(projects_all),
        dict(months),
        project_counter.most_common(6),
        command_counter.most_common(8),
    )


def pi_stats(sessions_path: Path) -> tuple[int, int, int, dict[str, int], list[tuple[str, int]], list[tuple[str, int]]]:
    session_count = 0
    message_count = 0
    months: Counter[str] = Counter()
    projects: Counter[str] = Counter()
    models: Counter[str] = Counter()

    if not sessions_path.exists():
        return 0, 0, 0, {}, [], []

    for path in sessions_path.glob("**/*.jsonl"):
        session_count += 1
        session_seen = False
        try:
            handle = path.open()
        except OSError:
            continue
        with handle:
            for line in handle:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                entry_type = obj.get("type")
                if entry_type == "session" and not session_seen:
                    session_seen = True
                    timestamp = obj.get("timestamp")
                    if isinstance(timestamp, str) and len(timestamp) >= 7:
                        months[timestamp[:7]] += 1
                    cwd = obj.get("cwd")
                    if isinstance(cwd, str) and cwd:
                        projects[project_name_from_path(cwd)] += 1
                elif entry_type == "message":
                    message_count += 1
                    message = obj.get("message")
                    if isinstance(message, dict):
                        model = message.get("model")
                        if isinstance(model, str) and model:
                            models[model] += 1
                elif entry_type == "model_change":
                    model = obj.get("modelId")
                    if isinstance(model, str) and model:
                        models[model] += 1

        if not session_seen:
            months[month_from_seconds(path.stat().st_mtime)] += 1

    return (
        session_count,
        message_count,
        len(projects),
        dict(months),
        projects.most_common(6),
        models.most_common(8),
    )


def cursor_stats(cursor_path: Path) -> tuple[int, int, int, int, dict[str, int], list[tuple[str, int]], list[tuple[str, int]]]:
    session_count = 0
    months: Counter[str] = Counter()
    projects: Counter[str] = Counter()
    code_hashes = 0
    conversations = 0
    models: Counter[str] = Counter()

    sessions_path = cursor_path / "acp-sessions"
    if sessions_path.exists():
        for path in sessions_path.glob("*/meta.json"):
            session_count += 1
            months[month_from_seconds(path.stat().st_mtime)] += 1
            try:
                meta = json.loads(path.read_text())
            except (OSError, json.JSONDecodeError):
                continue
            cwd = meta.get("cwd")
            if isinstance(cwd, str) and cwd:
                projects[project_name_from_path(cwd)] += 1

    tracking_db = cursor_path / "ai-tracking" / "ai-code-tracking.db"
    if tracking_db.exists():
        try:
            conn = sqlite3.connect(f"file:{tracking_db}?mode=ro", uri=True)
            cur = conn.cursor()
            code_hashes = cur.execute("select count(*) from ai_code_hashes").fetchone()[0]
            conversations = cur.execute("select count(*) from conversation_summaries").fetchone()[0]
            for model, count in cur.execute(
                """
                select coalesce(model, 'unknown'), count(*)
                from ai_code_hashes
                group by coalesce(model, 'unknown')
                order by count(*) desc
                limit 8
                """
            ).fetchall():
                models[model] = count
            conn.close()
        except sqlite3.Error:
            pass

    return (
        session_count,
        len(projects),
        code_hashes,
        conversations,
        dict(months),
        projects.most_common(6),
        models.most_common(8),
    )


def build_data(user: str, months_to_show: int) -> DashboardData:
    total_contribs, total_prs, private_contribs, github_months = github_stats(user)
    total_repos, public_repos, private_repos, repos_pushed = repo_stats(user, datetime.now().year)
    codex_threads, codex_tokens, codex_workdirs, codex_months, codex_projects, codex_roles = codex_stats(
        Path.home() / ".codex" / "state_5.sqlite"
    )
    claude_entries, claude_sessions, claude_projects_count, claude_months, claude_projects, claude_commands = claude_stats(
        Path.home() / ".claude" / "history.jsonl"
    )
    pi_sessions, pi_messages, pi_projects_count, pi_months, pi_projects, pi_models = pi_stats(
        Path.home() / ".pi" / "agent" / "sessions"
    )
    cursor_sessions, cursor_workdirs, cursor_code_hashes, cursor_conversations, cursor_months, cursor_projects, cursor_models = cursor_stats(
        Path.home() / ".cursor"
    )

    all_months = sorted(
        set(github_months) | set(codex_months) | set(claude_months) | set(pi_months) | set(cursor_months),
        reverse=True,
    )[:months_to_show]

    monthly_rows: list[MonthlyRow] = []
    for month in all_months:
        codex_threads_month, codex_tokens_month = codex_months.get(month, (None, None))
        monthly_rows.append(
            (
                month,
                github_months.get(month),
                codex_threads_month,
                codex_tokens_month,
                claude_months.get(month),
                pi_months.get(month),
                cursor_months.get(month),
            )
        )

    return DashboardData(
        snapshot_date=datetime.now().strftime("%Y-%m-%d"),
        codex_threads=codex_threads,
        codex_tokens=codex_tokens,
        codex_workdirs=codex_workdirs,
        claude_entries=claude_entries,
        claude_sessions=claude_sessions,
        claude_projects=claude_projects_count,
        pi_sessions=pi_sessions,
        pi_messages=pi_messages,
        pi_projects=pi_projects_count,
        cursor_sessions=cursor_sessions,
        cursor_workdirs=cursor_workdirs,
        cursor_code_hashes=cursor_code_hashes,
        cursor_conversations=cursor_conversations,
        github_contributions=total_contribs,
        github_prs=total_prs,
        github_private=private_contribs,
        repo_total=total_repos,
        repo_public=public_repos,
        repo_private=private_repos,
        repos_pushed_this_year=repos_pushed,
        monthly_rows=monthly_rows,
        load_rows=monthly_rows[:3],
        codex_projects=codex_projects,
        claude_projects_top=claude_projects,
        pi_projects_top=pi_projects,
        cursor_projects_top=cursor_projects,
        codex_roles=codex_roles,
        claude_commands=claude_commands,
        pi_models=pi_models,
        cursor_models=cursor_models,
    )


def render_markdown(data: DashboardData) -> str:
    github_max = max((row[1] or 0 for row in data.load_rows), default=0)
    codex_threads_max = max((row[2] or 0 for row in data.load_rows), default=0)
    codex_tokens_max = max((row[3] or 0 for row in data.load_rows), default=0)
    claude_max = max((row[4] or 0 for row in data.load_rows), default=0)
    pi_max = max((row[5] or 0 for row in data.load_rows), default=0)
    cursor_max = max((row[6] or 0 for row in data.load_rows), default=0)

    lines = [
        "## AI Operations Dashboard",
        "",
        f"Snapshot as of `{data.snapshot_date}`.",
        "",
        "<table>",
        "  <tr>",
        '    <td valign="top">',
        "      <strong>Codex</strong><br/>",
        f"      {format_int(data.codex_threads)} tracked threads<br/>",
        f"      {format_tokens_billions(data.codex_tokens)} tracked tokens<br/>",
        f"      {format_int(data.codex_workdirs)} working directories",
        "    </td>",
        '    <td valign="top">',
        "      <strong>Claude</strong><br/>",
        f"      {format_int(data.claude_entries)} history entries<br/>",
        f"      {format_int(data.claude_sessions)} sessions<br/>",
        f"      {format_int(data.claude_projects)} projects",
        "    </td>",
        '    <td valign="top">',
        "      <strong>Pi</strong><br/>",
        f"      {format_int(data.pi_sessions)} sessions<br/>",
        f"      {format_int(data.pi_messages)} message entries<br/>",
        f"      {format_int(data.pi_projects)} projects",
        "    </td>",
        "  </tr>",
        "  <tr>",
        '    <td valign="top">',
        "      <strong>Cursor</strong><br/>",
        f"      {format_int(data.cursor_sessions)} ACP sessions<br/>",
        f"      {format_int(data.cursor_workdirs)} working {'directory' if data.cursor_workdirs == 1 else 'directories'}<br/>",
        f"      {format_int(data.cursor_code_hashes)} AI code hashes",
        "    </td>",
        '    <td valign="top">',
        "      <strong>GitHub</strong><br/>",
        f"      {format_int(data.github_contributions)} contributions<br/>",
        f"      {format_int(data.github_prs)} PR contributions<br/>",
        f"      {format_int(data.github_private)} private contributions",
        "    </td>",
        "  </tr>",
        "</table>",
        "",
        "### Monthly View",
        "",
        "| Month | GitHub Contributions | Codex Threads | Codex Tokens | Claude Entries | Pi Sessions | Cursor ACP Sessions |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for month, github, codex_threads, codex_tokens, claude, pi, cursor in data.monthly_rows:
        lines.append(
            f"| {month} | {format_optional_int(github)} | {format_optional_int(codex_threads)} | {format_tokens_millions(codex_tokens)} | {format_optional_int(claude)} | {format_optional_int(pi)} | {format_optional_int(cursor)} |"
        )

    lines.extend(
        [
            "",
            "### Monthly Load",
            "",
            "```text",
        ]
    )

    for month, github, codex_threads, codex_tokens, claude, pi, cursor in data.load_rows:
        gh_text = format_optional_int(github).rjust(3)
        codex_threads_text = format_optional_int(codex_threads).rjust(3)
        codex_tokens_text = (format_tokens_millions(codex_tokens).rjust(8) if codex_tokens is not None else "       -")
        claude_text = format_optional_int(claude).rjust(4)
        pi_text = format_optional_int(pi).rjust(3)
        cursor_text = format_optional_int(cursor).rjust(5)
        lines.append(
            f"{month}  GH {gh_text}  |{bar(github, github_max)}|  "
            f"Codex {codex_threads_text} threads |{bar(codex_threads, codex_threads_max)}|  "
            f"Tokens {codex_tokens_text} |{bar(codex_tokens, codex_tokens_max)}|  "
            f"Claude {claude_text} |{bar(claude, claude_max)}|  "
            f"Pi {pi_text} |{bar(pi, pi_max)}|  "
            f"Cursor {cursor_text} |{bar(cursor, cursor_max)}|"
        )

    lines.extend(
        [
            "```",
            "",
            "### Top Projects",
            "",
            "**Codex**",
            "",
            "| Project | Threads | Tokens |",
            "| --- | ---: | ---: |",
        ]
    )

    for project, threads, tokens_m in data.codex_projects:
        lines.append(f"| {project} | {threads} | {tokens_m:.1f}M |")

    lines.extend(
        [
            "",
            "**Claude**",
            "",
            "| Project | Entries |",
            "| --- | ---: |",
        ]
    )

    for project, entries in data.claude_projects_top:
        lines.append(f"| {project} | {entries} |")

    lines.extend(
        [
            "",
            "**Pi**",
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
            "**Cursor**",
            "",
            "| Workdir | ACP Sessions |",
            "| --- | ---: |",
        ]
    )

    for project, sessions in data.cursor_projects_top:
        lines.append(f"| {project} | {sessions} |")

    lines.extend(
        [
            "",
            "<details>",
            "  <summary>More AI internals</summary>",
            "",
            "  <br/>",
            "",
            "  <strong>Codex agent role split</strong>",
            "",
            "  | Role | Threads | Tokens |",
            "  | --- | ---: | ---: |",
        ]
    )

    for role, threads, tokens_m in data.codex_roles:
        lines.append(f"  | {role} | {threads} | {tokens_m:.1f}M |")

    lines.extend(
        [
            "",
            "  <strong>Top Claude commands</strong>",
            "",
            "  | Command | Count |",
            "  | --- | ---: |",
        ]
    )

    for command, count in data.claude_commands:
        lines.append(f"  | {command} | {count} |")

    lines.extend(
        [
            "",
            "  <strong>Pi model events</strong>",
            "",
            "  | Model | Count |",
            "  | --- | ---: |",
        ]
    )

    for model, count in data.pi_models:
        lines.append(f"  | {model} | {count} |")

    lines.extend(
        [
            "",
            "  <strong>Cursor AI code tracking</strong>",
            "",
            f"  - {format_int(data.cursor_code_hashes)} AI code hashes",
            f"  - {format_int(data.cursor_conversations)} conversation summaries",
            "",
            "  | Model | Code Hashes |",
            "  | --- | ---: |",
        ]
    )

    for model, count in data.cursor_models:
        lines.append(f"  | {model} | {count} |")

    lines.extend(
        [
            "",
            "  <strong>Repo footprint</strong>",
            "",
            f"  - {format_int(data.repo_total)} GitHub repositories total",
            f"  - {format_int(data.repo_public)} public repositories",
            f"  - {format_int(data.repo_private)} private repositories",
            f"  - {format_int(data.repos_pushed_this_year)} repositories pushed in {datetime.now().year} already",
            "</details>",
        ]
    )

    return "\n".join(lines)


def render_compact_markdown(data: DashboardData) -> str:
    lines = [
        "## AI Snapshot",
        "",
        f"Snapshot as of `{data.snapshot_date}`. The full evidence trail lives in [`docs/profile-fact-audit-2026-05-24.md`](docs/profile-fact-audit-2026-05-24.md).",
        "",
        "<table>",
        "  <tr>",
        '    <td><strong>Codex</strong><br/>'
        f"{format_int(data.codex_threads)} threads<br/>{format_tokens_billions(data.codex_tokens)} tokens</td>",
        '    <td><strong>GitHub</strong><br/>'
        f"{format_int(data.github_contributions)} contributions<br/>{format_int(data.github_prs)} PRs</td>",
        '    <td><strong>Pi</strong><br/>'
        f"{format_int(data.pi_sessions)} sessions<br/>{format_int(data.pi_messages)} messages</td>",
        '    <td><strong>Cursor</strong><br/>'
        f"{format_int(data.cursor_sessions)} ACP sessions<br/>{format_int(data.cursor_code_hashes)} code hashes</td>",
        "  </tr>",
        "</table>",
        "",
        "| Month | GitHub | Codex | Tokens | Claude | Pi | Cursor |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for month, github, codex_threads, codex_tokens, claude, pi, cursor in data.load_rows:
        lines.append(
            f"| {month} | {format_optional_int(github)} | {format_optional_int(codex_threads)} | {format_tokens_millions(codex_tokens)} | {format_optional_int(claude)} | {format_optional_int(pi)} | {format_optional_int(cursor)} |"
        )

    lines.extend(
        [
            "",
            "| Tool | Why it is here |",
            "| --- | --- |",
            "| `Codex App` | default lane for long-running coding work on `GPT-5.5` |",
            "| `Pi` | clean/raw harness and custom `pi-tools` experiments |",
            "| `GPT Image` | UI direction, visual assets, and interface exploration |",
            "| `Cursor Pro` | editor-side AI and current Claude access path |",
            "| `Claude` / `Opencode Go` | historical telemetry only, not active standalone defaults |",
        ]
    )

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="edhor1608")
    parser.add_argument("--months", type=int, default=7)
    parser.add_argument("--style", choices=("full", "compact"), default="full")
    args = parser.parse_args()
    data = build_data(args.user, args.months)
    renderer = render_compact_markdown if args.style == "compact" else render_markdown
    print(renderer(data))


if __name__ == "__main__":
    main()
