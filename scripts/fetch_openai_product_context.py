#!/usr/bin/env python3

from __future__ import annotations

import argparse
import html
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SourceCheck:
    label: str
    pattern: str


@dataclass(frozen=True)
class Source:
    title: str
    url: str
    checks: tuple[SourceCheck, ...]


@dataclass(frozen=True)
class CheckResult:
    label: str
    matched: bool


@dataclass(frozen=True)
class SourceResult:
    title: str
    url: str
    ok: bool
    error: str | None
    checks: tuple[CheckResult, ...]


SOURCES = (
    Source(
        title="ChatGPT release notes",
        url="https://help.openai.com/en/articles/6825453-chatgpt-apps-on-ios-and-android",
        checks=(
            SourceCheck("2026-05-21 Codex update", r"May\s+21,\s+2026.*?Codex updates"),
            SourceCheck("Appshots", r"\bAppshots\b"),
            SourceCheck("Goal mode GA", r"Goal mode.*?generally available"),
            SourceCheck("Browser annotations", r"in-app browser annotations"),
            SourceCheck("Locked remote use", r"Locked computer use|locked remote use|remote locked use"),
            SourceCheck("Mobile remote access", r"Codex remote access from the ChatGPT mobile app"),
        ),
    ),
    Source(
        title="Codex changelog",
        url="https://developers.openai.com/codex/changelog",
        checks=(
            SourceCheck("Work from anywhere", r"Work with Codex from anywhere"),
            SourceCheck("Connected Mac host", r"connecting it to a Mac running the Codex app"),
            SourceCheck("Host context follows mobile", r"projects, files, credentials, plugins, skills"),
            SourceCheck("Hooks GA nearby", r"Hooks general availability"),
        ),
    ),
    Source(
        title="Image generation docs",
        url="https://platform.openai.com/docs/guides/image-generation",
        checks=(
            SourceCheck("Latest GPT Image model", r"latest[^.]{0,120}gpt-image-2"),
            SourceCheck("GPT Image family", r"GPT Image models"),
        ),
    ),
    Source(
        title="Code generation docs",
        url="https://platform.openai.com/docs/guides/code-generation",
        checks=(
            SourceCheck("Codex interfaces", r"IDE.*?CLI.*?web and mobile sites.*?CI/CD"),
            SourceCheck("GPT-5.5 coding default", r"gpt-5\.5"),
            SourceCheck("Agentic software engineering", r"agentic software engineering"),
        ),
    ),
)


def fetch_text(url: str, timeout: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "profile-fact-audit/1.0"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = response.read()
    return data.decode("utf-8", errors="replace")


def normalize(text: str) -> str:
    text = re.sub(r"<script\b.*?</script>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text)


def check_source(source: Source, timeout: int, offline: bool) -> SourceResult:
    if offline:
        return SourceResult(
            title=source.title,
            url=source.url,
            ok=False,
            error="offline mode",
            checks=tuple(CheckResult(check.label, False) for check in source.checks),
        )

    try:
        text = normalize(fetch_text(source.url, timeout))
    except (OSError, urllib.error.URLError, TimeoutError) as error:
        return SourceResult(
            title=source.title,
            url=source.url,
            ok=False,
            error=str(error),
            checks=tuple(CheckResult(check.label, False) for check in source.checks),
        )

    checks = tuple(
        CheckResult(check.label, bool(re.search(check.pattern, text, flags=re.I | re.S)))
        for check in source.checks
    )
    return SourceResult(
        title=source.title,
        url=source.url,
        ok=all(check.matched for check in checks),
        error=None,
        checks=checks,
    )


def check_sources(timeout: int = 15, offline: bool = False) -> list[SourceResult]:
    return [check_source(source, timeout, offline) for source in SOURCES]


def render_markdown(results: list[SourceResult]) -> str:
    lines = [
        "# OpenAI Product Context",
        "",
        f"Checked on `{datetime.now().strftime('%Y-%m-%d')}`.",
        "",
        "| Source | Status | Matched | Missing |",
        "| --- | --- | --- | --- |",
    ]
    for result in results:
        matched = [check.label for check in result.checks if check.matched]
        missing = [check.label for check in result.checks if not check.matched]
        status = "OK" if result.ok else "CHECK"
        if result.error:
            status = f"ERROR: {result.error}"
        lines.append(
            f"| [{result.title}]({result.url}) | {status} | {', '.join(matched) or '-'} | {', '.join(missing) or '-'} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    print(render_markdown(check_sources(timeout=args.timeout, offline=args.offline)))


if __name__ == "__main__":
    main()
