---
description: Add, remove, or show LLM proxy environment variables in Claude Code settings
---

# Proxy Claude Code Environment

Manage proxy-related environment variables in `~/.claude/settings.json` for routing Claude Code through the LLM API Key Proxy.

## Target File

`~/.claude/settings.json`

## Managed Keys

This command exclusively manages these 7 environment variables:

- `ANTHROPIC_AUTH_TOKEN`
- `ANTHROPIC_BASE_URL`
- `API_TIMEOUT_MS`
- `ANTHROPIC_DEFAULT_OPUS_MODEL`
- `ANTHROPIC_DEFAULT_SONNET_MODEL`
- `ANTHROPIC_DEFAULT_HAIKU_MODEL`
- `CLAUDE_CODE_MAX_OUTPUT_TOKENS`

Other env vars in the file are **never touched**.

## Default Values

```json
{
  "ANTHROPIC_AUTH_TOKEN": "XapAPI_3.",
  "ANTHROPIC_BASE_URL": "http://127.0.0.1:8000",
  "API_TIMEOUT_MS": "300000",
  "ANTHROPIC_DEFAULT_OPUS_MODEL": "antigravity/claude-opus-4.5",
  "ANTHROPIC_DEFAULT_SONNET_MODEL": "antigravity/claude-sonnet-4.5",
  "ANTHROPIC_DEFAULT_HAIKU_MODEL": "firmware/anthropic/claude-haiku-4-5-20251001",
  "CLAUDE_CODE_MAX_OUTPUT_TOKENS": "32000"
}
```

---

## Workflows

### `add` - Add/Update Proxy Env Vars

1. Read current `~/.claude/settings.json`
2. Display the default values above
3. Ask user: "Confirm these values or specify changes?"
4. Merge the (confirmed/modified) values into the `env` section
   - Create `env` object if it doesn't exist
   - Preserve any existing env vars not in the managed list
5. Write the updated file
6. Display summary of added/updated keys

### `remove` - Remove Proxy Env Vars

1. Read current `~/.claude/settings.json`
2. List which managed keys are currently present
3. Remove only the 7 managed keys from `env`
4. If `env` becomes empty (`{}`), remove the entire `env` key
5. Write the updated file
6. Display confirmation of removed keys

### `show` - Show Current Status

1. Read current `~/.claude/settings.json`
2. For each managed key, display:
   - Present / Missing
   - Current value (if present)
   - Matches default? (Yes/No/N/A)
3. Summary line:
   - "Fully configured" - all 7 keys present with default values
   - "Configured (modified)" - all 7 keys present, some differ from defaults
   - "Partially configured" - some keys present
   - "Not configured" - no managed keys present
