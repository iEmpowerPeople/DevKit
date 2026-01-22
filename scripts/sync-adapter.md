# Profile Sync Adapter (Claude + OpenCode)

## Goal
Sync exactly the tools selected in a single local profile into both runtime directories:
- Claude Code loads from `~/.claude/{agents,commands,skills}`
- OpenCode loads from `~/.config/opencode/{agents,commands,skills}`

Repo is SSOT; profile is the filter.

## Source Layout (SSOT)
- Agents: `library/<author>/agents/<id>.md`
- Commands: `library/<author>/commands/<id>.md`
- Skills: `library/<author>/skills/<id>/` (directory; copy entire folder, not just `SKILL.md`)

## Selection
Profile file: `profiles/<profile>.yml`
- For each category (`agents`, `commands`, `skills`), sync only entries with `enabled: true`.
- Entries with `enabled: false` are prune candidates.

## Targets
For each enabled tool:
- Claude
  - Agent: `~/.claude/agents/<id>.md`
  - Command: `~/.claude/commands/<id>.md`
  - Skill: `~/.claude/skills/<id>/...`
- OpenCode
  - Agent: `~/.config/opencode/agents/<id>.md`
  - Command: `~/.config/opencode/commands/<id>.md`
  - Skill: `~/.config/opencode/skills/<id>/...`

## Safety Invariant (Hard Rule)
Never modify or delete any destination path the adapter did not create.

Rationale: users may manage other files in these folders manually or via other tooling; the adapter must be non-destructive outside its own footprint.

## Ownership Model
Ownership is tracked in a local state file (gitignored): `.sync-state-<user>.json`.
- Parent directories are never "owned" (e.g. `~/.claude/agents/`, `~/.config/opencode/skills/`).
- Only the concrete paths the adapter writes are ownable (destination file paths for agents/commands; destination directory paths for skills).
- A destination path is "owned" iff its exact path is recorded in state.
- Adapter actions are restricted to owned paths.

## Sync Rules (Writes)
- If destination path does not exist: copy; record destination path as owned.
- If destination path exists and is owned: overwrite/update in place.
- If destination path exists and is not owned: do not touch; prompt user with remediation (rename/move existing destination path or change `id`), then abort.

## Prune Rules (Deletes)
Prune is on by default.

Delete only when BOTH are true:
1) tool is explicitly listed in the profile with `enabled: false`
2) corresponding destination path is owned (present in state)

If profile says `enabled: false` but destination is not owned: do nothing (no prompt required; optional note).

## Duplicate IDs (Interactive)
If multiple profile entries in the same category share the same `id`:
- Do not guess or merge.
- Prompt user to fix the repo/profile so ids become unique.
- Abort the run without changes; re-run after fixing.

## macOS + Windows
Python 3 + `pathlib`/`shutil`; OS-agnostic.
- Defaults assume:
  - Claude: `~/.claude`
  - OpenCode: `~/.config/opencode`
- If locations differ, override:
  - `--claude-root <path>`
  - `--opencode-root <path>`
