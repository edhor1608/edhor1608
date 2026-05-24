# Refresh AI Dashboard

Use this when the `AI Operations Dashboard` in the profile README needs a fresh snapshot.

## Scripts

Refresh the dashboard block:

```bash
python3 scripts/generate_ai_dashboard.py
```

The script reads:

- `~/.codex/state_5.sqlite`
- `~/.claude/history.jsonl`
- `~/.pi/agent/sessions/**/*.jsonl`
- `~/.cursor/acp-sessions/*/meta.json`
- `~/.cursor/ai-tracking/ai-code-tracking.db`
- GitHub data via `gh`

It prints a paste-ready markdown block for the entire `## AI Operations Dashboard` section.

Refresh the wider profile fact audit:

```bash
python3 scripts/generate_profile_fact_audit.py > docs/profile-fact-audit-$(date +%F).md
```

That script combines:

- local dashboard telemetry from `scripts/generate_ai_dashboard.py`
- user-confirmed current tool status encoded in the script
- official OpenAI product context from release/docs pages

Check only the official OpenAI product context:

```bash
python3 scripts/fetch_openai_product_context.py
```

Check that the README still mentions the current workflow and does not drift back to stale tool claims:

```bash
python3 scripts/check_profile_claims.py
```

The claim checker covers:

- current role and single-person builder positioning
- public/private project activity
- linked project/site overview
- AI usage, tool choice, and stale-tool drift
- activity counters, trends, dashboard, and Markdown visual affordances

## Prompt

Use this prompt with Codex:

```md
Update the profile facts in `/Users/jonas/repos/edhor1608/README.md`.

Rules:
- Regenerate the dashboard from local machine state by running:
  `python3 /Users/jonas/repos/edhor1608/scripts/generate_ai_dashboard.py`
- Regenerate the wider fact audit by running:
  `python3 /Users/jonas/repos/edhor1608/scripts/generate_profile_fact_audit.py > /Users/jonas/repos/edhor1608/docs/profile-fact-audit-$(date +%F).md`
- Verify current workflow claims by running:
  `python3 /Users/jonas/repos/edhor1608/scripts/check_profile_claims.py`
- Replace the README dashboard only if dashboard numbers changed meaningfully.
- Keep the first-screen role clear: software engineer at vivenu plus active private/public builder.
- Keep the current tool framing: Codex App default, Pi raw/custom, GPT Image for UI, Cursor Pro for editor AI and Claude access, standalone Claude historical, Opencode Go historical.
- Keep the same overall README structure unless generated output requires a data-driven change.
- Preserve project naming used publicly in the profile, especially `VeraMint`.
- After updating the README, verify the generated numbers match the inserted markdown.
- If the dashboard shape changes, update `/Users/jonas/repos/edhor1608/docs/plans/decisions-log.md`.
```

## Manual Verification

After updating the README:

```bash
python3 scripts/generate_ai_dashboard.py
python3 scripts/generate_profile_fact_audit.py
python3 scripts/check_profile_claims.py
sed -n '/^## AI Operations Dashboard$/,/^## Connect$/p' README.md
```

The numbers and tables should match.
