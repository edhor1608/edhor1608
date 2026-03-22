# Refresh AI Dashboard

Use this when the `AI Operations Dashboard` in the profile README needs a fresh snapshot.

## Script

Run:

```bash
python3 scripts/generate_ai_dashboard.py
```

The script reads:

- `~/.codex/state_5.sqlite`
- `~/.claude/history.jsonl`
- GitHub data via `gh`

It prints a paste-ready markdown block for the entire `## AI Operations Dashboard` section.

## Prompt

Use this prompt with Codex or Claude:

```md
Update the `AI Operations Dashboard` section in `/Users/jonas/repos/edhor1608/README.md`.

Rules:
- Do not change any other section.
- Replace only the content starting at `## AI Operations Dashboard` and ending right before `## Start Here`.
- Regenerate the dashboard from the local machine state by running:
  `python3 /Users/jonas/repos/edhor1608/scripts/generate_ai_dashboard.py`
- Keep the same overall structure unless the generated output requires a data-driven change.
- Preserve project naming used publicly in the profile, especially `VeraMint`.
- After updating the README, verify the generated numbers match the inserted markdown.
- If the dashboard shape changes, update `/Users/jonas/repos/edhor1608/docs/plans/decisions-log.md`.
```

## Manual Verification

After updating the README:

```bash
python3 scripts/generate_ai_dashboard.py
sed -n '/^## AI Operations Dashboard$/,/^## Start Here$/p' README.md
```

The numbers and tables should match.
