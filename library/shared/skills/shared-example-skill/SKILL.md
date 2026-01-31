---
name: shared-example-skill
description: Example shared skill demonstrating library structure
disable-model-invocation: true
user-invocable: true
---

# Example Shared Skill

This is an example skill available to all users. Invoke with `/shared-example-skill`.

## Purpose

Demonstrates the shared library skill structure with proper frontmatter for both Claude Code and OpenCode compatibility.

## Frontmatter Fields

Skills should include these frontmatter fields:
- `name`: Must match folder name (lowercase, hyphens allowed)
- `description`: One-line description of what the skill does
- `disable-model-invocation: true`: Prevents AI from auto-invoking (user must type /skill-name)
- `user-invocable: true`: Allows user to invoke via /skill-name

## Author

Maintained by the community (shared)
