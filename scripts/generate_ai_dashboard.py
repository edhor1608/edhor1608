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
    "meinungsmache-app": "VeraMint",
    "repos": "repos root",
    "picalyze": "Picalyze",
}


@dataclass
class DashboardData:
    snapshot_date: str
    codex_threads: int
    codex_tokens: int
    codex_workdirs: int
    claude_entries: int
    claude_sessions: int
    claude_projects: int
    github_contributions: int
    github_prs: int
    github_private: int
    repo_total: int
    repo_public: int
    repo_private: int
    repos_pushed_this_year: int
    monthly_rows: list[tuple[str, int | None, int | None, float | None, int | None]]
    load_rows: list[tuple[str, int | None, int | None, float | None, int | None]]
    codex_projects: list[tuple[str, int, float]]
    claude_projects_top: list[tuple[str, int]]
    codex_roles: list[tuple[str, int, float]]
    claude_commands: list[tuple[str, int]]


def run_json(cmd: list[str]) -> object:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def run_text(cmd: list[str]) -> str:
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return result.stdout


def month_from_ms(timestamp_ms: int) -> str:
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%Y-%m")


def pretty_name(raw: str) -> str:
    return NAME_MAP.get(raw, raw)


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


def build_data(user: str, months_to_show: int) -> DashboardData:
    total_contribs, total_prs, private_contribs, github_months = github_stats(user)
    total_repos, public_repos, private_repos, repos_pushed = repo_stats(user, datetime.now().year)
    codex_threads, codex_tokens, codex_workdirs, codex_months, codex_projects, codex_roles = codex_stats(
        Path.home() / ".codex" / "state_5.sqlite"
    )
    claude_entries, claude_sessions, claude_projects_count, claude_months, claude_projects, claude_commands = claude_stats(
        Path.home() / ".claude" / "history.jsonl"
    )

    all_months = sorted(
        set(github_months) | set(codex_months) | set(claude_months),
        reverse=True,
    )[:months_to_show]

    monthly_rows: list[tuple[str, int | None, int | None, float | None, int | None]] = []
    for month in all_months:
        codex_threads_month, codex_tokens_month = codex_months.get(month, (None, None))
        monthly_rows.append(
            (
                month,
                github_months.get(month),
                codex_threads_month,
                codex_tokens_month,
                claude_months.get(month),
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
        codex_roles=codex_roles,
        claude_commands=claude_commands,
    )


def render_markdown(data: DashboardData) -> str:
    github_max = max((row[1] or 0 for row in data.load_rows), default=0)
    codex_threads_max = max((row[2] or 0 for row in data.load_rows), default=0)
    codex_tokens_max = max((row[3] or 0 for row in data.load_rows), default=0)
    claude_max = max((row[4] or 0 for row in data.load_rows), default=0)

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
        "| Month | GitHub Contributions | Codex Threads | Codex Tokens | Claude Entries |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]

    for month, github, codex_threads, codex_tokens, claude in data.monthly_rows:
        lines.append(
            f"| {month} | {format_optional_int(github)} | {format_optional_int(codex_threads)} | {format_tokens_millions(codex_tokens)} | {format_optional_int(claude)} |"
        )

    lines.extend(
        [
            "",
            "### Monthly Load",
            "",
            "```text",
        ]
    )

    for month, github, codex_threads, codex_tokens, claude in data.load_rows:
        gh_text = format_optional_int(github).rjust(3)
        codex_threads_text = format_optional_int(codex_threads).rjust(3)
        codex_tokens_text = (format_tokens_millions(codex_tokens).rjust(8) if codex_tokens is not None else "       -")
        claude_text = format_optional_int(claude).rjust(4)
        lines.append(
            f"{month}  GH {gh_text}  |{bar(github, github_max)}|  "
            f"Codex {codex_threads_text} threads |{bar(codex_threads, codex_threads_max)}|  "
            f"Tokens {codex_tokens_text} |{bar(codex_tokens, codex_tokens_max)}|  "
            f"Claude {claude_text} |{bar(claude, claude_max)}|"
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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", default="edhor1608")
    parser.add_argument("--months", type=int, default=7)
    args = parser.parse_args()
    print(render_markdown(build_data(args.user, args.months)))


if __name__ == "__main__":
    main()
