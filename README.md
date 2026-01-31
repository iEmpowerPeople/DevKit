# DevKit

> **Important:** All additions to this repository should be made through an AI CLI, NOT manually. 
> 
>The AI will follow the specifications to ensure proper formatting and compatibility.

## Overview
This is a shared AI configuration library - your single source of truth (SSOT) for custom tools like agents, skills, commands, MCPs etc.

Scripts automate sync with Claude Code and Opencode configs.

Compatible with MacOS and Linux.

<br>


## Model: Library vs Profiles vs Sync

**Library** = The complete catalogue of available tools  
**Profiles** = Your personal selections (which tools you want to use)  
**Sync** = The system that syncs your selected agents/skills/comannds to your Claude and Opencode files.

### Library Structure

```
DevKit/
├── library/
│   ├── shared/              # All users can create PRs and approve
│   │   ├── agents/
│   │   ├── commands/
│   │   ├── skills/
│   │   ├── scripts/
│   │   ├── mcp/
│   │   └── extras/
│   ├── xapids/              # xapids authors and owns PRs for this folder
│   │   ├── agents/
│   │   ├── commands/
│   │   ├── skills/
│   │   └── scripts/
│   └── tihany7/             # tihany7 authors and owns PRs for this folder
│       ├── agents/
│       ├── commands/
│       ├── skills/
│       └── scripts/
└── profiles/                # User selections (not auto-generated)
```

All team members have access to all configs - the folder structure indicates authorship and PR ownership.

### Profiles

Profiles contain your personal tool selections. They are automatically updated with all available tools from the library.

Example `profiles/xapids.yml`:
```yaml
agents:
  - id: shared-example-agent
    author: shared
    enabled: true

  - id: xapids-example-agent
    author: xapids
    enabled: false
```

Set `enabled: true` to sync a tool, `enabled: false` to skip it.

### Workflow including Sync

**Repo Commands** (run these in the DevKit repo):
- `/devkit-add-tool` - Interactive guide for adding tools or tool types
- `/devkit-sync` - Sync enabled tools to Claude/OpenCode configs
- `/devkit-gitgh` - Commit and PR workflow with authorship rules

**Manual workflow:**
1. Add/edit tools in `library/{author}/{category}/`
2. Run `make generate` to update profiles and README
3. Edit `profiles/<you>.yml` to set `enabled: true`
4. Commit to GitHub; open PR for files you own; pull `main`
5. Sync locally with: `python3 repo-library/scripts/devkit-sync-adapter.py [profile] [options]`

<br>


## Development (SSOT)

This repo uses **Single Source of Truth** architecture. See `docs/ssot-architecture.md` for details.

**Quick reference:**
```bash
make generate  # Regenerate profiles + README from library
make validate  # Check library files against schema
make check     # Full check before committing
```

**Key files:**
- `config/schema.yml` — Source of truth for categories, authors, validation
- `library/**/*` — Tool definitions (edit these)
- `profiles/*.yml` — Auto-generated, don't edit directly

<br>


## Installation

1) Get the repo

Option 1) If you have git

```bash
git clone https://github.com/iEmpowerPeople/DevKit.git
cd DevKit
```

Option 2) If you do NOT have git (download ZIP)

```bash
curl -L -o DevKit.zip https://github.com/iEmpowerPeople/DevKit/archive/refs/heads/main.zip
unzip DevKit.zip
cd DevKit-main
```

2) Print install/update commands for required deps (installs nothing)

- MacOS/Linux: `bash repo-library/scripts/devkit-install-required.sh`

<br>
<!-- AUTO-GENERATED CATALOGUE -->

<!-- AUTO-GENERATED: Do not edit this section manually. Run `make generate` to update. -->

## Available Tools

Auto-generated list of all tools in the library. Your profile is automatically updated with these tools.


### Agents

<ul>
  <li><strong>shared-example-agent</strong>        Example shared agent demonstrating library structure</li>
</ul>


### Commands

<ul>
  <li><strong>file-editing</strong>                  Formats text and approval workflow for all file edits when using Claude Code CLI’s Edit-tool. Use for every file edit and before every Edit tool call.</li>
  <li><strong>gitgh-us-merge</strong>                AI-guided git-gh sync workflow: branch → commit → PR → merge</li>
  <li><strong>incise</strong>                        Write incisively - maximize information density per token</li>
  <li><strong>shared-example-command</strong>        Example shared command demonstrating library structure</li>
</ul>


### Skills

<ul>
  <li><strong>proxy</strong>                       Proxy workflows for LLM API Key Proxy setup and usage</li>
  <li><strong>shared-example-skill</strong>        Example shared skill demonstrating library structure</li>
</ul>


### Skills-user-only

*No items yet*


### Mcp

<ul>
  <li><strong>context7</strong>                  Up-to-date, version-specific library/API documentation and code examples</li>
  <li><strong>perplexity</strong>                Official MCP server for the Perplexity API Platform (web search + ask/reason/research)</li>
  <li><strong>shared-example-mcp</strong>        Example shared MCP demonstrating library structure</li>
</ul>


### Extras

<ul>
  <li><strong>claude-code-cli</strong>                 Anthropic's agentic coding assistant CLI</li>
  <li><strong>git-cli</strong>                         Version control CLI for commits, branches, and collaboration</li>
  <li><strong>github-cli</strong>                      GitHub CLI for PRs, issues, and CI status</li>
  <li><strong>opencode-cli</strong>                    Terminal-based AI coding assistant</li>
  <li><strong>shared-example-extra-cli</strong>        Example CLI extra demonstrating library structure</li>
</ul>

<ul>
  <li><strong>codelayer-gui</strong>        Desktop UI for working with AI and code</li>
  <li><strong>opencode-gui</strong>         Desktop app for OpenCode</li>
  <li><strong>vscode-gui</strong>           Free cross-platform code editor with extensions</li>
</ul>


### Claude-code-hooks

<ul>
  <li><strong>shared-example-claude-code-hook</strong>        Example Claude Code hook demonstrating library structure</li>
</ul>


### Opencode-plugins

<ul>
  <li><strong>shared-example-opencode-plugin</strong>        Example OpenCode plugin demonstrating library structure</li>
</ul>


---

*Last updated: 2026-01-31 • Auto-generated by `repo-library/scripts/devkit-gen-catalogue.sh`*
