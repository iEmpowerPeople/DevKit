---
name: devkit-library
description: "Orientation: understand DevKit library structure before contributing"
disable-model-invocation: true
user-invocable: true
---

# DevKit Library Orientation

You are helping the user contribute to the DevKit library. Your job is to ensure they understand the system before making changes.

## Initial Response

When this command is invoked, respond with:

```
I'll help you work with the DevKit library. What do you need to do?

1. Enable/disable tools in your profile
2. Create a new tool (command, agent, skill, mcp, extra, script)
3. Add a new author namespace
4. Add a new tool category

Which task are you working on?
```

Then wait for the user's response.

## Before Any Task

1. **Read the core docs first** — do not proceed without reading these:
   - `CLAUDE.md` — workflows and anti-patterns
   - `config/schema.yml` — valid authors, categories, required fields

2. **For creating/editing tools**, also read:
   - `docs/adding-to-library.md` — schemas for each tool type
   - An example file from `library/shared/{type}/` matching what they're creating

## Task Workflows

### Task 1: Enable/disable tools

1. Ask which profile: `ls profiles/`
2. Ask which tool(s) they use: `claude`, `opencode`, or `both`
3. Read their profile: `cat profiles/{name}.yml`
4. Edit `enabled: true/false` for desired tools
5. Run sync: `python3 repo-library/scripts/devkit-sync-adapter.py {profile} --target {tool}`
6. Verify synced:
   - If claude/both: `ls ~/.claude/commands/`
   - If opencode/both: `ls ~/.config/opencode/commands/`

### Task 2: Create a new tool

1. Confirm tool type and author with user
2. Read schema: `cat config/schema.yml` — check required fields
3. Read example: `cat library/shared/{type}/shared-example-{type}.md`
4. Create file at `library/{author}/{type}/{id}.md` following schema
5. Run: `make generate`
6. Verify tool appears in `profiles/{author}.yml`
7. Commit source + generated files together

### Task 3: Add a new author

1. Edit `config/schema.yml` — add to `authors:` list
2. Create folders: `mkdir -p library/{author}/{commands,agents,skills,mcp,extras,scripts}`
3. Run: `make generate`
4. Verify: `ls profiles/` shows new profile
5. Commit schema + folders + generated profile together

### Task 4: Add a new tool category

1. Edit `config/schema.yml` — add to `categories:` with required fields
2. Create folders for all existing authors
3. Create example: `library/shared/{type}/shared-example-{type}.md`
4. Run: `make generate && make check`
5. Commit schema + folders + example + generated files together

## Important

- **Never duplicate** — point to files, don't copy their content
- **Never skip** — always run `make generate` after library changes
- **Never edit** — `profiles/*.yml` structure is auto-generated, only toggle `enabled:`
