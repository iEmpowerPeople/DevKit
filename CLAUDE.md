# CLAUDE.md

Guidance for AI coding assistants working on this repository.

## What This Is

DevKit is a shared centralized personal library of AI coding tools that syncs to Claude Code and OpenCode configs. Users maintain profiles selecting which tools to enable.

## Workflows

### Using the library (enable/sync/create tools)

```
┌─────────────────────────────────────────────────────────────┐
│  ENABLE TOOLS                     CREATE/EDIT TOOLS         │
│  ─────────────                    ─────────────────         │
│  1. Edit profiles/{you}.yml       1. Add file to            │
│     └─ toggle enabled: true          library/{author}/      │
│                                      └─ see docs/adding-    │
│                                         to-library.md       │
│              │                              │                │
│              ▼                              ▼                │
│  2. Run sync adapter              2. Run: make generate     │
│     └─ devkit-sync-adapter.py        └─ updates profiles/   │
│                                         and README.md       │
│              │                              │                │
│              ▼                              ▼                │
│  3. Tools active in               3. Commit source +        │
│     Claude Code / OpenCode           generated files        │
└─────────────────────────────────────────────────────────────┘

  EXPAND THE LIBRARY (new authors or tool types)
  ───────────────────────────────────────────────
  1. Edit config/schema.yml to add author or category
  2. Create folder structure and example files
  3. Run: make generate
  4. Commit all changes together
```

### Developing the framework (modify DevKit itself)

```
┌─────────────────────────────────────────────────────────────┐
│  FRAMEWORK FILES (change how DevKit works)                  │
│  ├─ repo-library/scripts/   ← sync, generation, validation  │
│  ├─ Makefile                ← build commands                │
│  └─ config/schema.yml       ← validation rules only         │
│        (adding authors/categories = library workflow)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
                   make generate + make check
                               │
                               ▼
              Verify all profiles and README regenerate correctly
                               │
                               ▼
                          git commit
```

## Project Structure

```
library/{author}/     # Tool definitions (SSOT)
  commands/*.md       # Slash commands
  agents/*.md         # Agent definitions
  skills/*/SKILL.md   # Skill folders
  mcp/*.md            # MCP server configs
  extras/*.md         # External tool references
  scripts/*.py|sh     # Helper scripts
profiles/*.yml        # Auto-generated; toggle enabled: true/false only
repo-library/         # Repo-specific utilities
config/schema.yml     # Schema defining all categories and authors
```

## Guides

| Task | Read |
|------|------|
| Create/edit a tool | `docs/adding-to-library.md` |
| Understand SSOT and derived files | `docs/ai-guide-ssot.md` |
| Look up valid categories, authors, fields | `config/schema.yml` |

## Anti-Patterns

- **Never edit** `profiles/*.yml` structure — only toggle `enabled:` field
- **Never hardcode** author/category lists — read from `config/schema.yml`
- **Never skip** `make generate` after library changes
