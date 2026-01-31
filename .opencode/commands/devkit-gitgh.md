---
description: "DevKit git-gh workflow: branch, commit, PR with authorship rules"
requires_extras: "`git-cli`, `github-cli`"
---

# DevKit Git Flow

Git + GitHub workflow for DevKit with authorship and PR ownership rules.

## DevKit Authorship Rules

| Folder | Who Can PR | Who Approves |
|--------|-----------|--------------|
| `library/shared/` | Anyone | Any team member |
| `library/xapids/` | xapids only | xapids |
| `library/tihany7/` | tihany7 only | tihany7 |
| `repo-library/` | Anyone | Any team member |
| `profiles/{user}.yml` | That user | That user |

## Step 1: Identify User

Ask: "Which author are you? (xapids / tihany7 / other)"

Store response for authorship validation.

## Step 2: Analyze State

Run ALL in parallel:
```bash
git status
git diff --name-only
git diff --staged --name-only
git branch --list
```

For each branch:
```bash
git log main..[branch] --oneline
git log origin/[branch]...[branch] --oneline 2>/dev/null
```

Display state using schema:
```
Working directory:
  *us* path/to/file.md      # unstaged
  *s*  path/to/other.md     # staged

Branches:
* feature/current (on remote):
  *c*  abc123 Previous commit
  *uc* def456 Unpushed commit

main (up to date)
```

Labels: `*us*` = unstaged; `*s*` = staged; `*uc*` = committed unpushed; `*c*` = committed pushed; `*` = current branch

## Step 3: Validate Authorship

Check changed files against authorship rules:

```bash
git diff --name-only HEAD
```

**Validation rules:**
- Files in `library/xapids/` → only xapids can PR
- Files in `library/tihany7/` → only tihany7 can PR
- Files in `library/shared/` → anyone can PR
- Files in `repo-library/` → anyone can PR
- Files in `profiles/xapids.yml` → only xapids can PR
- Files in `profiles/tihany7.yml` → only tihany7 can PR

**If violations detected:**
```
WARNING: Authorship conflict detected

You identified as: {user}
But changes include files you cannot PR:
  - library/xapids/.commands/tool.md (owned by xapids)
  - profiles/tihany7.yml (owned by tihany7)

Options:
1. Remove those changes from this commit
2. Have the owner create the PR
3. Abort
```

## Step 4: Analyze Changes

Read changed files to understand:
- Problem solved / feature added
- Type: fix, feature, refactor, docs, chore
- Scope: library, profiles, repo-library, docs

Check commit style:
```bash
git log --oneline -10
```

## Step 5: Generate Branch Name

Pattern: `{type}/{scope}-{description}`

Types: `feature`, `fix`, `refactor`, `docs`, `chore`

Examples:
- `feature/shared-new-agent`
- `fix/xapids-command-typo`
- `docs/update-readme`
- `chore/repo-library-scripts`

## Step 6: Generate Commit Message

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

## Step 7: Generate PR

**Title**: `Type: Imperative description`

Examples:
- `Feat: Add social login command to shared library`
- `Fix: Correct sync adapter path handling`
- `Docs: Update workflow section in README`

**Body**:
```markdown
## Summary
[1-2 sentences: what + why]

## Changes
- [Key change with file reference]
- [Another change]

## Authorship
- [ ] All `library/shared/` changes (open to all)
- [ ] All `library/{my-author}/` changes (I am the owner)
- [ ] All `profiles/{my-profile}.yml` changes (I am the owner)

## Testing
- [ ] Scripts run without error
- [ ] Profile updates work
- [ ] No breaking changes

## Notes
[Context or follow-up needed]
```

## Step 8: Present Plan

```
PROPOSED WORKFLOW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Author: {user}
Change type: {Feature/Fix/etc.}
Scope: {library/shared, library/xapids, etc.}

Branch:
git checkout -b {branch-name}

Commit:
git add {files}
git commit -m "{message}"

Push & PR:
git push -u origin {branch-name}
gh pr create --title "{title}" --body "{body}"

After approval:
gh pr merge --merge
git checkout main && git pull
git branch -d {branch-name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Reply: "proceed" / "edit" / "abort"
And: "keep branch" / "delete branch"
```

## Step 9: Execute

**Phase 1: Branch & Commit**
```bash
git checkout -b {branch-name}
git add {specific-files}   # NOT git add .
git commit -m "{message}"
git status                 # verify clean
```

**Phase 2: Push & PR**
```bash
git push -u origin {branch-name}
gh pr create --title "{title}" --body "{body}"
```

Show PR URL to user.

**Phase 3: Merge (after approval)**

Ask: "Is the PR approved?"

If yes:
```bash
gh pr merge --merge
git checkout main
git pull
# If "delete branch":
git branch -d {branch-name}
```

## Step 10: Report

```
Complete!
• Author: {user}
• Branch: {name}
• Commit: {hash} {message}
• PR: {URL}
• Status: {Merged/Pending}
• Branch: {Kept/Deleted}
```

## Critical Rules

- NEVER execute before presenting plan
- Specific `git add {files}`, not `git add .`
- Validate authorship BEFORE committing
- Match repo conventions via `git log`
- Wait for user approval before merge
- User-authored commits only (NO AI co-author)

## Error Handling

| Error | Action |
|-------|--------|
| Branch exists | Ask: use existing or rename? |
| No changes | Inform nothing to commit |
| gh missing | Inform user to install GitHub CLI |
| Push fails | Check remote, offer to create |
| Authorship violation | Block and explain ownership rules |
