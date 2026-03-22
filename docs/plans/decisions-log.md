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
