---
description: Example Claude Code hook demonstrating library structure
hook_type: PostToolUse
---

# Example Shared Claude Code Hook

This is an example Claude Code hook available to all users.

## Purpose

Demonstrates the shared library hook structure for Claude Code.

## Hook Types

Claude Code supports these hook types:
- `PreToolUse` - Runs before a tool is executed
- `PostToolUse` - Runs after a tool is executed
- `Notification` - Runs when notifications are triggered
- `Stop` - Runs when the agent stops

## Configuration

Hooks are configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Bash",
        "hooks": ["./hooks/my-hook.sh"]
      }
    ]
  }
}
```

## Author

Maintained by the community (shared)
