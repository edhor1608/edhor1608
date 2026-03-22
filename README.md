# Jonas Rohde

I build products, infrastructure, and AI-native delivery systems.

This profile shows the systems I work on, what they do, and how I operate across public and private projects.

## Systems I Ship, Build, And Explore

| Project | State | What it is | Stack | Code |
| --- | --- | --- | --- | --- |
| VeraMint | active | Mobile news app focused on human-curated journalism, offline-first reading, and media literacy | Expo, React Native, TypeScript, Convex | private |
| [qwer-q](https://github.com/edhor1608/qwer-q) | active | Typed, docker-first message queue with schema registry, durability, and a built-in dashboard | Go, BadgerDB, Docker | public |
| [stead-core](https://github.com/edhor1608/stead-core) | active | Vendor-neutral session standard and interop layer for Codex and Claude Code | TypeScript | public |
| [stead](https://github.com/edhor1608/stead) | active | Workspace orchestrator for terminals, ports, and context | TypeScript | public |
| [aurora](https://github.com/edhor1608/aurora) | active | European community platform with a Convex-first realtime core | TypeScript, React, Convex | public |
| [passepartout](https://github.com/edhor1608/passepartout) | shipped | Photography-first export tool for framed image output and social-ready formats | TypeScript | public |
| edhor-me | active | Personal site and portfolio with an AI-powered ask-me flow | Astro, Tailwind, Playwright, Vercel AI SDK | private |
| Picalyze | active | Photography analysis platform for uploading, analyzing, and exploring photo insights | TypeScript, web app stack, third-party photo integrations | private |
| Thinking Loop | active | Deep research and idea-convergence workflow built around iterative agent loops | shell, AI workflows, session tooling | private |
| Fair Creator | active | Transparency-first platform for creator-contractor relationships and fair work standards | TypeScript, TanStack, data pipeline, moderation workflows | private |
| Image Provenance | planning | Verifiable image authenticity that survives social media distribution | Rust, watermarking, distributed registry | private |
| Upstrio | concept | European streaming platform exploring fair economics and distributed infrastructure | architecture, market design, distributed systems | private |

## Recent Shipped Work

- VeraMint: pushed the Expo 55 upgrade, audio migration, and release-gating work for mobile delivery
- aurora: shipped auth/session baseline work and permissioned text flow core
- qwer-q: shipped a typed queue with schema registry, durability, metrics, and an embedded dashboard
- Picalyze: improved third-party integration error handling, health checks, and asset sync tracking
- edhor-me: built the portfolio site around Astro, Playwright, and an AI-powered ask-me interface

## What I Optimize For

- Shipping real systems, not demo repos
- Small diffs, clear ownership, and boring code that stays easy to change
- Planning before implementation and verifying through checks, tests, and review
- Treating AI as an execution multiplier, not a replacement for engineering judgment

## AI-Native Operator

I work in an AI-heavy loop, but with structure:

- plan first, then cut work into small PR-sized changes
- use `Codex` and `Claude` as active implementation and review partners
- run parallel work through `git worktree`, branch isolation, and agent loops
- keep a bias toward `gh`, PR review, automation, and repeatable delivery workflows
- document decisions, keep project knowledge in-repo, and avoid hidden context

### Tools I Actually Use

- AI: Codex, Claude
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
      1,995 contributions<br/>
      183 PR contributions<br/>
      1,529 private contributions
    </td>
  </tr>
</table>

### Monthly View

| Month | GitHub Contributions | Codex Threads | Codex Tokens | Claude Entries |
| --- | ---: | ---: | ---: | ---: |
| 2026-03 | 36 | 76 | 1216.6M | 14 |
| 2026-02 | 598 | 143 | 1732.7M | 482 |
| 2026-01 | 634 | 15 | 1.1M | 1512 |
| 2025-12 | 37 | 10 | 3.7M | - |
| 2025-11 | 93 | 2 | 3.9M | - |
| 2025-10 | 69 | 3 | 17.7M | - |
| 2025-09 | 84 | 2 | 2.9M | - |

### Monthly Load

```text
2026-03  GH  36  |#...................|  Codex  76 threads |###########.........|  Tokens 1216.6M |##############......|  Claude  14 |#...................|
2026-02  GH 598  |###################.|  Codex 143 threads |####################|  Tokens 1732.7M |####################|  Claude 482 |######..............|
2026-01  GH 634  |####################|  Codex  15 threads |##..................|  Tokens    1.1M |#...................|  Claude 1512|####################|
```

### Top Projects

**Codex**

| Project | Threads | Tokens |
| --- | ---: | ---: |
| VeraMint | 77 | 826.0M |
| repos root | 41 | 490.6M |
| stead-core | 10 | 431.4M |
| passepartout | 3 | 282.2M |
| Aegis | 1 | 245.3M |
| stead | 9 | 185.7M |

**Claude**

| Project | Entries |
| --- | ---: |
| picalyze | 392 |
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
  | main | 219 | 2279.6M |
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
