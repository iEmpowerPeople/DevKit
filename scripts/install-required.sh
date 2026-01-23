#!/usr/bin/env bash
set -euo pipefail

# Prints install/upgrade commands for missing/outdated REQUIRED dependencies.
# Does not execute installs.

OS="$(uname -s)"

case "$OS" in
  MINGW*|MSYS*|CYGWIN*)
    echo "Windows detected (Git Bash/MSYS/Cygwin)."
    echo "Use PowerShell instead: powershell -ExecutionPolicy Bypass -File .\\scripts\\install-required.ps1"
    exit 0
    ;;
esac

have() {
  command -v "$1" >/dev/null 2>&1
}

ver_ge() {
  # usage: ver_ge <have> <min>
  local have="$1"
  local min="$2"
  local h1=0 h2=0 h3=0 m1=0 m2=0 m3=0

  IFS='.' read -r h1 h2 h3 _ <<<"$have"
  IFS='.' read -r m1 m2 m3 _ <<<"$min"

  h1=${h1:-0}; h2=${h2:-0}; h3=${h3:-0}
  m1=${m1:-0}; m2=${m2:-0}; m3=${m3:-0}

  if ((h1 != m1)); then
    ((h1 > m1))
    return
  fi
  if ((h2 != m2)); then
    ((h2 > m2))
    return
  fi
  ((h3 >= m3))
}

print_cmds() {
  local title="$1"
  shift
  echo ""
  echo "$title"
  while [[ $# -gt 0 ]]; do
    echo "  $1"
    shift
  done
}

if [[ "$OS" == "Darwin" ]]; then
  if have brew; then
    print_cmds "(xapids suggestion) homebrew (recommended)" \
      "Install everything through homebrew. simplifies management and update processes" \
      "https://brew.sh/"
  else
    print_cmds "(xapids suggestion) homebrew (recommended)" \
      "Install Homebrew first, install everything through homebrew. simplifies management and update processes" \
      "https://brew.sh/"
  fi
fi

want_git="2.30.0"
want_py="3.9.0"
want_pyyaml="6.0.0"

missing=0

# git
if have git; then
  have_git="$(git --version | awk '{print $3}')"
  if ! ver_ge "$have_git" "$want_git"; then
    missing=$((missing + 1))
    case "$OS" in
      Darwin) print_cmds "git (upgrade)" "brew upgrade git" ;; 
      Linux)  print_cmds "git (upgrade)" "sudo apt-get update" "sudo apt-get install -y git" ;; 
      *)      print_cmds "git (upgrade)" "https://git-scm.com/downloads" ;;
    esac
  fi
else
  missing=$((missing + 1))
  case "$OS" in
    Darwin) print_cmds "git (install)" "xcode-select --install" "# or: brew install git" ;; 
    Linux)  print_cmds "git (install)" "sudo apt-get update" "sudo apt-get install -y git" ;; 
    *)      print_cmds "git (install)" "https://git-scm.com/downloads" ;;
  esac
fi

# gh
if ! have gh; then
  missing=$((missing + 1))
  case "$OS" in
    Darwin) print_cmds "gh (install)" "brew install gh" ;; 
    Linux)  print_cmds "gh (install)" "sudo apt-get update" "sudo apt-get install -y gh" "# or: https://cli.github.com/" ;; 
    *)      print_cmds "gh (install)" "https://cli.github.com/" ;;
  esac
fi

# python3
if have python3; then
  have_py="$(python3 -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
  if ! ver_ge "$have_py" "$want_py"; then
    missing=$((missing + 1))
    case "$OS" in
      Darwin) print_cmds "python3 (upgrade)" "brew upgrade python" ;; 
      Linux)  print_cmds "python3 (upgrade)" "sudo apt-get update" "sudo apt-get install -y python3 python3-pip" ;; 
      *)      print_cmds "python3 (upgrade)" "https://www.python.org/downloads/" ;;
    esac
  fi
else
  missing=$((missing + 1))
  case "$OS" in
    Darwin) print_cmds "python3 (install)" "brew install python" ;; 
    Linux)  print_cmds "python3 (install)" "sudo apt-get update" "sudo apt-get install -y python3 python3-pip" ;; 
    *)      print_cmds "python3 (install)" "https://www.python.org/downloads/" ;;
  esac
fi

# pip
if ! python3 -m pip --version >/dev/null 2>&1; then
  missing=$((missing + 1))
  case "$OS" in
    Darwin) print_cmds "pip (install)" "python3 -m ensurepip --upgrade" ;; 
    Linux)  print_cmds "pip (install)" "sudo apt-get update" "sudo apt-get install -y python3-pip" ;; 
    *)      print_cmds "pip (install)" "https://pip.pypa.io/en/stable/installation/" ;;
  esac
fi

# pyyaml
have_yaml_ver=""
if python3 -c 'import yaml; print(getattr(yaml, "__version__", ""))' >/dev/null 2>&1; then
  have_yaml_ver="$(python3 -c 'import yaml; print(getattr(yaml, "__version__", "0.0.0"))')"
fi
if [[ -z "$have_yaml_ver" ]] || ! ver_ge "$have_yaml_ver" "$want_pyyaml"; then
  missing=$((missing + 1))
  print_cmds "pyyaml (install/upgrade)" "python3 -m pip install --upgrade pyyaml"
fi

if [[ $missing -eq 0 ]]; then
  echo "All required dependencies present; nothing to install."
fi
