# Profile Fact Audit - 2026-05-24

This audit backs the public README wording. It uses local machine artifacts and GitHub metadata available on 2026-05-24.

## Sources

- `~/.codex/state_5.sqlite`
- `~/.claude/history.jsonl`
- `~/.claude/projects/**/*.jsonl`
- `~/.pi/agent/sessions/**/*.jsonl`
- `~/.cursor/acp-sessions/*/meta.json`
- `~/.cursor/ai-tracking/ai-code-tracking.db`
- `gh repo list edhor1608`
- installed local skills under `~/.agents/skills`

## Current Project Evidence

Recent GitHub pushes in the last 60 days include:

| Repo | Visibility | Pushed | Note |
| --- | --- | --- | --- |
| passepartout | public | 2026-05-22 | photography export tool |
| qwer-q | public | 2026-05-21 | typed message queue |
| pi-tools | public | 2026-05-21 | Pi package with model prompts and structured compaction |
| meinungsmache-app | private | 2026-05-21 | VeraMint product work |
| picalyze | private | 2026-05-21 | Picalyze product work |
| zero | public | 2026-05-16 | programming language for agents |
| sandcastle | public | 2026-05-06 | sandboxed coding-agent orchestration |
| aurora | public | 2026-05-02 | community platform |

Recent Codex load tells a slightly different story from public pushes:

| Window | Top Codex Project Signals |
| --- | --- |
| Last 30 days | aurora 1.84B tokens, Picalyze 411.5M, zero-sense 243.8M, passepartout 221.3M, VeraMint 191.7M, stead 176.2M, pi-tools 122.3M |
| Last 60 days | repos root 6.62B tokens, VeraMint 2.05B, aurora 1.84B, stead 446.3M, Picalyze 411.5M, zero-sense 243.8M |

README implication: keep `pi-tools`, `qwer-q`, `passepartout`, `zero`, `aurora`, `VeraMint`, and `Picalyze` visible. Treat `stead` as historically important but not a current headline unless the focus shifts back.

## Workflow Evidence

Codex thread openers with a non-empty first user message: `926`.

All-time Codex opener signals:

| Signal | Matches |
| --- | ---: |
| plan | 446 |
| research | 359 |
| agent | 274 |
| frontend | 224 |
| docs | 195 |
| pr | 145 |
| test | 129 |
| bugfix | 125 |
| review | 111 |
| worktree | 74 |

Last 60 days of Codex opener signals:

| Signal | Matches |
| --- | ---: |
| plan | 367 |
| research | 322 |
| agent | 265 |
| docs | 127 |
| frontend | 115 |
| pr | 113 |
| test | 106 |
| bugfix | 99 |
| review | 62 |
| worktree | 54 |

Last 30 days of Codex opener signals:

| Signal | Matches |
| --- | ---: |
| bugfix | 15 |
| frontend | 12 |
| docs | 12 |
| research | 12 |
| triage | 12 |
| plan | 11 |
| skill | 11 |
| review | 6 |
| agent | 5 |

README implication: "planning-heavy" is true historically, but recent wording should also mention bugfix, docs, frontend, research, and triage.

## Tool Evidence

Codex model split:

| Window | Model | Threads | Tokens |
| --- | --- | ---: | ---: |
| All time | gpt-5.4 | 558 | 10.54B |
| All time | gpt-5.5 | 123 | 4.33B |
| All time | gpt-5.3-codex | 51 | 1.65B |
| Last 30 days | gpt-5.5 | 119 | 4.26B |

Pi:

| Metric | Value |
| --- | ---: |
| Session files | 35 |
| Message entries | 10,934 |
| Projects | 9 |
| pi-tools sessions | 9 |

Cursor:

| Metric | Value |
| --- | ---: |
| ACP session metadata files | 71,463 |
| AI code hashes | 346 |
| AI code hashes with gpt-5.5 | 131 |

Cursor caveat: ACP metadata currently mostly reports `home` as cwd, so it is a poor source for project priority.

Claude:

| Period | Signal |
| --- | --- |
| 2026-01 | 1,512 history entries |
| 2026-W21 | 10 history entries |
| 2026-W19 | 38 history entries |

README implication: Claude was a high-volume exploration layer early in 2026, but current wording should not imply it is still the main lane.

## Skill Evidence

Installed local skills: `29`.

Recent Codex opener skill mentions:

| Skill | Last 30d Mentions |
| --- | ---: |
| setup-matt-pocock-skills | 6 |
| grill-with-docs | 2 |
| workflow | 1 |

Pi transcripts include recurring references to workflow, TDD, triage, prototype, and PR-comment skill flows. These counts are content mentions inside transcripts, not guaranteed proof of direct invocation.

README implication: say local skills are installed and visible in recent prompts. Avoid claiming every skill is a dominant active lane.

## Copy Changes This Supports

- Replace broad "AI-Native Operator" wording with evidence-first workflow wording.
- Keep Codex as the current heavy execution lane.
- Treat Claude as historically important and currently lower-volume.
- Mention Pi as a concrete smaller lane with `pi-tools`.
- Mention Cursor as footprint/code-tracking evidence, not as project-priority evidence.
- Keep current project priorities tied to both GitHub push recency and local AI session load.
