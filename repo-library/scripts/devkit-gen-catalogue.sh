#!/bin/bash
set -euo pipefail

# Update README.md with tool catalogue from library folder structure
# Groups by category, lists tools alphabetically with author info and descriptions
# Descriptions are aligned for readability

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

SCHEMA_FILE="${REPO_ROOT}/config/schema.yml"
README_FILE="README.md"
TEMP_FILE="${README_FILE}.tmp"
CATALOGUE_MARKER="<!-- AUTO-GENERATED CATALOGUE -->"

# Extract description from YAML frontmatter
extract_description() {
    local file=$1
    local desc=""

    # Check if file has YAML frontmatter (starts with ---)
    if head -1 "$file" | grep -q '^---$'; then
        # Extract frontmatter and get description field
        desc=$(sed -n '/^---$/,/^---$/p' "$file" | yq -r '.description // ""' 2>/dev/null || echo "")
    fi

    echo "$desc"
}

# Function to scan library and collect all tools by category
collect_tools() {
    local category=$1

    # Read scopes from schema
    local scopes
    scopes=($(yq -r '.authors[].id' "$SCHEMA_FILE"))

    for scope in "${scopes[@]}"; do
        local path
        if [[ "$category" == "commands" ]]; then
            path="library/${scope}/.commands"
        else
            path="library/${scope}/${category}"
        fi
        if [[ ! -d "$path" ]]; then
            continue
        fi

        if [[ "$category" == "skills" || "$category" == "skills-user-only" ]]; then
            # Skills are stored as:
            #   library/{author}/skills/{skill-id}/SKILL.md
            find "$path" -type f -name 'SKILL.md' ! -path '*/.*' ! -path '*/_*' ! -name '.gitkeep' | while read -r file; do
                local id
                id=$(basename "$(dirname "$file")")
                local relpath="${file#./}"
                local desc
                desc=$(extract_description "$file")

                # Output as: tool_id|author|filepath|description
                echo "${id}|${scope}|${relpath}|${desc}"
            done
        else
            # Find all files (excluding .gitkeep, hidden files, and _private docs)
            find "$path" -type f ! -name '.*' ! -name '.gitkeep' ! -name '_*' | while read -r file; do
                local basename=$(basename "$file")
                local id="${basename%.*}"
                local relpath="${file#./}"
                local desc
                desc=$(extract_description "$file")

                # Output as: tool_id|author|filepath|description
                echo "${id}|${scope}|${relpath}|${desc}"
            done
        fi
    done | sort -t'|' -k1,1
}

# Helper to capitalize first letter
capitalize() {
    echo "$(echo "${1:0:1}" | tr '[:lower:]' '[:upper:]')${1:1}"
}

# Calculate max tool name length from a tools list
get_max_name_length() {
    local tools="$1"
    local max_len=0
    while IFS='|' read -r tool_id author filepath desc; do
        local len=${#tool_id}
        if (( len > max_len )); then
            max_len=$len
        fi
    done <<< "$tools"
    echo "$max_len"
}

# Format a tool line with aligned description
format_tool_line() {
    local tool_id="$1"
    local desc="$2"
    local max_len="$3"
    local min_spacing=8

    # Calculate padding needed
    local name_len=${#tool_id}
    local padding=$((max_len - name_len + min_spacing))

    if [[ -n "$desc" ]]; then
        # Create spaces for padding
        local spaces=""
        for ((i=0; i<padding; i++)); do
            spaces+=" "
        done
        echo "  <li><strong>${tool_id}</strong>${spaces}${desc}</li>"
    else
        echo "  <li><strong>${tool_id}</strong></li>"
    fi
}

# Extract everything before the catalogue marker (or whole file if no marker)
if grep -q "$CATALOGUE_MARKER" "$README_FILE"; then
    sed "/$CATALOGUE_MARKER/q" "$README_FILE" > "$TEMP_FILE"
else
    # No marker exists, add it at the end
    cat "$README_FILE" > "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"
    echo "$CATALOGUE_MARKER" >> "$TEMP_FILE"
fi

# Build catalogue section
cat >> "$TEMP_FILE" << 'EOF'

<!-- AUTO-GENERATED: Do not edit this section manually. Run `make generate` to update. -->

## Available Tools

Auto-generated list of all tools in the library. Your profile is automatically updated with these tools.

EOF

# Read categories from schema (excluding scripts)
CATEGORIES=($(yq -r '.categories | keys | .[] | select(. != "scripts")' "$SCHEMA_FILE"))

for category in "${CATEGORIES[@]}"; do
    cat_title=$(capitalize "$category")
    echo "" >> "$TEMP_FILE"
    echo "### ${cat_title}" >> "$TEMP_FILE"
    echo "" >> "$TEMP_FILE"

    # Collect all tools for this category
    tools=$(collect_tools "$category")

    if [[ -n "$tools" ]]; then
        if [[ "$category" == "extras" ]]; then
            clis=$(echo "$tools" | awk -F'|' '$1 ~ /-cli$/ {print}')
            guis=$(echo "$tools" | awk -F'|' '$1 ~ /-gui$/ {print}')
            other=$(echo "$tools" | awk -F'|' '$1 !~ /-cli$/ && $1 !~ /-gui$/ {print}')

            if [[ -n "$clis" ]]; then
                max_len=$(get_max_name_length "$clis")
                echo "<ul>" >> "$TEMP_FILE"
                while IFS='|' read -r tool_id author filepath desc; do
                    format_tool_line "$tool_id" "$desc" "$max_len" >> "$TEMP_FILE"
                done <<< "$clis"
                echo "</ul>" >> "$TEMP_FILE"
            fi

            if [[ -n "$guis" ]]; then
                [[ -n "$clis" ]] && echo "" >> "$TEMP_FILE"
                max_len=$(get_max_name_length "$guis")
                echo "<ul>" >> "$TEMP_FILE"
                while IFS='|' read -r tool_id author filepath desc; do
                    format_tool_line "$tool_id" "$desc" "$max_len" >> "$TEMP_FILE"
                done <<< "$guis"
                echo "</ul>" >> "$TEMP_FILE"
            fi

            if [[ -n "$other" ]]; then
                [[ -n "$clis" || -n "$guis" ]] && echo "" >> "$TEMP_FILE"
                max_len=$(get_max_name_length "$other")
                echo "<ul>" >> "$TEMP_FILE"
                while IFS='|' read -r tool_id author filepath desc; do
                    format_tool_line "$tool_id" "$desc" "$max_len" >> "$TEMP_FILE"
                done <<< "$other"
                echo "</ul>" >> "$TEMP_FILE"
            fi
        else
            max_len=$(get_max_name_length "$tools")
            echo "<ul>" >> "$TEMP_FILE"
            while IFS='|' read -r tool_id author filepath desc; do
                format_tool_line "$tool_id" "$desc" "$max_len" >> "$TEMP_FILE"
            done <<< "$tools"
            echo "</ul>" >> "$TEMP_FILE"
        fi
    else
        echo "*No items yet*" >> "$TEMP_FILE"
    fi

    echo "" >> "$TEMP_FILE"
done

# Add footer
cat >> "$TEMP_FILE" << EOF

---

*Last updated: $(date -u +"%Y-%m-%d") • Auto-generated by \`repo-library/scripts/devkit-gen-catalogue.sh\`*
EOF

# Replace README
mv "$TEMP_FILE" "$README_FILE"

echo "✓ README.md updated with tool catalogue"
