---
description: "Orientation: understand DevKit framework before modifying its machinery"
---

# DevKit Framework Orientation

You are helping the user modify DevKit's framework — the scripts and build system that process library content.

## Initial Response

When this command is invoked, respond with:

```
I'll help you modify the DevKit framework. Before we make any changes, I need to read the relevant documentation and source files to ensure I understand the system.
```

Then proceed to read the required files.

## Required Reading

**Do not proceed without reading these:**

1. `CLAUDE.md` — workflows, anti-patterns, library vs framework distinction
2. `docs/ai-guide-ssot.md` — SSOT system and derived files
3. The specific script(s) the user wants to modify in `repo-library/scripts/`

## Rules

After reading, confirm you understand:

- **Data flow**: `library/` + `config/schema.yml` → scripts → `profiles/*.yml` + `README.md`
- **SSOT**: Never hardcode content that lives in source files
- **Preservation**: Profile regeneration must preserve `enabled:` states
- **Cross-platform**: Scripts must work on macOS and Linux
- **Validation**: Always run `make generate && make check` after changes
- **No regressions**: Diff `profiles/` and `README.md` before committing

## Then

Ask the user what specific change they need to make, and proceed only after confirming you've read the relevant source files.

## Related Commands

- `/devkit-library` — orientation for library contributions (adding content, not modifying machinery)
