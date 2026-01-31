#!/usr/bin/env python3
"""
Update profile with all available tools from library
Preserves existing enabled/disabled states
Adds new tools with enabled: false
Removes tools that no longer exist
"""

import os
import sys
import yaml
import re
from pathlib import Path
from collections import OrderedDict

def load_schema(repo_root):
    """Load schema from config/schema.yml"""
    schema_path = repo_root / "config" / "schema.yml"
    with open(schema_path, 'r') as f:
        return yaml.safe_load(f)

def parse_frontmatter(file_path):
    """Extract YAML frontmatter from markdown file"""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Check for YAML frontmatter (between --- markers)
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
        if match:
            frontmatter_text = match.group(1)
            metadata = yaml.safe_load(frontmatter_text) or {}
            
            # Parse backtick-separated dependencies from strings
            for key in ['requires_extras', 'requires_scripts']:
                if key in metadata and isinstance(metadata[key], str):
                    # Extract items between backticks
                    items = re.findall(r'`([^`]+)`', metadata[key])
                    metadata[key] = items
            
            return metadata
        return {}
    except Exception:
        return {}

def find_tools_in_library(repo_root):
    """Scan library and return all tools organized by category"""
    schema = load_schema(repo_root)
    categories = [c for c in schema["categories"].keys() if c != "scripts"]
    scopes = [a["id"] for a in schema["authors"]]

    tools = {cat: [] for cat in categories}

    def category_path(scope, category):
        if category == "commands":
            return repo_root / "library" / scope / ".commands"
        return repo_root / "library" / scope / category
    
    for category in categories:
        for scope in scopes:
            lib_path = category_path(scope, category)
            if not lib_path.exists():
                continue

            # Most categories use a flat file structure:
            #   library/{author}/{category}/{tool-id}.md
            # Skills use a folder structure:
            #   library/{author}/skills/{skill-id}/SKILL.md
            if category in ("skills", "skills-user-only"):
                seen_ids = set()

                # Preferred structure: one folder per skill
                for skill_dir in sorted(lib_path.glob("*")):
                    if not skill_dir.is_dir() or skill_dir.name.startswith('.') or skill_dir.name.startswith('_'):
                        continue

                    skill_file = skill_dir / "SKILL.md"
                    if not skill_file.exists() or not skill_file.is_file():
                        continue

                    tool_id = skill_dir.name
                    seen_ids.add(tool_id)
                    
                    # Parse frontmatter for dependencies
                    metadata = parse_frontmatter(skill_file)
                    
                    tools[category].append({
                        'id': tool_id,
                        'author': scope,
                        'file': str(skill_file.relative_to(repo_root)),
                        'requires_extras': metadata.get('requires_extras', []),
                        'requires_scripts': metadata.get('requires_scripts', [])
                    })

                # Back-compat: legacy flat skills in library/{author}/skills/{id}.md
                for file_path in sorted(lib_path.glob("*")):
                    if (
                        file_path.is_file()
                        and not file_path.name.startswith('.')
                        and not file_path.name.startswith('_')
                        and file_path.name != '.gitkeep'
                    ):
                        tool_id = file_path.stem
                        if tool_id in seen_ids:
                            continue
                        
                        # Parse frontmatter for dependencies
                        metadata = parse_frontmatter(file_path)
                        
                        tools[category].append({
                            'id': tool_id,
                            'author': scope,
                            'file': str(file_path.relative_to(repo_root)),
                            'requires_extras': metadata.get('requires_extras', []),
                            'requires_scripts': metadata.get('requires_scripts', [])
                        })
            else:
                # Find all files (excluding hidden and .gitkeep)
                for file_path in sorted(lib_path.glob("*")):
                    if (
                        file_path.is_file()
                        and not file_path.name.startswith('.')
                        and not file_path.name.startswith('_')
                        and file_path.name != '.gitkeep'
                    ):
                        tool_id = file_path.stem  # filename without extension
                        
                        # Parse frontmatter for dependencies
                        metadata = parse_frontmatter(file_path)
                        
                        tools[category].append({
                            'id': tool_id,
                            'author': scope,
                            'file': str(file_path.relative_to(repo_root)),
                            'requires_extras': metadata.get('requires_extras', []),
                            'requires_scripts': metadata.get('requires_scripts', [])
                        })

    # Match README catalogue grouping for extras: -cli, then -gui, then other.
    def _extras_sort_key(tool):
        tool_id = tool.get('id', '')
        if tool_id.endswith('-cli'):
            group = 0
        elif tool_id.endswith('-gui'):
            group = 1
        else:
            group = 2
        return (group, tool_id, tool.get('author', ''))

    tools['extras'] = sorted(tools.get('extras', []), key=_extras_sort_key)
    
    return tools

