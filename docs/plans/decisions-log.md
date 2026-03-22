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
