# Scripts

## Sync Adapter

Script: `scripts/sync-adapter.py`

Purpose:
Sync `profiles/<profile>.yml` selections into Claude Code + OpenCode config directories.

Command:
`python3 scripts/sync-adapter.py [profile] [target flags] [root overrides] [options]`

Example:
`python3 scripts/sync-adapter.py xapids --target both --claude-root ~/.claude --opencode-root ~/.config/opencode --dry-run`

Arguments:
- profile: `xapids` reads `profiles/xapids.yml`; installs `enabled: true`; prunes `enabled: false` (adapter-owned only).
- targets: `--target {both|claude|opencode}`
  - `both`: write to both roots
  - `claude`: write to `--claude-root` only
  - `opencode`: write to `--opencode-root` only
- roots: override destination roots
  - `--claude-root <path>` (default `~/.claude`)
  - `--opencode-root <path>` (default `~/.config/opencode`)
- options:
  - `--dry-run`: print plan; write nothing; do not update state.
  - `--no-prune`: install/update only; skip default pruning.

Mental Model:
- SSOT: `library/<author>/{agents,commands}/<id>.md`, `library/<author>/skills/<id>/...` (copy full skill dir).
- Targets:
  - Claude: `~/.claude/{agents,commands}/<id>.md`, `~/.claude/skills/<id>/...`
  - OpenCode: `~/.config/opencode/{agents,commands}/<id>.md`, `~/.config/opencode/skills/<id>/...`

Safety (hard rule):
Never modify or delete any destination path the adapter did not create.

Ownership:
- Tracked in `.sync-state-<user>.json`.
- Ownable paths: destination files (agents/commands) + destination dirs (skills); parent dirs are never owned.

Writes:
- dest missing: copy; record as owned.
- dest exists + owned: overwrite/update.
- dest exists + not owned: abort; user must rename/move/delete dest path or change tool id.

Prune (default on):
Delete only when BOTH are true:
1) tool is explicitly listed in the profile with `enabled: false`
2) corresponding destination path is owned

Duplicates:
If multiple profile entries in the same category share the same `id`: prompt user to fix ids to be unique; abort without changes.

## Update Profile

Scripts: `scripts/update-profile.sh`, `scripts/update-profile.py`

Purpose:
Refresh `profiles/<name>.yml` from `library/` while preserving user intent.

Architecture:
- Wrapper UX: `.sh` delegates to Python.
- Categories: `agents`, `skills`, `commands`, `mcp`, `extras`.
- Preserve intent: keep existing `enabled` by id; default new tools to `enabled: false`.
- Remove drift: drop tools removed from `library/`.
- Skills: prefer folder form `skills/<id>/SKILL.md`; back-compat for legacy flat `skills/<id>.md`.

## Generate Catalogue

Script: `scripts/gen-catalogue.sh`

Purpose:
Rewrite the `README.md` tool catalogue under `<!-- AUTO-GENERATED CATALOGUE -->`.

Architecture:
- Marker-based overwrite: preserve content above marker; regenerate catalogue below.
- Deterministic ordering: sort by tool id.
- Categories: `agents`, `skills`, `commands`, `mcp`, `extras`.
- Authors: scan `library/{shared,xapids,tihany7}/...` only.
- Skills: discover `skills/<id>/SKILL.md`; id is folder name.
- Ignore: dotfiles, `_private` docs, `.gitkeep`.

## Check Tools

Scripts: `scripts/check-tools.sh`, `scripts/check-tools.ps1`

Purpose:
Check required/optional CLIs; print install hints; optionally fail.

Architecture:
- Pure diagnostics: never installs.
- Portability: `command -v`; `uname -s` for OS hints.
- Tiers: required (git, gh, python3, pip, pyyaml) vs optional (rg, fzf, bat, yq, shellcheck, shfmt, claude, opencode).
- Strict mode: `--strict` exits non-zero if required items are missing.

## Install Required

Scripts: `scripts/install-required.sh`, `scripts/install-required.ps1`

Purpose:
Print install/upgrade commands for missing/outdated required dependencies; run nothing.

MacOS note:
(xapids suggestion) Install Homebrew first, install everything through homebrew. simplifies management and update processes. https://brew.sh/
