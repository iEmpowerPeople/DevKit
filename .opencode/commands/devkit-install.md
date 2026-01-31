---
description: Set up DevKit on a new machine or for a new user
---

# DevKit Installation

Guide for setting up DevKit from scratch or onboarding a new user.

## Prerequisites

DevKit requires:

| Dependency | Minimum Version | Purpose |
|------------|-----------------|---------|
| git | 2.30.0 | Version control |
| gh | any | GitHub CLI for PRs |
| python3 | 3.9.0 | Scripts |
| pip | any | Python packages |
| pyyaml | 6.0.0 | YAML parsing |
| yq | any (mikefarah/yq) | YAML processing |

## Check Dependencies

Run the install checker to see what's missing:

```bash
bash repo-library/scripts/devkit-install-required.sh
```

This prints install commands for any missing dependencies — it does not install them automatically.

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/iEmpowerPeople/devkit.git
cd devkit
```

### 2. Install Missing Dependencies

Run the checker and follow its output:

```bash
bash repo-library/scripts/devkit-install-required.sh
```

Install each missing dependency using the printed commands.

### 3. Create Your Profile

If you're a new user, add yourself to the schema and create a profile:

**a) Add author to schema** — edit `config/schema.yml`:

```yaml
authors:
  - id: shared
    description: Community-maintained tools
  - id: {your-username}
    description: {your-username} personal tools
```

**b) Regenerate profiles:**

```bash
make generate
```

This creates `profiles/{your-username}.yml` with all tools set to `enabled: false`.

### 4. Enable Your Tools

Edit `profiles/{your-username}.yml` and set `enabled: true` for tools you want:

```yaml
commands:
  - id: some-command
    author: shared
    enabled: true  # ← change this
```

### 5. Sync to Configs

```bash
python3 repo-library/scripts/devkit-sync-adapter.py {your-username} --target both
```

This copies enabled tools to:
- `~/.claude/` (Claude Code)
- `~/.config/opencode/` (OpenCode)

### 6. Verify

```bash
ls ~/.claude/commands/
ls ~/.claude/agents/
```

You should see your enabled tools.

## Existing User on New Machine

If you already have a profile in the repo:

```bash
# Clone
git clone https://github.com/iEmpowerPeople/devkit.git
cd devkit

# Check dependencies
bash repo-library/scripts/devkit-install-required.sh

# Sync your profile
python3 repo-library/scripts/devkit-sync-adapter.py {your-username} --target both
```

## Troubleshooting

### "yq: command not found"

Install mikefarah/yq (not the Python yq wrapper):

```bash
# macOS
brew install yq

# Linux - see https://github.com/mikefarah/yq#install
```

### "No module named 'yaml'"

```bash
python3 -m pip install --upgrade pyyaml
```

### Profile doesn't exist

You need to add yourself to `config/schema.yml` and run `make generate`. See step 3 above.

### Sync conflicts

If files already exist in destination:

```bash
# Preview what would happen
python3 repo-library/scripts/devkit-sync-adapter.py {profile} --dry-run
```

The sync adapter only modifies files it owns. Manually remove conflicting files or rename your tools.

## Related Commands

- `/devkit-sync` — detailed sync options
- `/devkit-library` — orientation for using/contributing to the library
