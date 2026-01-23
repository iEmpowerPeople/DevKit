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
from pathlib import Path
from collections import OrderedDict

def find_tools_in_library(repo_root):
    """Scan library and return all tools organized by category"""
    categories = ["agents", "skills", "commands", "mcp", "extras"]
    scopes = ["shared", "xapids", "tihany7"]
    
    tools = {cat: [] for cat in categories}
    
    for category in categories:
        for scope in scopes:
            lib_path = repo_root / "library" / scope / category
            if not lib_path.exists():
                continue

            # Most categories use a flat file structure:
            #   library/{author}/{category}/{tool-id}.md
            # Skills use a folder structure:
            #   library/{author}/skills/{skill-id}/SKILL.md
            if category == "skills":
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
                    tools[category].append({
                        'id': tool_id,
                        'author': scope,
                        'file': str(skill_file.relative_to(repo_root))
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
                        tools[category].append({
                            'id': tool_id,
                            'author': scope,
                            'file': str(file_path.relative_to(repo_root))
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
                        tools[category].append({
                            'id': tool_id,
                            'author': scope,
                            'file': str(file_path.relative_to(repo_root))
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

def load_profile(profile_path):
    """Load existing profile and extract enabled states"""
    if not profile_path.exists():
        return {}
    
    with open(profile_path, 'r') as f:
        profile = yaml.safe_load(f) or {}
    
    # Build map of tool_id -> enabled state for each category
    enabled_states = {}
    for category in ["agents", "skills", "commands", "mcp", "extras"]:
        enabled_states[category] = {}
        if category in profile and isinstance(profile[category], list):
            for tool in profile[category]:
                if isinstance(tool, dict) and 'id' in tool and 'enabled' in tool:
                    enabled_states[category][tool['id']] = tool['enabled']
    
    return enabled_states

def write_profile(profile_path, profile_name, library_tools, existing_enabled):
    """Write updated profile preserving enabled states"""
    
    lines = []
    lines.append(f"# {profile_name}'s DevKit Profile")
    lines.append("# Personal tool selections from the library")
    lines.append("# Browse README.md to see all available tools")
    lines.append("# Set enabled: true to sync a tool, enabled: false to skip it")
    lines.append("# author: indicates who maintains the tool (shared, xapids, tihany7)")
    lines.append("")
    
    for category in ["agents", "skills", "commands", "mcp", "extras"]:
        lines.append(f"# {category.capitalize()}")
        lines.append(f"{category}:")
        
        tools = library_tools.get(category, [])
        if tools:
            for tool in tools:
                tool_id = tool['id']
                author = tool['author']
                
                # Preserve existing enabled state or default to false
                enabled = existing_enabled.get(category, {}).get(tool_id, False)
                enabled_str = "true" if enabled else "false"
                
                lines.append(f"  - id: {tool_id}")
                lines.append(f"    author: {author}")
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
    
    # Get repo root (script is in scripts/ subdirectory)
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    
    profile_path = repo_root / "profiles" / f"{profile_name}.yml"
    
    if not profile_path.exists():
        print(f"Error: Profile not found: {profile_path}")
        sys.exit(1)
    
    print(f"Updating profile: {profile_path}")
    
    # Load existing enabled states
    existing_enabled = load_profile(profile_path)
    
    # Scan library for all available tools
    library_tools = find_tools_in_library(repo_root)
    
    # Write updated profile
    write_profile(profile_path, profile_name, library_tools, existing_enabled)
    
    print(f"✓ Profile updated: {profile_path}")
    print("  - Preserved all existing enabled/disabled settings")
    print("  - Added new tools with enabled: false")
    print("  - Removed tools no longer in library")

if __name__ == "__main__":
    main()
