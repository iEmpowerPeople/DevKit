.PHONY: help generate generate-profiles generate-readme validate check clean

# Default target
help:
	@echo "DevKit Makefile"
	@echo ""
	@echo "Commands:"
	@echo "  make generate   - Regenerate all derived files (profiles, README)"
	@echo "  make validate   - Validate library files against schema"
	@echo "  make check      - Generate + validate + verify no uncommitted changes"
	@echo "  make clean      - Remove temporary files"
	@echo ""

# Read authors from schema (avoids hardcoding profile names)
AUTHORS := $(shell yq -r '.authors[].id' config/schema.yml 2>/dev/null || echo "shared xapids tihany7")

# Regenerate all derived files
generate: generate-profiles generate-readme
	@echo "✓ All derived files regenerated"

generate-profiles:
	@echo "Regenerating profiles..."
	@for author in $(AUTHORS); do \
		if [ -f "profiles/$${author}.yml" ]; then \
			python3 repo-library/scripts/devkit-update-profile.py $$author; \
		fi; \
	done

generate-readme:
	@echo "Regenerating README catalogue..."
	@bash repo-library/scripts/devkit-gen-catalogue.sh

# Validate library against schema
validate:
	@python3 repo-library/scripts/devkit-validate-library.py

# Full check: validate, generate, then verify no uncommitted changes
check: validate generate
	@echo "Checking for uncommitted changes..."
	@if ! git diff --quiet; then \
		echo ""; \
		echo "❌ ERROR: Derived files are out of sync!"; \
		echo ""; \
		echo "Changed files:"; \
		git diff --name-only; \
		echo ""; \
		echo "Run 'make generate' and commit the changes."; \
		exit 1; \
	fi
	@echo "✓ All files in sync"

clean:
	@rm -f README.md.tmp
	@echo "✓ Cleaned temporary files"
