---
description: Sync enabled tools from profile to Claude/OpenCode configs
requires_extras: "`git-cli`"
---

# Sync DevKit Profile to Configs

Sync your enabled tools from `profiles/{profile}.yml` to Claude Code and OpenCode configuration directories.

## Quick Reference

```bash
# Dry run (preview changes)
python3 repo-library/scripts/devkit-sync-adapter.py {profile} --dry-run

# Sync to both Claude and OpenCode
python3 repo-library/scripts/devkit-sync-adapter.py {profile} --target both

# Sync to Claude only
python3 repo-library/scripts/devkit-sync-adapter.py {profile} --target claude

# Sync to OpenCode only
python3 repo-library/scripts/devkit-sync-adapter.py {profile} --target opencode
```

## Workflow

### 1. Check Current State

Before syncing, verify:
```bash
git status                           # Working directory clean?
cat profiles/{profile}.yml           # Review enabled tools
```

### 2. Dry Run First

Always preview changes before syncing:
```bash
python3 repo-library/scripts/devkit-sync-adapter.py {profile} --dry-run
```

Review output:
- Files to be **installed** (enabled: true)
- Files to be **pruned** (enabled: false, previously synced)
- Any **conflicts** or **ownership issues**

### 3. Execute Sync

```bash
python3 repo-library/scripts/devkit-sync-adapter.py {profile} --target both
```

### 4. Verify

Check destination directories:
```bash
ls ~/.claude/commands/
ls ~/.claude/agents/
ls ~/.config/opencode/commands/
ls ~/.config/opencode/agents/
```

## Command Options

| Flag | Description |
|------|-------------|
| `--target {both\|claude\|opencode}` | Choose destination(s) |
| `--claude-root <path>` | Override Claude root (default: `~/.claude`) |
| `--opencode-root <path>` | Override OpenCode root (default: `~/.config/opencode`) |
| `--dry-run` | Preview changes without writing |
| `--no-prune` | Install/update only, skip pruning disabled tools |

## Examples

**Sync xapids profile to both:**
```bash
python3 repo-library/scripts/devkit-sync-adapter.py xapids --target both
```

**Preview tihany7 sync to Claude only:**
```bash
python3 repo-library/scripts/devkit-sync-adapter.py tihany7 --target claude --dry-run
```

**Custom roots:**
```bash
python3 repo-library/scripts/devkit-sync-adapter.py xapids \
  --target both \
  --claude-root ~/custom/.claude \
  --opencode-root ~/custom/.config/opencode
```

## How It Works

1. **Reads** `profiles/{profile}.yml`
2. **Installs** tools with `enabled: true` to destination dirs
3. **Prunes** tools with `enabled: false` (only if previously synced by adapter)
4. **Tracks** ownership in `.sync-state-{profile}.json`

## Safety Rules

- Never modifies files the adapter didn't create
- Tracks ownership to prevent conflicts
- Aborts on duplicate IDs in same category
- Preserves user-created files in destination dirs

## Troubleshooting

**Conflict: destination exists but not owned**
- File exists in destination but wasn't created by sync
- Resolution: rename/move/delete the conflicting file, or change tool ID

**Duplicate IDs detected**
- Multiple tools in same category have same ID
- Resolution: rename one of the tools to have unique ID

## Related Commands

- `/devkit-add-tool` - Add new tools to library
- `/devkit-gitgh` - Commit and PR workflow
