# Decisions Log

## 2026-03-22 - Profile README positioning

### Context

The initial profile README was too generic. The goal was to make the GitHub profile communicate more signal about shipped systems, private product work, AI-native workflow, and actual operating scale.

### Decision

Structure the profile in this order:

1. Shipped and active systems
2. AI-native operator workflow
3. Hard activity signals and metrics

Private projects may be named publicly, but their source remains closed.

### Rationale

- Project-first framing gives the strongest credibility signal
- Workflow details differentiate the profile from generic portfolio pages
- Metrics add proof, but should support the narrative instead of replacing it
- Naming private systems is acceptable here because the constraint is code/IP protection, not anonymity

### Consequences

- The README will contain time-bound metrics that may need periodic updates
- Private systems become part of the public narrative even though the code remains closed
- Future iterations may automate metric refresh if the static snapshot becomes stale

## 2026-03-22 - AI usage section presentation

### Context

The first metrics section was too flat. The goal was to show AI usage in a way that felt visual, specific, and operational without turning the README into a noisy telemetry dump.

### Decision

Use a hybrid layout for the AI section:

1. Summary cards for Codex, Claude, and GitHub
2. Exact month-by-month table
3. Visual monthly load block
4. Project breakdown tables
5. Expandable deeper internals for roles, commands, and repo footprint

### Rationale

- Summary cards make the scale readable at a glance
- Monthly tables provide exact numbers and prevent the visuals from feeling vague
- The load block adds visual texture without relying on external images or badges
- Collapsible details let the profile show depth without overwhelming first-pass readers

### Consequences

- The section is denser and may need future trimming after real-world viewing
- Static bars and month snapshots will become stale without automation
- The README now doubles as both profile copy and a lightweight operations dashboard

## 2026-03-22 - AI dashboard refresh workflow

### Context

The profile now contains machine-derived AI and GitHub metrics. Updating those numbers by hand is error-prone and makes the dashboard stale quickly.

### Decision

Add:

1. `scripts/generate_ai_dashboard.py` to regenerate the markdown block for the full `AI Operations Dashboard` section
2. `docs/refresh-ai-dashboard.md` with a reusable prompt and manual verification steps

### Rationale

- One script keeps the dashboard numbers reproducible from local machine state
- A dedicated prompt file makes it easy to hand the refresh task to Codex or Claude
- Generating the whole section avoids partial edits and drift between tables, bars, and summary cards

### Consequences

- The workflow now depends on local Codex/Claude data files and authenticated `gh`
- GitHub metrics can move during the same day, so reruns may change totals without any repo edits
- Future automation can wire this script directly into a README refresh command if needed

## 2026-03-22 - Usable shipped work definition

### Context

The earlier shipped section mixed recent implementation work with projects that were not directly usable or viewable by a visitor.

### Decision

Define that section as:

1. live public sites
2. public projects that are clearly runnable from the repo, package, container, or quick-start path

Rename the section to `Live And Runnable Now`.

### Rationale

- This keeps the claim honest and visitor-centered
- It removes ambiguous “shipped” language for work that is only recently touched
- It gives readers a direct path to try or inspect the work immediately

### Consequences

- Private but shipped work no longer appears in that section unless it is publicly accessible
- The section may need periodic review as more projects gain or lose live surfaces

## 2026-03-22 - Evidence-based AI workflow analysis

### Context

The `AI-Native Operator` section should be grounded in observed usage patterns, not just plausible branding language.

### Decision

Add:

1. `scripts/analyze_ai_workflow.py` to extract workflow evidence from local Codex and Claude artifacts plus GitHub contribution history
2. `docs/ai-workflow-analysis.md` as the generated analysis report

The report should separate direct findings from interpretation and explicitly track time evolution.

### Rationale

- This creates an audit trail for future profile wording changes
- It makes the AI/workflow section defensible line by line
- It captures a more important signal than raw counts alone: how the workflow changed over weeks

### Consequences

- The analysis depends on private local telemetry and is not meant for direct publication
- Some findings are heuristic because keyword pattern matching is approximate
- Future rewrites of the profile should cite this report rather than restating assumptions

## 2026-03-22 - Time-aware rewrite of AI operator section

### Context

The earlier `AI-Native Operator` text was directionally right but too generic. It needed to reflect not just what tools are used, but how the workflow actually behaves and how it changed over early 2026.

### Decision

Rewrite the section to emphasize:

1. planning, review, bugfix, docs, testing, research, frontend, and worktree usage as observed workflow signals
2. differentiated roles for Codex and Claude
3. the time shift from Claude-heavy exploration into Codex-heavy delivery

### Rationale

- This keeps the branding language but grounds it in observable evidence
- The time dimension explains more than raw usage counts alone
- The rewritten section is more useful because it describes the operating model instead of just listing tools

