---
description: AI-guided git-gh sync workflow: branch → commit → PR → merge
---

# Git Flow

You are tasked with guiding user through complete git + github sync workflow. Analyze changes, generate branch names, commit messages, PR descriptions.

## Steps to follow:

1. **Analyze state:**
   - Run ALL:
     - `git status` for current state
     - `git diff --name-only` for unstaged files
     - `git diff --staged --name-only` for staged files
     - `git branch --list` for all local branches
   - For each branch:
     - `git log main..[branch] --oneline` for all commits
     - `git log origin/[branch]...[branch] --oneline 2>/dev/null` for unpushed commits

   **If on feature branch:**
   - Show branch message
   - Ask: "Continue on `branch-name` or create new one?"

   **If on main/master with existing branches:**
   - Show branch message
   - Ask: "Continue with existing branch or create new one?"

   **If on main/master without existing branches:**
   - Create new branch

   **Branch message schema:**
   - Labels: `*us*` = unstaged; `*s*` = staged; `*uc*` = committed unpushed; `*c*` = committed pushed; `*` = branch currently on
   - DO NOT use AskUserQuestion tool; Ask question in chat thread
   - Follow exact schema:
   ```markdown

   Working directory:
     *us* auth/social.ts
     *s*  auth/providers.ts
     *s*  api/callback.ts

   Branches:
   * feature/auth (on remote):
     *c*  abc123 Add OAuth2 configuration
     *c*  bcd234 Implement Google provider
     *uc* def456 Add user profile mapping
     *uc* efg567 Fix token validation

   feature/other (not on remote):
     *uc* hij678 Initial implementation

   main (up to date)

   [Ask question]
   ```

2. **Analyze changes:**
   - If user selected existing branch: `git checkout [branch-name]`, then `git diff main` to see branch changes
   - Read all changed files to understand: problem solved, feature added, type (fix/feature/refactor/enhancement), technical details
   - `git log --oneline -10`: commit style, conventions, scope
   - Identify scope/area (auth, ui, api, docs)
   - **Check if changes span multiple unrelated concerns**: If they do (e.g., auth fix + docs update + UI feature), ask user: "Split into separate atomic commits or combine into one?"
   - **If user chooses split**: Group files by concern (e.g., Group 1: auth files, Group 2: docs files, Group 3: UI files)

3. **Generate branch name:**
   If user chose existing branch: skip to step 4
   Otherwise, generate name:
   Pattern: `type/scope-description`
   Types: `feature`, `fix`, `refactor`, `docs`, `test`, `chore`
   Examples: `feature/auth-social-login`, `fix/api-rate-limiting`

4. **Generate commit message(s):**
   **If single commit**: Draft one message
   **If multi-commit**: Draft one message per group

   Format:
   ```
   type(scope): imperative summary (<72 chars)

   - Key change 1
   - Key change 2
   - Why change was needed
   ```

   Rules:
   - Imperative mood: "Add" not "Added"
   - Focus on WHY not only WHAT
   - Match repo's `git log` style

5. **Generate PR:**
   Draft PR following this format:

   **Title**: `Type: Imperative description`

   - Capitalize prefix: `Feat:`, `Fix:`, `Docs:`, `Refactor:` etc.
   - Keep title concise and action-oriented
   - Example: `Feat: Add social login with OAuth2`

   **Body**:
   ```markdown
   ## Summary
   [1-2 Sentences: what + why, using imperative mood]

   ## Changes
   - [Key change with file reference]
   - [Another change]
   - [Technical detail]

   ## Testing
   - [ ] Tests pass locally
   - [ ] Manual verification
   - [ ] No breaking changes (or documented if present)

   ## Notes
   [Any Context, decisions, or follow-up needed]
   ```

