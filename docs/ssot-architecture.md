# DevKit SSOT Architecture

> **For AI assistants**: See `docs/ai-guide-ssot.md` for machine-optimized instructions.

## What is SSOT?

**Single Source of Truth** means one file defines shared data, and everything else derives from it. When you change the source, running `make generate` updates all dependent files automatically.

## The Source

```
config/schema.yml  ← THE source of truth
```

This file defines:
- **Authors** - Who can create tools (shared, xapids, tihany7)
- **Categories** - Tool types (agents, commands, skills, mcp, extras, scripts)
- **Validation rules** - What each tool type requires

## Visual: Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         SOURCES                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   config/schema.yml          library/**/*                       │
│   ┌───────────────┐          ┌───────────────┐                  │
│   │ • authors     │          │ • agents/*.md │                  │
│   │ • categories  │          │ • commands/*  │                  │
│   │ • validation  │          │ • skills/*    │                  │
│   └───────┬───────┘          │ • mcp/*       │                  │
│           │                  │ • extras/*    │                  │
│           │                  └───────┬───────┘                  │
│           │                          │                          │
└───────────┼──────────────────────────┼──────────────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      make generate                              │
│                                                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  devkit-update-profile.py    devkit-gen-catalogue.sh    │   │
│   │  (reads schema + library)    (reads schema + library)   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
            │                          │
            ▼                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DERIVED (auto-generated)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   profiles/*.yml              README.md                         │
│   ┌───────────────┐          ┌───────────────┐                  │
│   │ Tool listings │          │ Tool catalogue│                  │
│   │ with enabled  │          │ (Available    │                  │
│   │ flags         │          │  Tools section│                  │
│   └───────────────┘          └───────────────┘                  │
│                                                                 │
│   ⚠️  AUTO-GENERATED - Do not edit manually                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Commands

| Command | What it does |
|---------|-------------|
| `make generate` | Regenerate all derived files (profiles, README) |
| `make validate` | Check library files against schema rules |
| `make check` | Generate + validate + verify no uncommitted changes |

## Dependency Map

| Source | Derived |
|--------|---------|
| `config/schema.yml` | Scripts read authors/categories from here |
| `library/**/*` | `profiles/*.yml`, `README.md` catalogue section |

## Common Tasks

### Adding a new tool

1. Create file in `library/{author}/{category}/`
2. Run `make generate`
3. Commit

### Adding a new tool type (category)

1. Edit `config/schema.yml` - add the category
2. Create example file in `library/shared/{type}/`
3. Run `make generate`
4. Commit

### Adding a new author

1. Edit `config/schema.yml` - add to authors list
2. Create `library/{author}/` directory
3. Create `profiles/{author}.yml`
4. Run `make generate`
5. Commit

## CI Behavior

GitHub Actions automatically:
1. Triggers on changes to `library/**`, `config/**`, `repo-library/scripts/**`, `Makefile`
2. Runs `make validate` (catches errors)
3. Runs `make generate` (updates derived files)
4. Auto-commits if files changed

## Best Practices

1. **Never edit derived files** - They have "AUTO-GENERATED" comments
2. **Always run `make generate`** after changing library or schema
3. **Use `make check`** before committing to catch sync issues
4. **Edit the source** - Change schema.yml for structure, library files for content

## Adding New Documentation

To add documentation that follows SSOT:

1. **Identify the source** - What file is authoritative?
2. **Create the doc** - Reference the source, don't duplicate data
3. **Add to schema** if it's a new category type
4. **Cross-reference** - Human docs point to AI docs and vice versa

Example pattern:
```
docs/my-feature.md          ← Human-readable (THE SOURCE)
docs/ai-guide-my-feature.md ← AI-readable (references human doc)
```

The AI doc should say: "See `docs/my-feature.md` for full details" and only add AI-specific instructions.