### Consequences

- The section is longer and may need a later trimming pass
- Specific numbers inside the prose can go stale and may need refresh alongside the dashboard

## 2026-03-22 - Deep AI telemetry pass for README wording

### Context

The next profile pass needed a higher bar than aggregate counts. The goal was to ground the public wording in week-level change, monthly signal shifts, and at least one code-retention source rather than only session totals.

### Decision

Expand the local analysis to include:

1. monthly signal-shape tables for Codex and Claude
2. explicit week-level inflection points for the shift from Claude-heavy exploration to Codex-heavy delivery
3. a smaller `git-ai` prompt sample to measure tracked code retention separately from raw session volume

Use those results to rewrite the public `AI-Native Operator` section and add compact weekly inflection bullets to the dashboard.

### Rationale

- Week-level inflection points explain the workflow shift more clearly than monthly totals alone
- Signal-shape tables reveal what the AI was used for, not just how much it was used
- `git-ai` adds a useful second lens: whether tracked AI-assisted code tends to survive in git

### Consequences

- The local analysis artifact became more useful for future rewrites, but also more sensitive and therefore should remain local-only
- The public README now makes stronger claims with better evidence behind them
- The dashboard has slightly more density, so future passes may need a trim after live review

## 2026-03-22 - Include harness footprint in AI workflow analysis

### Context

The session-level analysis captured Codex and Claude well, but it missed an important part of the setup: the machine and repos also show real usage or experimentation with other harnesses such as Opencode, Cursor, Windsurf, T3, and repo-level bridge workflows.

### Decision

Expand the local analysis to track:

1. home-level harness footprints
2. repo-level harness config spread
3. local `t3` state counts
4. dedicated multi-harness bridge artifacts such as the `stead-core-live-m13-opencode` workspace

Reflect only the strongest part publicly: that the workflow is multi-harness, while keeping the denser breakdown local-only.

### Rationale

- This distinguishes actual harness usage from merely mentioning other tools in chats
- The README benefits from one concise public signal, but the detailed harness inventory would be too much for the profile page
- The local report becomes a better source of truth for future iterations

### Consequences

- The analyzer script now covers a wider operational surface than just Codex and Claude logs
- The public profile can mention multi-harness usage without overstating any specific third-party tool
- The detailed harness spread remains private context instead of public profile copy

## 2026-05-24 - Add Pi and Cursor to profile dashboard

### Context

The profile dashboard only covered Codex, Claude, and GitHub. That made the public operating snapshot stale because current workflow now includes Pi with `pi-tools` and Cursor activity.

### Decision

Extend `scripts/generate_ai_dashboard.py` to include:

1. Pi sessions, message entries, project counts, monthly sessions, top projects, and model events from `~/.pi/agent/sessions/**/*.jsonl`
2. Cursor ACP sessions, workdirs, monthly sessions, top workdirs, AI code hashes, conversation summaries, and code-hash models from `~/.cursor`
3. A wider monthly dashboard table and extra top-project/internal sections for Pi and Cursor

### Rationale

- The dashboard should reflect the tools currently in use, not just the older Codex/Claude split
- Pi session JSONL files provide enough structured data for sessions, projects, months, and model usage
- Cursor's most reliable local footprint is ACP metadata plus the AI code tracking database, so the dashboard names those metrics explicitly instead of pretending they are full chat counts

### Consequences

- The dashboard is wider and denser, especially in the monthly load block
- Cursor ACP session counts are much larger than human-visible chat counts and need to stay labeled as ACP sessions
- Refreshes now depend on additional local Pi and Cursor paths, but missing paths degrade to zero instead of failing

## 2026-05-24 - Make profile claims evidence-first

### Context

The profile copy still mixed current facts, older March-era claims, and interpretive positioning. Project priorities and tool usage had changed enough that the README needed a full evidence pass rather than another partial stats refresh.

### Decision

Add `docs/profile-fact-audit-2026-05-24.md` and rewrite the public profile around facts from:

1. GitHub push recency
2. Codex project, model, signal, and token data
3. Claude history and transcript volume
4. Pi sessions and `pi-tools` activity
5. Cursor ACP and AI-code-tracking footprint
6. installed local agent skills

### Rationale

- Public project priority should be anchored in recent repo activity and local AI-session load
- The "how" section should state observed patterns instead of generic AI-native positioning
- Cursor data is too noisy for project priority, so it should be explicitly labeled as footprint data
- Claude remains historically important, but current copy should reflect lower recent volume

### Consequences

- The README is more data-heavy but less likely to overstate current usage
- Future edits should update the fact audit or rerun the relevant scripts before changing project priorities
- Some claims are now deliberately narrower, especially around skills and Cursor

## 2026-05-24 - Separate current subscriptions from historical tool telemetry

### Context

