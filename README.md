# Jonas Rohde

I build products, infrastructure, and AI-native delivery systems.

This profile shows the systems I work on, what they do, and how I operate across public and private projects.

## Systems I Ship, Build, And Explore

| Project | State | What it is | Stack | Code |
| --- | --- | --- | --- | --- |
| [VeraMint](https://veramint.de) | active | Mobile news app focused on human-curated journalism, offline-first reading, and media literacy | Expo, React Native, TypeScript, Convex | private |
| [qwer-q](https://github.com/edhor1608/qwer-q) | active | Typed, docker-first message queue with schema registry, durability, and a built-in dashboard | Go, BadgerDB, Docker | public |
| [stead-core](https://github.com/edhor1608/stead-core) | active | Vendor-neutral session standard and interop layer for Codex and Claude Code | TypeScript | public |
| [stead](https://github.com/edhor1608/stead) | active | Workspace orchestrator for terminals, ports, and context | TypeScript | public |
| [aurora](https://github.com/edhor1608/aurora) | active | European community platform with a Convex-first realtime core | TypeScript, React, Convex | public |
| [passepartout](https://github.com/edhor1608/passepartout) | shipped | Photography-first export tool for framed image output and social-ready formats | TypeScript | public |
| edhor-me | active | Personal site and portfolio with an AI-powered ask-me flow | Astro, Tailwind, Playwright, Vercel AI SDK | private |
| [Picalyze](https://picalyze.com) | active | Photography analysis platform for uploading, analyzing, and exploring photo insights | TypeScript, web app stack, third-party photo integrations | private |
| Thinking Loop | active | Deep research and idea-convergence workflow built around iterative agent loops | shell, AI workflows, session tooling | private |
| Fair Creator | active | Transparency-first platform for creator-contractor relationships and fair work standards | TypeScript, TanStack, data pipeline, moderation workflows | private |
| Image Provenance | planning | Verifiable image authenticity that survives social media distribution | Rust, watermarking, distributed registry | private |
| Upstrio | concept | European streaming platform exploring fair economics and distributed infrastructure | architecture, market design, distributed systems | private |

## Live And Runnable Now

- [VeraMint](https://veramint.de) - live public site
- [Picalyze](https://picalyze.com) - live public site
- [qwer-q](https://github.com/edhor1608/qwer-q) - public queue you can run today via Docker or from source
- [passepartout](https://github.com/edhor1608/passepartout) - public CLI you can run locally for image analysis and export workflows
- [aurora](https://github.com/edhor1608/aurora) - public vertical slice with a runnable web app and realtime backend scaffold
- [stead](https://github.com/edhor1608/stead) - public CLI and control-room environment buildable from source

## What I Optimize For

- Shipping real systems, not demo repos
- Small diffs, clear ownership, and boring code that stays easy to change
- Planning before implementation and verifying through checks, tests, and review
- Treating AI as an execution multiplier, not a replacement for engineering judgment

## AI-Native Operator

My AI usage is structured, repo-bound, and phase-dependent rather than one generic chat stream.

### What The Workflow Optimizes For

- Planning and task shaping stay inside the build loop. In Codex thread openers alone, planning-related prompts show up `65` times, documentation `58`, bugfix `49`, review `35`, research `28`, and testing `23`.
- Frontend and product-shaping work are a major slice of the loop. Frontend/UI signals show up `98` times in Codex thread openers and `489` times in Claude transcript user messages.
- Parallel execution is part of the normal operating model. Worktree-specific Codex prompts appear `19` times, explicit agent prompts `9` times, and non-main agent roles account for `32` threads and about `699M` tracked tokens.
- The setup is opinionated rather than scattered. `Codex` is the main delivery lane, and `Claude Code` is the UI and frontend-design sidecar when visual work matters.
- The work stays project-centered. Codex-heavy work clusters around `VeraMint`, `stead-core`, `passepartout`, `Aegis`, and `Nexum`. Claude-heavy work clusters around `Picalyze`, `VeraMint`, `qwer-digest`, `qwer-q`, and `Upstrio`.

### How The Tool Split Looks

- `Claude` carries the high-volume exploration layer. January `2026` alone has `1,512` Claude entries, with dominant signals in bugfixing, planning, testing, and brainstorming.
- `Codex` carries the heavier repo-bound execution layer. The current setup is `GPT-5.4`, mainly through the `codex` CLI, with the Codex app also in use.
- `Claude Code` is the frontend and UI lane. The current setup there is `Opus 4.6` together with the frontend-design skill.
- `T3` is in evaluation, but not yet part of the stable default workflow.
- March `2026` stays Codex-heavy: `76` threads and `1.22B` tracked tokens, while Claude drops to `14` entries and mostly reads as a frontend/UI sidecar. The top Codex signals in March are frontend, docs, brainstorm, and plan, which reads like active product and tooling buildout rather than passive chat.

### What Changed Over Weeks

- `2026-W06`: Claude-heavy phase with `221` entries across `29` sessions and almost no Codex activity.
- `2026-W08`: Codex takes over with `110` threads and `738.7M` tracked tokens while Claude is down to `21` entries.
- `2026-W10`: Codex remains dominant at `53` threads and `717.0M` tracked tokens; Claude is only `12` entries.
- The pattern is consistent: early `2026` starts as high-volume Claude exploration, then shifts into Codex-centered delivery, parallel execution, and longer implementation sessions.

### Tools I Actually Use

- AI: Codex, Claude
- Current setup: `Codex` via `GPT-5.4`, mainly in the CLI, plus the Codex app
- UI setup: `Claude Code` with `Opus 4.6` and the frontend-design skill
- In evaluation: `T3`
- Workflow: `git`, `git worktree`, `gh`, PR review loops, multi-agent execution
- Product stack: TypeScript, Bun, React, Next.js, Astro, Expo, Convex, PostgreSQL
- Delivery and QA: Playwright, Biome, CI workflows, Vercel, Netlify
- Systems work: Go, Rust, Docker

## AI Operations Dashboard

Snapshot as of `2026-03-22`.

<table>
  <tr>
    <td valign="top">
      <strong>Codex</strong><br/>
      251 tracked threads<br/>
      2.98B tracked tokens<br/>
      31 working directories
    </td>
    <td valign="top">
      <strong>Claude</strong><br/>
      2,008 history entries<br/>
      174 sessions<br/>
      15 projects
    </td>
    <td valign="top">
      <strong>GitHub</strong><br/>
      2,005 contributions<br/>
      183 PR contributions<br/>
      1,530 private contributions
    </td>
  </tr>
</table>

### Monthly View

| Month | GitHub Contributions | Codex Threads | Codex Tokens | Claude Entries |
| --- | ---: | ---: | ---: | ---: |
| 2026-03 | 44 | 76 | 1216.9M | 14 |
| 2026-02 | 598 | 143 | 1732.7M | 482 |
| 2026-01 | 634 | 15 | 1.1M | 1512 |
| 2025-12 | 37 | 10 | 3.7M | - |
| 2025-11 | 93 | 2 | 3.9M | - |
| 2025-10 | 69 | 3 | 17.7M | - |
| 2025-09 | 84 | 2 | 2.9M | - |

### Weekly Inflection Points

- `2026-W06`: Claude `221` entries across `29` sessions, Codex `1` thread
- `2026-W08`: Codex `110` threads and `738.7M` tracked tokens, Claude `21` entries
- `2026-W10`: Codex `53` threads and `717.0M` tracked tokens, Claude `12` entries
- `2026-W12`: Codex `7` threads and `16.5M` tracked tokens, Claude `1` entry

### Top Projects

**Codex**

| Project | Threads | Tokens |
| --- | ---: | ---: |
| VeraMint | 77 | 826.0M |
| repos root | 41 | 490.9M |
| stead-core | 10 | 431.4M |
| passepartout | 3 | 282.2M |
| Aegis | 1 | 245.3M |
| stead | 9 | 185.7M |

**Claude**

| Project | Entries |
| --- | ---: |
| Picalyze | 392 |
| VeraMint | 373 |
| qwer-digest | 228 |
| qwer-q | 145 |
| stead | 95 |
| Upstrio | 81 |

<details>
  <summary>More AI internals</summary>

  <br/>

  <strong>Codex agent role split</strong>

  | Role | Threads | Tokens |
  | --- | ---: | ---: |
  | main | 219 | 2279.9M |
  | worker | 24 | 597.6M |
  | explorer | 4 | 87.3M |
  | researcher | 2 | 12.3M |
  | convex_expert | 1 | 1.6M |
  | frontend_claude | 1 | 0.3M |

  <strong>Top Claude commands</strong>

  | Command | Count |
  | --- | ---: |
  | /resume | 63 |
  | /rewind | 53 |
  | /plugin | 50 |
  | /clear | 25 |
  | /compact | 23 |
  | /usage | 16 |
  | /export | 13 |
  | /rate-limit-options | 9 |

  <strong>Repo footprint</strong>

  - 64 GitHub repositories total
  - 19 public repositories
  - 45 private repositories
  - 29 repositories pushed in 2026 already
</details>

## Start Here

If you want a quick sample of what I build, start with:

- [aurora](https://github.com/edhor1608/aurora)
- [stead-core](https://github.com/edhor1608/stead-core)
- [stead](https://github.com/edhor1608/stead)
- [qwer-q](https://github.com/edhor1608/qwer-q)
- [passepartout](https://github.com/edhor1608/passepartout)
