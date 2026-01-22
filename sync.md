# Sync Guide

How to set up selective syncing with DevKit-Claude that remembers your choices.

## Overview

This guide helps you create a sync system that:
- Lets you choose which config files to sync to your `~/.claude/`
- **Automatically adapts** the repo's author-based structure to `~/.claude/`'s type-based structure
- Syncs files to their proper locations (commands/, skills/, agents/, etc.)
- Remembers your previous choices
- Works interactively in natural language
- Updates automatically when you pull from the repo

## Repository vs. ~/.claude/ Structure

**DevKit-Claude** organizes files by **authorship** (who owns/maintains them):
```
DevKit-Claude/
├── shared/
│   ├── commands/
│   ├── skills/
│   └── agents/
├── xapids/
│   ├── commands/
│   ├── skills/
│   └── agents/
└── tihany7/
    ├── commands/
    ├── skills/
    └── agents/
```

**~/.claude/** organizes files by **type** (what they are):
```
~/.claude/
├── commands/           # All commands from all authors
├── skills/             # All skills from all authors
└── agents/             # All agents from all authors
```

**The sync script automates this adaptation.** 
- Files declare their destination using headers, and the script copies them from the author-based repo structure (e.g., `xapids/skills/my-skill.md`) to the appropriate type-based `~/.claude/` subdirectory (e.g., `~/.claude/skills/my-skill.md`).

## Setup

### Step 1: Create Your Sync State File

```bash
cd ~/GitHub/iEmpowerPeople/DevKit-Claude
touch .sync-state-$(whoami).json
```

This file remembers which configs you want synced.

### Step 2: Create the Sync Script

Create `sync-interactive.sh`:

```bash
#!/bin/bash
# Interactive sync script with memory

USER=${1:-$(whoami)}
STATE_FILE=".sync-state-${USER}.json"
CLAUDE_DIR=~/.claude

# Initialize state file if it doesn't exist
if [[ ! -f "$STATE_FILE" ]]; then
    echo "{}" > "$STATE_FILE"
fi

echo "DevKit-Claude Interactive Sync for: $USER"
echo "=========================================="
echo ""

# Function to check if file is enabled
is_enabled() {
    local file=$1
    jq -r ".\"$file\" // \"ask\"" "$STATE_FILE"
}

# Function to update state
update_state() {
    local file=$1
    local value=$2
    jq ". + {\"$file\": $value}" "$STATE_FILE" > "${STATE_FILE}.tmp"
    mv "${STATE_FILE}.tmp" "$STATE_FILE"
}

# Function to determine destination from file
get_destination() {
    local file=$1
    local filename=$(basename "$file")

    # Check for destination header in file
    local dest=$(head -5 "$file" | grep -E "^# Destination:|^<!-- Destination:" | sed 's/.*: *//' | tr -d ' >')

    if [[ -n "$dest" ]]; then
        echo "$CLAUDE_DIR/$dest/$filename"
    else
        # Default to root if no destination specified
        echo "$CLAUDE_DIR/$filename"
    fi
}

# Find all .md files (except README and sync.md)
files=$(find shared xandru friend -name "*.md" 2>/dev/null | sort)

# Interactive selection
for file in $files; do
    current=$(is_enabled "$file")
    dest=$(get_destination "$file")

    if [[ "$current" == "true" ]]; then
        echo "✓ Currently enabled: $file"
        echo "  → Syncs to: $dest"
        read -p "  Keep it? (y/n/skip): " answer
        case $answer in
            n|N) update_state "$file" false ;;
            s|S) continue ;;
            *) update_state "$file" true ;;
        esac
    elif [[ "$current" == "false" ]]; then
        echo "✗ Currently disabled: $file"
        echo "  → Would sync to: $dest"
        read -p "  Enable it? (y/n/skip): " answer
        case $answer in
            y|Y) update_state "$file" true ;;
            s|S) continue ;;
            *) update_state "$file" false ;;
        esac
    else
        # First time seeing this file
        echo "? New file found: $file"
        echo "  → Would sync to: $dest"
        read -p "  Include in your config? (y/n): " answer
        case $answer in
            y|Y) update_state "$file" true ;;
            *) update_state "$file" false ;;
        esac
    fi
    echo ""