The README includes historical Claude and Opencode telemetry, but the current paid/default tool setup changed: the Claude subscription is cancelled, Cursor Pro is active, and Opencode Go is no longer part of the setup.

### Decision

Keep historical telemetry visible, but label current status explicitly:

1. `Claude` remains historical usage evidence, not an active subscription lane
2. `Cursor Pro` is the active editor-side AI tier
3. `Opencode Go` is historical footprint only, not current setup

### Rationale

- Subscription status is user-confirmed current context and outranks passive install traces
- Historical telemetry is still useful, but should not imply active usage
- Public profile wording should distinguish tool footprint from current operating choices

### Consequences

- The top README badges and setup bullets now match the current tool stack
- Future dashboard refreshes can keep old telemetry, as long as current-status wording stays explicit

## 2026-05-24 - Explain tool choice by workflow fit

### Context

The README had current tool stats, but not the practical selection logic: Codex App is the main lane because it is stable and improving quickly, Pi is for raw/custom harness work, GPT Image is used for UI/visual work, and Claude is now only accessed through Cursor.

### Decision

Describe the current workflow by when each tool is used:

1. `Codex App` is the default for most work, backed by local usage volume and current OpenAI release notes for Goal mode, Appshots, mobile remote access, browser annotations, and locked/remote use
2. `Pi` is for cleaner/rawer agent work or custom `pi-tools` behavior, but currently lower-volume
3. `GPT Image` is the UI/visual lane
4. `Cursor Pro` is the editor-side AI tier and current Claude access path

### Rationale

- The profile should explain operating choices, not just list installed tools
- Official changelog context supports mentioning why Codex App is attractive now
- User-confirmed workflow intent should guide public copy where passive telemetry cannot show motivation

### Consequences

- README wording now distinguishes default execution, custom-harness work, UI/image work, editor AI, and historical telemetry
- Future profile refreshes should keep motivation separate from measured local usage

## 2026-05-24 - Add reusable profile fact scripts

### Context

The README now depends on multiple evidence types: local AI telemetry, user-confirmed subscription/tool status, GitHub activity, and official OpenAI product changes. Keeping those claims accurate manually is fragile.

### Decision

Add scripts that separate the evidence checks:

1. `scripts/fetch_openai_product_context.py` checks official OpenAI release/docs pages for Codex and GPT Image context
2. `scripts/generate_profile_fact_audit.py` generates a reusable profile fact audit from local telemetry, current setup, and product context
3. `scripts/check_profile_claims.py` verifies the README still contains the current workflow claims and does not drift back to stale tool claims

### Rationale

- The dashboard script covers numbers, but not current tool-choice semantics
- OpenAI product facts change, so the Codex/GPT Image context should be checked from official sources
- Current subscription/tool status is user-confirmed and should be made explicit in one repeatable audit path

### Consequences

- Future README refreshes can run a small fact pipeline before editing public claims
- The claim checker is intentionally narrow and should be updated whenever the desired public workflow story changes

## 2026-05-24 - Make first-screen profile purpose explicit

### Context

The README covered projects, AI workflow, tooling, telemetry, and links, but the current professional anchor was too implicit. For an unknown individual profile, the first screen needs to state the current role clearly before asking readers to parse dashboards.

### Decision

Add the current role to the opening line and add a compact profile map:

1. visible `Software engineer at vivenu` link near the top
2. a small table that tells readers where to find what is built, how it is built, how much AI is involved, and why those tools are used
3. claim-check coverage so the role, profile map, activity overview, AI telemetry, links, and Markdown visual affordances do not disappear in future edits

### Rationale

- The profile should work for readers with no prior context
- The role gives a fast credibility anchor while the rest of the README proves private activity and AI-heavy workflow
- The table is a useful Markdown visual without adding decorative noise

### Consequences

- The first viewport now answers who, current professional context, what is being built, and where the evidence lives
- Future claim checks include role clarity, not just AI tool status

## 2026-05-25 - Trim profile into a compact public read

### Context

The README had become fact-rich but too long and visually noisy. The reference profiles from `steipete`, `t3dotgg`, `jonschlinkert`, `juliusmarminge`, and `c-ehrlich` show a stronger pattern: clear identity, short project overview, concise links, and only enough detail to prove the point.

### Decision

Reduce the visible README from a long evidence dump into:

1. a short identity and link block
2. a `Start Here` proof table
3. compact `Current Work` and `How I Build` tables
4. a compact `AI Snapshot` with three months of trend data
5. one collapsed evidence section for the heavier claims

### Rationale

- The profile should be readable by someone who has no context and only scans the first screen
- Detailed telemetry is useful, but it belongs behind a compact snapshot or in audit docs
- The scripts can preserve evidence without forcing the README to display every table

### Consequences