def load_profile(profile_path, repo_root):
    """Load existing profile and extract enabled states"""
    if not profile_path.exists():
        return {}

    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f) or {}

    # Build map of tool_id -> enabled state for each category
    schema = load_schema(repo_root)
    categories = [c for c in schema["categories"].keys() if c != "scripts"]

    enabled_states = {}
    for category in categories:
        enabled_states[category] = {}
        if category in profile and isinstance(profile[category], list):
            for tool in profile[category]:
                if isinstance(tool, dict) and 'id' in tool and 'enabled' in tool:
                    enabled_states[category][tool['id']] = tool['enabled']

    return enabled_states

def write_profile(profile_path, profile_name, library_tools, existing_enabled, repo_root):
    """Write updated profile preserving enabled states"""

    schema = load_schema(repo_root)
    categories = [c for c in schema["categories"].keys() if c != "scripts"]

    lines = []
    lines.append(f"# {profile_name}'s DevKit Profile")
    lines.append("# AUTO-GENERATED from library/. Do not edit manually.")
    lines.append("# Run `make generate` to refresh after library changes.")
    lines.append("# Set enabled: true to sync a tool, enabled: false to skip it")
    lines.append("")

    for category in categories:
        lines.append(f"# {category.capitalize()}")
        lines.append(f"{category}:")
        
        tools = library_tools.get(category, [])
        if tools:
            prev_extras_group = None

            def _extras_group(tool_id: str) -> str:
                if tool_id.endswith('-cli'):
                    return 'cli'
                if tool_id.endswith('-gui'):
                    return 'gui'
                return 'other'

            for tool in tools:
                tool_id = tool['id']
                author = tool['author']
                requires_extras = tool.get('requires_extras', [])
                requires_scripts = tool.get('requires_scripts', [])

                # For extras, add an extra blank line between groups (-cli, -gui, other)
                if category == 'extras':
                    group = _extras_group(tool_id)
                    if prev_extras_group is not None and group != prev_extras_group:
                        lines.append("")
                    prev_extras_group = group
                
                # Preserve existing enabled state or default to false
                enabled = existing_enabled.get(category, {}).get(tool_id, False)
                enabled_str = "true" if enabled else "false"
                
                lines.append(f"  - id: {tool_id}")
                lines.append(f"    author: {author}")
                
                # Add dependency information if present (before enabled) - backtick format in quotes
                if requires_extras:
                    extras_list = '`, `'.join(requires_extras)
                    lines.append(f'    requires_extras: "`{extras_list}`"')
                if requires_scripts:
                    scripts_list = '`, `'.join(requires_scripts)
                    lines.append(f'    requires_scripts: "`{scripts_list}`"')
                
                # enabled is always last
                lines.append(f"    enabled: {enabled_str}")
                lines.append("")
        
        lines.append("")
    
    with open(profile_path, 'w') as f:
        f.write('\n'.join(lines))

def main():
    if len(sys.argv) != 2:
        print("Usage: update-profile.sh <profile-name>")
        print("Example: update-profile.sh xapids")
        sys.exit(1)
    
    profile_name = sys.argv[1]
    
    # Get repo root (script is in repo-library/scripts/ subdirectory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent
    
    profile_path = repo_root / "profiles" / f"{profile_name}.yml"
    
    if not profile_path.exists():
        print(f"Error: Profile not found: {profile_path}")
        sys.exit(1)
    
    print(f"Updating profile: {profile_path}")
    
    # Load existing enabled states
    existing_enabled = load_profile(profile_path, repo_root)

    # Scan library for all available tools
    library_tools = find_tools_in_library(repo_root)

    # Write updated profile
    write_profile(profile_path, profile_name, library_tools, existing_enabled, repo_root)
    
    print(f"✓ Profile updated: {profile_path}")
    print("  - Preserved all existing enabled/disabled settings")
    print("  - Added new tools with enabled: false")
    print("  - Removed tools no longer in library")

if __name__ == "__main__":
    main()
