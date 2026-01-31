# AI Guide: Creating Library Tools

Machine-readable specification for AI assistants adding commands, agents, scripts, skills, MCP servers, or extras to this repository.

## File Locations

```
library/{author}/.commands/{name}.md   # Commands
library/{author}/agents/{name}.md      # Agents  
library/{author}/scripts/{name}.{ext}  # Scripts (.py, .sh)
library/{author}/skills/{name}/SKILL.md # Skills (folder with SKILL.md)
library/{author}/skills-user-only/{name}/SKILL.md # User-only skills (folder with SKILL.md)
library/{author}/mcp/{name}.md         # MCP server configs
library/{author}/extras/{name}.md      # External tool references
```

Valid authors: See `config/schema.yml` for current list (typically: `shared`, `xapids`, `tihany7`)

## Hidden `.commands/` Folders

The `library/{author}/.commands/` folders exist because:

1. **OpenCode limitation:** OpenCode does not support user-invocable skills yet.
2. **Workaround:** Command wrappers invoke user-only skills for OpenCode.
3. **Why hidden:** These wrappers are implementation details, not the source of truth.

Without `.commands/`, user-only skills could not be invoked via `/skill-name` in OpenCode.

## YAML Frontmatter Specification

All `.md` files in commands/, agents/, skills/, and mcp/ MUST begin with YAML frontmatter.

### Required Fields (All Types)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `description` | string | YES | One-line description. Quote if contains `:` |

### Required Fields (Skills Only)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | YES | Must match folder name (lowercase, hyphens allowed, max 64 chars) |
| `description` | string | YES | One-line description of what the skill does |
| `disable-model-invocation` | boolean | YES | Set to `true` to prevent AI from auto-invoking |
| `user-invocable` | boolean | YES | Set to `true` to allow user invocation via /skill-name |

### Optional Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `requires_extras` | string | NO | Extras dependencies in backtick format (must exist in library) |
| `requires_scripts` | string | NO | Script dependencies in backtick format |
| `allowed-tools` | string | NO | (Skills) Tools the AI can use without permission when skill is active |
| `argument-hint` | string | NO | (Skills) Hint shown during autocomplete, e.g. `[filename]` |
| `context` | string | NO | (Skills) Set to `fork` to run in a subagent context |
| `agent` | string | NO | (Skills) Subagent type when `context: fork` is set |
| `model` | string | NO | (Skills) Model to use when skill is active |

### Dependency Format

Dependencies use backtick-quoted string format:
- Single: `"`tool`"`
- Multiple: `"`tool1`, `tool2`, `tool3`"`

Script names only - no paths.
Extras IDs only - must exist in `library/*/extras/`.

---

## Tool Type Schemas

### Command Schema

| Component | Location | Required | Format |
|-----------|----------|----------|--------|
| Frontmatter start | Line 1 | YES | `---` |
| `description` | Frontmatter | YES | string (quote if contains `:`) |
| `requires_extras` | Frontmatter | NO | backtick-quoted list |
| `requires_scripts` | Frontmatter | NO | backtick-quoted list |
| Frontmatter end | After fields | YES | `---` |
| Title | Body | YES | `# ` heading |
| Content | Body | YES | Markdown |

**File path**: `library/{author}/.commands/{id}.md`
**ID**: filename without `.md` extension

### Agent Schema

| Component | Location | Required | Format |
|-----------|----------|----------|--------|
| Frontmatter start | Line 1 | YES | `---` |
| `description` | Frontmatter | YES | string (quote if contains `:`) |
| `requires_extras` | Frontmatter | NO | backtick-quoted list |
| `requires_scripts` | Frontmatter | NO | backtick-quoted list |
| Frontmatter end | After fields | YES | `---` |
| Title | Body | YES | `# ` heading |
| Content | Body | YES | Markdown |

**File path**: `library/{author}/agents/{id}.md`
**ID**: filename without `.md` extension

### Skill Schema

| Component | Location | Required | Format |
|-----------|----------|----------|--------|
| Frontmatter start | Line 1 | YES | `---` |
| `name` | Frontmatter | YES | string (must match folder name) |
| `description` | Frontmatter | YES | string (quote if contains `:`) |
| `disable-model-invocation` | Frontmatter | YES | `true` (prevents AI auto-invocation) |
| `user-invocable` | Frontmatter | YES | `true` (allows /skill-name invocation) |
| Frontmatter end | After fields | YES | `---` |
| Title | Body | YES | `# ` heading |
| Content | Body | YES | Markdown |

**File path**: `library/{author}/skills/{id}/SKILL.md`
**ID**: folder name (must match `name` field in frontmatter)

**Example frontmatter:**
```yaml
---
name: my-skill
description: What this skill does
disable-model-invocation: true
user-invocable: true
---
```