- The README is now much shorter and closer to the referenced profiles' density
- `scripts/generate_ai_dashboard.py` now supports `--style compact` for the public snapshot
- The claim checker now verifies the compact structure rather than the previous long-section names

## 2026-05-25 - Add LinkedIn as a professional profile link

### Context

The public GitHub sidebar already includes a LinkedIn profile URL, and the user confirmed LinkedIn can be used for additional professional context. The LinkedIn page itself is mostly behind an auth wall when checked anonymously, so it should not be mined for detailed claims.

### Decision

Add the public LinkedIn URL to the top link row and `Connect` badges, and make the claim checker require that link.

### Rationale

- LinkedIn is useful as a professional context link without increasing README content length
- Auth-walled LinkedIn details are weaker evidence than the user-confirmed README/fact-audit data
- Keeping it as a link supports discoverability while preserving the cleaned-up profile structure

### Consequences

- Readers now get a direct professional-profile link alongside website, GitHub, and X
- Future profile checks will fail if the LinkedIn link is accidentally removed

## 2026-05-25 - Replace Start Here with a real hook

### Context

The compact `Start Here` table was orderly, but it still read like a stats index. The first section needs to be a catch: explain what the profile is trying to show, then use numbers only when they support that claim.

### Decision

Replace `Start Here` with `Now`:

1. lead with the current work/private-builder/AI-operating-model claim
2. keep only the stats that explain active building, AI usage, and tool preference
3. update the claim checker to require the hook rather than the old section title

### Rationale

- Stats are only useful when they support a point the reader already understands
- The hook should make the AI angle clearer without making the profile longer
- The table can stay, but its labels need to answer "why should I care?"

### Consequences

- The first section now reads more like positioning and less like a dashboard table
- Future checks guard for the hook, not the old `Start Here` wording

## 2026-03-22 - Prioritize user-confirmed current setup over passive footprint data

### Context

The local machine and repo scan can detect installs, config files, and old bridge artifacts for tools like Opencode, Cursor, Windsurf, and T3. That is useful context, but it can drift away from the actual current workflow.

### Decision

For public-facing wording, prefer the user-confirmed current setup:

1. `Codex` via `GPT-5.4`, mainly through the CLI, with the Codex app also in use
2. `Claude Code` with `Opus 4.6` and the frontend-design skill for UI work
3. `T3` as something being tested, but not yet stable enough to count as a default lane
4. do not present `Gemini` or `Opencode` as active current usage based only on passive telemetry or old prompt samples

### Rationale

- Direct user confirmation is higher quality than inferring current preference from install traces
- Public profile text should describe the current setup, not just the machine's historical surface area
- The local analysis can still keep weaker signals, as long as they are labeled correctly

### Consequences

- The README now reflects the current tool split more accurately
- The local analyzer keeps harness data, but explicitly labels it as footprint rather than primary usage
- Future profile edits should separate current setup from historical or experimental tooling

## 2026-03-22 - Add a compareable curated-builder top section

### Context

The `steipete` profile comparison showed a stronger top-of-page structure: fast identity, current focus, curated links, and proof of motion before the longer detail sections. Instead of replacing the whole README immediately, the goal was to compare that direction live against the current structure.

### Decision

Add an experimental top block above the existing README with:

1. a compact identity statement
2. current-focus projects
3. current AI setup
4. live and runnable links
5. proof-of-motion metrics

Keep the existing longer structure underneath, separated by a divider, so the two directions can be compared visually on the live profile.

### Rationale

- This creates a real A/B comparison instead of debating structure abstractly
- The curated-builder direction is strongest when seen at the very top of the profile
- Keeping the older version below avoids losing useful detail too early

### Consequences

- The profile is temporarily redundant by design
- The next pass should remove one of the two directions after comparison
- Feedback can now focus on structure and scannability rather than imagined diffs

## 2026-03-22 - Merge the curated-builder top into the main README

### Context

After comparing the two structures live, the top section was clearly stronger: faster identity, current focus up front, and a more scannable first screen. The next step was to merge that direction into the main README while keeping the AI/dashboard material intact.

### Decision

Restructure the README to:

1. use a stronger header with a badge row
2. keep the curated `Current focus` section at the top
3. convert `Systems I Ship, Build, And Explore` from a dense table into the same bullet-driven style
4. remove `Live And Runnable Now`
5. replace `What I Optimize For` with `What I'm Doing`
6. remove `Start Here`
7. add a `Connect` block with real public links

### Rationale

- This keeps the strongest top-of-page structure from the comparison pass
- The bullet style is easier to scan than the earlier table for this kind of mixed public/private project list
- The README now reads more like a live builder profile and less like a static inventory

### Consequences

- The profile is now structurally closer to the steipete-inspired direction
- The AI and dashboard sections remain intact, so depth is preserved below the fold
- Future refinements should now focus on copy polish and section trimming rather than major structure changes
