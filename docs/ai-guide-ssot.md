# AI Guide: SSOT Architecture

Machine-readable specification for AI assistants working with DevKit's Single Source of Truth system.

> **Human-readable version**: `docs/ssot-architecture.md`

## Quick Reference

```yaml
source_of_truth: config/schema.yml
derived_files:
  - profiles/*.yml
  - README.md (catalogue section)
commands:
  regenerate: make generate
  validate: make validate
  full_check: make check
```

## Schema Structure

The schema at `config/schema.yml` defines:

```yaml
authors:
  - id: string        # Author identifier
    description: string

categories:
  {category_name}:
    file_pattern: string              # Path template with {author}, {id}
    requires_frontmatter: boolean
    required_fields: [string]         # Frontmatter fields
    optional_fields: [string]
    example: string                   # Example file ID

validation:
  requires_extras_must_exist: boolean
  requires_scripts_must_exist: boolean
  scripts_must_be_executable: boolean
```

## Decision Tree

```
TASK: Add/modify a tool
├─► Create/edit file in library/{author}/{category}/
├─► Run: make generate
└─► Commit changes

TASK: Add new tool category
├─► Edit: config/schema.yml (add category)
├─► Create: library/shared/{category}/shared-example-{category}.md
├─► Run: make generate
└─► Commit changes

TASK: Add new author
├─► Edit: config/schema.yml (add to authors)
├─► Create: library/{author}/ directory
├─► Create: profiles/{author}.yml
├─► Run: make generate
└─► Commit changes

TASK: Verify changes are correct
└─► Run: make check
    ├─► Exit 0: All files in sync
    └─► Exit 1: Run `make generate` and commit
```

## File Modification Rules

| File Pattern | Editable? | Notes |
|-------------|-----------|-------|
| `config/schema.yml` | YES | Source of truth for structure |
| `library/**/*` | YES | Source of truth for content |
| `profiles/*.yml` | NO | Auto-generated, has header comment |
| `README.md` (catalogue) | NO | Section marked AUTO-GENERATED |
| `docs/*.md` | YES | Documentation is manually maintained |

## Validation Checks

When `make validate` runs, it checks:

1. All tool files have required frontmatter (per schema)
2. Required fields present in frontmatter
3. `requires_extras` references existing extras
4. `requires_scripts` references existing scripts
5. Scripts are executable (`chmod +x`)
6. Scripts have shebang line
7. Example files exist for each category

## Reading Schema Programmatically

Python:
```python
import yaml
from pathlib import Path

def load_schema(repo_root):
    schema_path = repo_root / "config" / "schema.yml"
    with open(schema_path) as f:
        return yaml.safe_load(f)

schema = load_schema(Path("."))
authors = [a["id"] for a in schema["authors"]]
categories = list(schema["categories"].keys())
```

Bash (requires yq):
```bash
# Get authors
yq -r '.authors[].id' config/schema.yml

# Get categories (excluding scripts)
yq -r '.categories | keys | .[] | select(. != "scripts")' config/schema.yml
```

## Anti-Patterns

DO NOT:
- Hardcode author lists in scripts (read from schema)
- Hardcode category lists in scripts (read from schema)
- Edit files marked AUTO-GENERATED
- Skip `make generate` after library changes
- Duplicate schema data in documentation

DO:
- Read from `config/schema.yml` for authors/categories
- Run `make generate` after any library or schema change
- Use `make check` before committing
- Reference source docs instead of duplicating

## Adding Documentation (SSOT Pattern)

When creating new documentation:

1. **Human doc is the source**: `docs/{feature}.md`
2. **AI doc references it**: `docs/ai-guide-{feature}.md`
3. AI doc starts with: `> **Human-readable version**: docs/{feature}.md`
4. AI doc contains machine-optimized format (tables, decision trees, code)
5. Only update AI doc when AI-specific guidance changes

This ensures:
- One place to update conceptual information (human doc)
- AI doc stays focused on actionable instructions
- Cross-references keep both in sync
