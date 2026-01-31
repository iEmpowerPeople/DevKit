# Repo Library Scripts

## Overview

This directory contains utility scripts for managing the DevKit:
- **Sync workflows** - Deploy profiles to Claude/OpenCode configs
- **Profile management** - Update profiles from library changes
- **Catalogue generation** - Auto-generate README tool listings
- **Tool checking** - Validate dependencies and installations

## Library Scripts

The `library/{author}/scripts/` directories contain helper scripts used by commands and agents:
- `library/shared/scripts/` - Community scripts available to all
- `library/xapids/scripts/` - xapids-specific utilities
- `library/tihany7/scripts/` - tihany7-specific utilities

Scripts follow the naming convention: `{author}-{name}-script.{ext}`
- Example: `shared-example-script.py`, `tihany7-custom-script.sh`

### Declaring Dependencies

Commands and agents can declare their dependencies in YAML frontmatter:

```yaml
---
description: Command description
requires_extras: [git-cli, github-cli]
requires_scripts:
  - shared/scripts/shared-example-script.py
  - tihany7/scripts/tihany7-custom-script.sh
---
```

**Benefits:**
- Dependencies are automatically listed in profiles when running `devkit-update-profile`
- Users see exactly what extras and scripts are needed for each tool
- Makes it easy to audit and install required dependencies

### Dependency Types

1. **`requires_extras`** - List of extras from `library/*/extras/` (e.g., git-cli, github-cli)
2. **`requires_scripts`** - List of scripts from `library/{author}/scripts/`
   - Use relative paths: `shared/scripts/example.py` or `xapids/scripts/helper.sh`
   - Scripts are copied to user config during sync

### Example

```yaml
---
description: Example command with dependencies
    requires_extras: [git-cli]
requires_scripts:
  - shared/scripts/shared-example-script.py
  - tihany7/scripts/tihany7-example-script.sh
---
```

Profile output after `devkit-update-profile`:
```yaml
commands:
  - id: example-command
    author: tihany7
    enabled: true
requires_extras: [git-cli]
    requires_scripts:
      - shared/scripts/shared-example-script.py
      - tihany7/scripts/tihany7-example-script.sh
```

---

## Sync Adapter

Script: `repo-library/scripts/devkit-sync-adapter.py`

Purpose:
Sync `profiles/<profile>.yml` selections into Claude Code + OpenCode config directories.

Command:
`python3 repo-library/scripts/devkit-sync-adapter.py [profile] [target flags] [root overrides] [options]`

Example:
`python3 repo-library/scripts/devkit-sync-adapter.py xapids --target both --claude-root ~/.claude --opencode-root ~/.config/opencode --dry-run`

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

Enabled extras output:
- Prints install status for each enabled extra with `ok`, `missing`, or `outdated`.
- GUI extras are detected with OS-specific checks (app bundles, cask installs, or known paths).

Mental Model:
- SSOT: `library/<author>/{agents,commands}/<id>.md`, `library/<author>/skills/<id>/...` (copy full skill dir).
- Targets:
  - Claude: `~/.claude/{agents,commands}/<id>.md`, `~/.claude/skills/<id>/...`
  - OpenCode: `~/.config/opencode/{agents,commands}/<id>.md`, `~/.config/opencode/skills/<id>/...`

Safety (hard rule):
Never modify or delete any destination path the adapter did not create.

Ownership:
- Tracked in `.sync-state-<profile>.json`.
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

Scripts: `repo-library/scripts/devkit-update-profile.sh`, `repo-library/scripts/devkit-update-profile.py`

Purpose:
Refresh `profiles/<name>.yml` from `library/` while preserving user intent.

Architecture:
- Wrapper UX: `.sh` delegates to Python.
- Categories: `agents`, `skills`, `commands`, `mcp`, `extras`.
- Preserve intent: keep existing `enabled` by id; default new tools to `enabled: false`.
- Remove drift: drop tools removed from `library/`.
- Skills: prefer folder form `skills/<id>/SKILL.md`; back-compat for legacy flat `skills/<id>.md`.

## Generate Catalogue

Script: `repo-library/scripts/devkit-gen-catalogue.sh`

Purpose:
Rewrite the `README.md` tool catalogue under `<!-- AUTO-GENERATED CATALOGUE -->`.

Architecture:
- Marker-based overwrite: preserve content above marker; regenerate catalogue below.
- Deterministic ordering: sort by tool id.
- Categories: `agents`, `skills`, `commands`, `mcp`, `extras`.
- Authors: scan `library/{shared,xapids,tihany7}/...` only.
- Skills: discover `skills/<id>/SKILL.md`; id is folder name.
- Ignore: dotfiles, `_private` docs, `.gitkeep`.
- Output lists use HTML `<ul>`/`<li>` to keep spacing tight in previews; extras may be split into multiple lists by type.

## Check Tools

Script: `repo-library/scripts/devkit-check-tools.sh`

Purpose:
Check required/optional CLIs; print install hints; optionally fail.

Architecture:
- Pure diagnostics: never installs.
- Portability: `command -v`; `uname -s` for OS hints.
- Tiers: required (git, gh, python3, pip, pyyaml) vs optional (rg, fzf, bat, yq, shellcheck, shfmt, claude, opencode).
- Strict mode: `--strict` exits non-zero if required items are missing.

## Install Required

Script: `repo-library/scripts/devkit-install-required.sh`

Purpose:
Print install/upgrade commands for missing/outdated required dependencies; run nothing.

macOS note:
(xapids suggestion) Install Homebrew first, install everything through homebrew. simplifies management and update processes. https://brew.sh/