**Why these fields?**
- `name`: Required by OpenCode for skill discovery
- `disable-model-invocation: true`: Prevents AI from running the skill automatically (user must type /skill-name)
- `user-invocable: true`: Ensures the skill appears in the /command menu

#### Required Skill Folder Structure

Every skill folder (in `skills/` or `skills-user-only/`) MUST contain:

```
{skill-name}/
├── SKILL.md          # Main skill file (required)
├── reference/        # Reference documentation (required folder)
├── scripts/          # Helper scripts (required folder)
├── assets/           # Images/data/templates (required folder)
└── templates/        # Template files (required folder)
```

### Skills-User-Only Schema

Same schema as skills, with one extra rule:

- `user-invocable` MUST be `true`

**File path**: `library/{author}/skills-user-only/{id}/SKILL.md`
**ID**: folder name (must match `name` field in frontmatter)

### MCP Schema

| Component | Location | Required | Format |
|-----------|----------|----------|--------|
| Frontmatter start | Line 1 | YES | `---` |
| `description` | Frontmatter | YES | string |
| Frontmatter end | After fields | YES | `---` |
| Title | Body | YES | `# ` heading |
| Content | Body | YES | Markdown with install instructions |

**File path**: `library/{author}/mcp/{id}.md`
**ID**: filename without `.md` extension

### Extras Schema

| Component | Location | Required | Format |
|-----------|----------|----------|--------|
| Title | Line 1 | YES | `# ` heading |
| Description | Body | YES | Brief text |
| Why section | Body | YES | `## Why you might want it` + list |
| Install section | Body | YES | `## Install` + link |

**File path**: `library/{author}/extras/{id}.md`
**ID**: filename without `.md` extension (use `-cli` or `-gui` suffix)
**No frontmatter required**

### Script Schema (Python)

| Component | Location | Required | Format |
|-----------|----------|----------|--------|
| Shebang | Line 1 | YES | `#!/usr/bin/env python3` |
| Docstring | After shebang | YES | `"""..."""` |
| Code | Body | YES | Python code |

**File path**: `library/{author}/scripts/{id}.py`
**Must be executable**: `chmod +x`

### Script Schema (Bash)

| Component | Location | Required | Format |
|-----------|----------|----------|--------|
| Shebang | Line 1 | YES | `#!/bin/bash` or `#!/usr/bin/env bash` |
| Description | Line 2 | YES | `# ...` comment |
| Code | Body | YES | Bash code |

**File path**: `library/{author}/scripts/{id}.sh`
**Must be executable**: `chmod +x`

---

## Validation Rules

1. Frontmatter MUST be first content in file
2. Frontmatter MUST be between `---` markers
3. `description` field is REQUIRED for all types
4. **Skills MUST have**: `name`, `description`, `disable-model-invocation`, `user-invocable` fields
5. Skill `name` MUST match the folder name (lowercase, hyphens allowed)
6. Skills MUST include `reference/`, `scripts/`, `assets/`, `templates/` folders
7. Skills-user-only MUST set `user-invocable: true`
8. Dependencies MUST use `"`backtick`"` format (quoted string with backticks)
9. Dependencies MUST reference items that exist in the library
10. `requires_extras` IDs MUST match files in `library/*/extras/`
11. `requires_scripts` names MUST match files in `library/*/scripts/`
12. Scripts MUST be executable (`chmod +x`)
13. Scripts MUST have shebang line

## After Creating/Modifying Tools

Run regeneration to update profiles and README:
```bash
make generate
```

Or manually for a specific profile:
```bash
python3 repo-library/scripts/devkit-update-profile.py xapids
```

## Profile Output Format

The update-profile script generates:

```yaml
  - id: tool-id
    author: author-name
    requires_extras: `extra1-cli`, `extra2-cli`
    requires_scripts: `script.py`
    enabled: false
```

Field order: id, author, requires_extras (if any), requires_scripts (if any), enabled (always last).

## Examples Reference

See working examples at:
- `library/shared/.commands/shared-example-command.md`
- `library/shared/agents/shared-example-agent.md`
- `library/shared/skills/shared-example-skill/SKILL.md`
- `library/shared/scripts/shared-example-script.py`
- `library/shared/mcp/shared-example-mcp.md`
- `library/shared/extras/shared-example-extra-cli.md`

---

## Adding a New Tool Type

To add a new category (e.g., `hooks/`):

1. Edit `config/schema.yml` — add the new category with its schema
2. Create `library/shared/{type}/` folder
3. Create `library/shared/{type}/shared-example-{type}.md` example file
4. Run `make generate` to update all derived files
5. Commit all changes

The schema file is the Single Source of Truth. Scripts, profiles, README, and documentation all derive from it.