done

# Sync enabled files
echo "Syncing files..."
mkdir -p "$CLAUDE_DIR"

for file in $files; do
    if [[ $(is_enabled "$file") == "true" ]]; then
        dest=$(get_destination "$file")
        dest_dir=$(dirname "$dest")

        mkdir -p "$dest_dir"
        cp "$file" "$dest"
        echo "  ✓ Synced: $file → $dest"
    fi
done

echo ""
echo "✅ Sync complete!"
echo "Your preferences saved in: $STATE_FILE"
```

Make it executable:

```bash
chmod +x sync-interactive.sh
```

### Step 3: Add Destination Headers to Your Files

Each config file should specify where it goes. Add this as the first line:

**For skills:**
```markdown
# Destination: skills

# My Custom Skill
...
```

**For agents:**
```markdown
# Destination: agents

# My Custom Agent
...
```

**For commands:**
```markdown
# Destination: commands

# My Custom Command
...
```

**For root ~/.claude/ files:**
```markdown
# Destination: .

# Global Config
...
```

### Step 4: Run Your First Sync

```bash
./sync-interactive.sh
```

You'll be asked about each config file:
- **New files**: "Include in your config? (y/n)"
- **Previously enabled**: "Keep it? (y/n/skip)"
- **Previously disabled**: "Enable it? (y/n/skip)"

Your choices are saved in `.sync-state-<yourname>.json`

### Step 5: Auto-Sync on Git Pull (Optional)

Add a git hook to auto-sync after pulling:

```bash
cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
./sync-interactive.sh
EOF

chmod +x .git/hooks/post-merge
```

Now whenever you `git pull`, the sync script runs and only asks about **new files** - it remembers your previous choices.

## Daily Workflow

### Initial Selection
```bash
# First time
./sync-interactive.sh

# You see:
# ? New file found: shared/perplexity.md
#   → Would sync to: ~/.claude/commands/perplexity.md
#   Include in your config? (y/n): y
#
# ? New file found: xandru/custom-agent.md
#   → Would sync to: ~/.claude/agents/custom-agent.md
#   Include in your config? (y/n): y
```

### Updating Your Choices
```bash
# Later, you change your mind
./sync-interactive.sh

# You see:
# ✓ Currently enabled: shared/perplexity.md
#   → Syncs to: ~/.claude/commands/perplexity.md
#   Keep it? (y/n/skip): y
#
# ✓ Currently enabled: xandru/custom-agent.md
#   → Syncs to: ~/.claude/agents/custom-agent.md
#   Keep it? (y/n/skip): n   # Disabled it!
```

### After Git Pull (with hook)
```bash
git pull

# Auto-runs sync, only asks about NEW files:
# ? New file found: shared/new-feature.md
#   → Would sync to: ~/.claude/skills/new-feature.md
#   Include in your config? (y/n): y
#
# (Doesn't ask about files you've already chosen)
```

## Example File Structure

**shared/perplexity-commands.md:**
```markdown
# Destination: commands

# Perplexity MCP Commands

Custom commands for Perplexity integration...
```

**xandru/my-agent.md:**
```markdown
# Destination: agents

# My Custom Agent

Agent configuration...
```

**shared/global-prefs.md:**
```markdown
# Destination: .

# Global Claude Preferences

These preferences apply to all sessions...
```

## Troubleshooting

### "jq: command not found"

Install jq:
```bash
brew install jq
```

### Reset All Preferences

```bash
rm .sync-state-$(whoami).json
./sync-interactive.sh
```

### View Current Preferences

```bash
cat .sync-state-$(whoami).json | jq .
```

### Check Where a File Will Sync

```bash
head -5 shared/myfile.md | grep "Destination"
```
