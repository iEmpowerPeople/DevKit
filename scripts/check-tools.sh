#!/usr/bin/env bash
set -euo pipefail

# Checks required and optional tools for this repo.
# Pure diagnostics: prints guidance; installs nothing.

STRICT=0
if [[ "${1:-}" == "--strict" ]]; then
  STRICT=1
fi

OS="$(uname -s)"

case "$OS" in
  MINGW*|MSYS*|CYGWIN*)
    echo "Windows detected (Git Bash/MSYS/Cygwin)."
    echo "Use PowerShell instead: powershell -ExecutionPolicy Bypass -File .\\scripts\\check-tools.ps1"
    exit 0
    ;;
esac

have() {
  command -v "$1" >/dev/null 2>&1
}

if [[ "$OS" == "Darwin" ]]; then
  echo ""
  if have brew; then
    echo "(xapids suggestion) Install everything through homebrew. simplifies management and update processes"
  else
    echo "(xapids suggestion) Install Homebrew first, install everything through homebrew. simplifies management and update processes"
  fi
  echo "https://brew.sh/"
fi

print_header() {
  echo ""
  echo "$1"
  echo "----------------------------------------"
}

print_ok() {
  echo "[ok]  $1"
}

print_missing() {
  echo "[miss] $1"
}

hint() {
  local mac_hint="$1"
  local linux_hint="$2"
  local other_hint="$3"

  case "$OS" in
    Darwin)
      [[ -n "$mac_hint" ]] && echo "      macOS: $mac_hint"
      ;;
    Linux)
      [[ -n "$linux_hint" ]] && echo "      Linux: $linux_hint"
      ;;
    *)
      [[ -n "$other_hint" ]] && echo "      $other_hint"
      ;;
  esac
}

missing_required=0

print_header "Required"

if have git; then
  print_ok "git"
else
  print_missing "git"
  hint "xcode-select --install" \
       "sudo apt-get update && sudo apt-get install -y git" \
       "https://git-scm.com/downloads"
  missing_required=$((missing_required + 1))
fi

if have gh; then
  print_ok "gh"
else
  print_missing "gh"
  hint "brew install gh" \
       "sudo apt-get update && sudo apt-get install -y gh" \
       "https://cli.github.com/"
  missing_required=$((missing_required + 1))
fi

if have python3; then
  print_ok "python3"
else
  print_missing "python3"
  hint "brew install python" \
       "sudo apt-get update && sudo apt-get install -y python3 python3-pip" \
       "https://www.python.org/downloads/"
  missing_required=$((missing_required + 1))
fi

if python3 -m pip --version >/dev/null 2>&1; then
  print_ok "pip (python3 -m pip)"
else
  print_missing "pip (python3 -m pip)"
  hint "python3 -m ensurepip --upgrade" \
       "sudo apt-get update && sudo apt-get install -y python3-pip" \
       "https://pip.pypa.io/en/stable/installation/"
  missing_required=$((missing_required + 1))
fi

if python3 -c 'import yaml' >/dev/null 2>&1; then
  print_ok "pyyaml"
else
  print_missing "pyyaml"
  hint "python3 -m pip install --upgrade pyyaml" \
       "python3 -m pip install --upgrade pyyaml" \
       "https://pypi.org/project/PyYAML/"
  missing_required=$((missing_required + 1))
fi

print_header "Optional"

echo "Optional apps are listed in the catalogue under library/shared/extras/."

if have rg; then
  print_ok "rg (ripgrep)"
else
  print_missing "rg (ripgrep)"
  hint "brew install ripgrep" \
       "sudo apt-get update && sudo apt-get install -y ripgrep" \
       "Install ripgrep: https://github.com/BurntSushi/ripgrep#installation"
fi

if have fzf; then
  print_ok "fzf"
else
  print_missing "fzf"
  hint "brew install fzf" \
       "sudo apt-get update && sudo apt-get install -y fzf" \
       "Install fzf: https://github.com/junegunn/fzf#installation"
fi

if have bat; then
  print_ok "bat"
else
  print_missing "bat"
  hint "brew install bat" \
       "sudo apt-get update && sudo apt-get install -y bat" \
       "Install bat: https://github.com/sharkdp/bat#installation"
fi

if have yq; then
  print_ok "yq"
else
  print_missing "yq"
  hint "brew install yq" \
       "sudo apt-get update && sudo apt-get install -y yq" \
       "Install yq: https://github.com/mikefarah/yq#install"
fi

if have shellcheck; then
  print_ok "shellcheck"
else
  print_missing "shellcheck"
  hint "brew install shellcheck" \
       "sudo apt-get update && sudo apt-get install -y shellcheck" \
       "Install shellcheck: https://www.shellcheck.net/"
fi

if have shfmt; then
  print_ok "shfmt"
else
  print_missing "shfmt"
  hint "brew install shfmt" \
       "sudo apt-get update && sudo apt-get install -y shfmt" \
       "Install shfmt: https://github.com/mvdan/sh#shfmt"
fi

if have claude; then
  print_ok "claude (Claude Code CLI)"
else
  print_missing "claude (Claude Code CLI)"
  hint "Install Claude Code: https://code.claude.com/" \
       "Install Claude Code: https://code.claude.com/" \
       "Install Claude Code: https://code.claude.com/"
fi

if have opencode; then
  print_ok "opencode"
else
  print_missing "opencode"
  hint "Install Opencode: https://opencode.ai/" \
       "Install Opencode: https://opencode.ai/" \
       "Install Opencode: https://opencode.ai/"
fi

echo ""
if [[ $missing_required -eq 0 ]]; then
  echo "Check result: OK (required present)"
else
  echo "Check result: missing $missing_required required item(s)"
  if [[ $STRICT -eq 1 ]]; then
    exit 1
  fi
fi
