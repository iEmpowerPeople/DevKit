---
description: Formats text and approval workflow for all file edits when using Claude Code CLI’s Edit-tool. Use for every file edit and before every Edit tool call.
---

# File Editing

## Overview
This guide standardises file-editing workflows using the Claude Code CLI's Edit tool.
It includes:
- How to format the text to be added/merged into an existing file.
- How to present file editing workflow in a 2 stage process:
Stage 1: Print Markdown Block
Stage 2: Edit-tool call 

## Text Formatting
- Provide edits for relevant sections; no full rewrites
- Provide each edit unique numbering for referencing
- Write incisively: maximise information density per token while preserving all semantics; remove non-essential words; NO redundancy.

## Workflow Formatting
### **Stage 1 - Output as visible markdown text in thread (NOT in tool call):**
> **##[Unique Number] [Edit Title (max 5 words)]**
> **Purpose:** [Brief explanation of edit purpose; max 3 sentences]
> **File:** [Exact Filename]
> **Location:** [Section Header or Line approx.]

### **Stage 2 immediately after Stage 1:** 
- Execute Edit tool call

## Rules
**Stage 1**
- DO NOT add empty line breaks between title, purpose, file or location
- DO NOT use Markdown headings; the identifier is plain text
- If [Unique Number] < 10, add "0" before it eg. ##01, ##11, ##111 
- ALWAYS output Stage 1 markdown blockquote, then immediately call Edit; no text in between.”

## Example
> **##01 Fix tile weight**
> **Purpose:** Correct the kg/m² calculation after updated tile mass.
> **File:** test.md
> **Location:** Section 10, “Zonqor Tile” (around line 312)
[TOOL_CALL: Edit]
