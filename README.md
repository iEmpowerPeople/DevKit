# DevKit-Claude

Shared Claude Code configuration library for iEmpowerPeople team.

## Structure

```
DevKit-Claude/
├── shared/           # Shared configurations (both can edit)
├── xandru/          # Alex's authored configurations (Alex owns PRs)
└── friend/          # Tijana's authored configurations (Tijana owns PRs)
```

## Authorship & PRs

- **shared/** - Both Alex and Tijana can create PRs and approve
- **xandru/** - Alex authors and owns PRs for this folder
- **friend/** - Tijana authors and owns PRs for this folder

## Usage

```bash
# Clone the repo
git clone https://github.com/iEmpowerPeople/DevKit-Claude.git

# Add/edit configs
code xandru/my-config.md

# Commit and push
git add .
git commit -m "Add my config"
git push
```

Both team members have access to all configs - the folder structure just indicates authorship and PR ownership.
