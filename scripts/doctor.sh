#!/usr/bin/env bash
set -euo pipefail

# Checks for common CLIs used with this repo.
# This script does not install anything; it only prints guidance.

STRICT=0
if [[ "${1:-}" == "--strict" ]]; then
  STRICT=1
fi

OS="$(uname -s)"

have() {
  command -v "$1" >/dev/null 2>&1
}

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

missing_core=0

print_header "Core CLIs"

if have git; then
  print_ok "git"
else
  print_missing "git"
  hint "Install Xcode Command Line Tools (includes git): xcode-select --install" \
       "Install via your distro package manager (e.g. apt/yum/pacman)" \
       "Install git: https://git-scm.com/downloads"
  missing_core=$((missing_core + 1))
fi

if have python3; then
  print_ok "python3"
else
  print_missing "python3"
  hint "brew install python" \
       "sudo apt-get update && sudo apt-get install -y python3" \
       "Install Python: https://www.python.org/downloads/"
  missing_core=$((missing_core + 1))
fi

if have jq; then
  print_ok "jq"
else
  print_missing "jq"
  hint "brew install jq" \
       "sudo apt-get update && sudo apt-get install -y jq" \
       "Install jq: https://jqlang.github.io/jq/download/"
  missing_core=$((missing_core + 1))
fi

if have node; then
  print_ok "node"
else
  print_missing "node"
  hint "brew install node" \
       "sudo apt-get update && sudo apt-get install -y nodejs npm" \
       "Install Node.js: https://nodejs.org/en/download"
  missing_core=$((missing_core + 1))
fi

if have npx; then
  print_ok "npx"
else
  print_missing "npx (usually comes with npm/node)"
  hint "brew install node" \
       "sudo apt-get update && sudo apt-get install -y nodejs npm" \
       "Install Node.js (includes npm/npx): https://nodejs.org/en/download"
  missing_core=$((missing_core + 1))
fi

print_header "Optional CLIs"

if have gh; then
  print_ok "gh (GitHub CLI)"
else
  print_missing "gh (GitHub CLI)"
  hint "brew install gh" \
       "sudo apt-get update && sudo apt-get install -y gh" \
       "Install gh: https://cli.github.com/"
fi

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
if [[ $missing_core -eq 0 ]]; then
  echo "Doctor result: OK (core CLIs present)"
else
  echo "Doctor result: missing $missing_core core CLI(s)"
  if [[ $STRICT -eq 1 ]]; then
    exit 1
  fi
fi
