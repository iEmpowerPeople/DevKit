#!/usr/bin/env python3
"""
Validate all library files against config/schema.yml rules.
Exit 0 if valid, exit 1 if errors found.
"""

import os
import sys
import yaml
import re
from pathlib import Path

def load_schema(repo_root):
    schema_path = repo_root / "config" / "schema.yml"
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)

def parse_frontmatter(file_path):
    """Extract YAML frontmatter from markdown file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            return yaml.safe_load(match.group(1)) or {}
        return None  # No frontmatter found
    except Exception as e:
        return {'_error': str(e)}

def validate_library(repo_root):
    schema = load_schema(repo_root)
    errors = []

    authors = [a['id'] for a in schema['authors']]
    categories = schema['categories']

    def category_path(author, cat_name):
        if cat_name == "commands":
            return repo_root / "library" / author / ".commands"
        return repo_root / "library" / author / cat_name

    # Collect all extras and scripts for dependency validation
    all_extras = set()
    all_scripts = set()

    for author in authors:
        extras_path = repo_root / "library" / author / "extras"
        if extras_path.exists():
            for f in extras_path.glob("*.md"):
                all_extras.add(f.stem)

        scripts_path = repo_root / "library" / author / "scripts"
        if scripts_path.exists():
            for f in scripts_path.glob("*"):
                if f.is_file() and f.suffix in ['.py', '.sh']:
                    all_scripts.add(f.name)

    # Validate each category
    for cat_name, cat_config in categories.items():
        if cat_name == "scripts":
            # Validate scripts separately
            for author in authors:
                scripts_path = repo_root / "library" / author / "scripts"
                if not scripts_path.exists():
                    continue
                for script in scripts_path.glob("*"):
                    if not script.is_file() or script.suffix not in ['.py', '.sh']:
                        continue
                    # Check executable
                    if not os.access(script, os.X_OK):
                        errors.append(f"{script}: not executable (run chmod +x)")
                    # Check shebang
                    with open(script, 'r') as f:
                        first_line = f.readline().strip()
                    if not first_line.startswith('#!'):
                        errors.append(f"{script}: missing shebang line")
            continue

        for author in authors:
            if cat_name in ("skills", "skills-user-only"):
                cat_path = category_path(author, cat_name)
                if not cat_path.exists():
                    continue
                for skill_dir in cat_path.iterdir():
                    if not skill_dir.is_dir() or skill_dir.name.startswith('.'):
                        continue
                    skill_file = skill_dir / "SKILL.md"
                    if not skill_file.exists():
                        errors.append(f"{skill_dir}: missing SKILL.md")
                        continue
                    for subfolder in cat_config.get('required_subfolders', []):
                        subfolder_path = skill_dir / subfolder
                        if not subfolder_path.exists() or not subfolder_path.is_dir():
                            errors.append(f"{skill_dir}: missing required folder '{subfolder}'")
                    errors.extend(validate_file(skill_file, cat_config, all_extras, all_scripts))
            else:
                cat_path = category_path(author, cat_name)
                if not cat_path.exists():
                    continue
                for file in cat_path.glob("*.md"):
                    if file.name.startswith('.') or file.name.startswith('_'):
                        continue
                    errors.extend(validate_file(file, cat_config, all_extras, all_scripts))

    # Validate examples exist
    for cat_name, cat_config in categories.items():
        if 'example' in cat_config:
            example_id = cat_config['example']
            found = False
            for author in authors:
                if cat_name in ("skills", "skills-user-only"):
                    if (category_path(author, cat_name) / example_id / "SKILL.md").exists():
                        found = True
                        break
                elif cat_name == "scripts":
                    for ext in ['.py', '.sh']:
                        if (repo_root / "library" / author / "scripts" / f"{example_id}{ext}").exists():
                            found = True
                            break
                else:
                    if (category_path(author, cat_name) / f"{example_id}.md").exists():
                        found = True
                        break
            if not found:
                errors.append(f"Example '{example_id}' for category '{cat_name}' not found")

    return errors

def validate_file(file_path, cat_config, all_extras, all_scripts):
    errors = []

    if cat_config.get('requires_frontmatter', False):
        fm = parse_frontmatter(file_path)
        if fm is None:
            errors.append(f"{file_path}: missing required frontmatter")
            return errors
        if '_error' in fm:
            errors.append(f"{file_path}: frontmatter parse error: {fm['_error']}")
            return errors

        for field in cat_config.get('required_fields', []):
            if field not in fm or not fm[field]:
                errors.append(f"{file_path}: missing required field '{field}'")

        for field, required_value in cat_config.get('required_values', {}).items():
            if fm.get(field) != required_value:
                errors.append(f"{file_path}: field '{field}' must be {required_value}")

        # Validate dependency references
        if 'requires_extras' in fm:
            extras = fm['requires_extras']
            if isinstance(extras, str):
                extras = re.findall(r'`([^`]+)`', extras)
            for extra in extras:
                if extra not in all_extras:
                    errors.append(f"{file_path}: requires_extras references non-existent '{extra}'")

        if 'requires_scripts' in fm:
            scripts = fm['requires_scripts']
            if isinstance(scripts, str):
                scripts = re.findall(r'`([^`]+)`', scripts)
            for script in scripts:
                if script not in all_scripts:
                    errors.append(f"{file_path}: requires_scripts references non-existent '{script}'")

    return errors

def main():
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent

    print("Validating library against schema...")
    errors = validate_library(repo_root)

    if errors:
        print(f"\n❌ Validation failed: {len(errors)} error(s)\n")
        for error in errors:
            print(f"  • {error}")
        sys.exit(1)
    else:
        print("✓ Validation passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