6. **Present plan to user:**
   Use EXACT schema:

   ```
   PROPOSED WORKFLOW
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   📋 Analysis Summary:
   • Change type: *[Feature/Fix/etc.]*
   • Scope: *[Area affected]*
   • Change: *[Brief description]*

   🌿 Branch:
   git checkout -b *[suggested-branch-name]*

   💾 Commit(s):
   [If single commit:]
   git add *[specific files]*
   git commit -m *"[suggested commit message]"*

   [If multi-commit:]
   git add *[group1 files]*
   git commit -m *"[group1 message]"*
   git add *[group2 files]*
   git commit -m *"[group2 message]"*
   git add [group3 files]
   git commit -m *"[group3 message]"*

   🚀 Push & PR:
   git push -u origin *[branch-name]*
   gh pr create --title *"[PR title]"* --body *"[PR description]"*

   🔀 After approval, merge:
   gh pr merge --merge
   git checkout main
   git pull
   git branch -d *[branch-name]*

   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

   Reply with: 
   • "proceed" to execute with these suggestions
   • "edit" with specific changes
   AND
   • "keep branch" to keep branch after merge
   • "delete branch" to delete branch after merge
   ```

7. **Handle response:**
   - If "proceed": Execute all commands in sequence
   - If "edit": Ask which parts to change
   - Remember "keep branch" or "delete branch" for step 8
   - If Unclear: Clarify

8. **Execute (post-approval only):**

   **Phase 1: Branch & Commit(s)**
   - If new branch: `git checkout -b [name]`
   - If existing branch: already checked out in step 2

   **If single commit:**
   - Stage: `git add [file1] [file2]` (NOT `git add .`)
   - Commit: `git commit -m "[message]"` with approved message
   - Verify: `git status` clean

   **If multi-commit:**
   - For each group in order:
     - Stage group files: `git add [group files]`
     - Commit: `git commit -m "[group message]"`
   - Verify: `git status` clean after all commits

   **Phase 2: Push & PR**
   - Push: `git push -u origin [branch-name]`
   - PR: `gh pr create --title "[title]" --body "[body]"`
   - Show PR URL to user

   **Phase 3: Merge (only after user confirms PR is approved)**
   - Ask: "Is the PR approved and ready to merge?"
   - Yes: 
     - merge: `gh pr merge --merge` or `--squash`/`--rebase` if specifically requested by user
     - Checkout main: `git checkout main`
     - Pull: `git pull`
     - If step 7 "Keep Branch": keep branch, DO NOT delete
     - If step 7 "Delete Branch": 
       - Verify branch is fully merged: `git branch --merged main | grep [branch-name]`
       - If branch is in the merged list: `git branch -d [branch-name]`
       - If branch is NOT in merged list: 
          - Warn user: "Branch has unmerged changes. Force delete anyway? (You'll lose commits not in main)"
          - If yes: `git branch -D [branch-name]`
          - If no: Keep branch
   - No: Stop and follow user instructions

9.  **Report:**
   ```
   ✅ Complete!
   • Branch: [name]
   • Commit: [hash] [message]
   • PR: [URL]
   • Status: [Merged/Pending]
   • Branch: [Still exists/Deleted]
   ```

## Critical Rules:

- NEVER execute before presenting plan
- Specific `git add [files]`, not `git add .` or `-A`
- Analyze actual changes, don't guess
- Match repo conventions via `git log`
- Don't auto-merge; wait for user approval
- User-authored commits only (NO Claude co-author attribution)

## Error Handling:

- Branch exists: Ask use/rename
- No changes: Inform nothing to commit
- gh missing: Inform user
- Push fails: Check remote, offer create

## Examples:

**Feature:**
- Branch: `feature/add-user-search`
- Commit: `feat(users): add search with filters`
- PR: `Feat: Add user search with filtering`

**Fix:**
- Branch: `fix/auth-token-expiry`
- Commit: `fix(auth): correct token expiration`
- PR: `Fix: Resolve token expiration bug`

## Edge Cases:

- No changes: Inform nothing to commit
- Conflicts: Manual resolution needed
- PR exists: Show URL, ask update?
