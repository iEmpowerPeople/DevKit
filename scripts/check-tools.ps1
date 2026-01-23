$ErrorActionPreference = 'Stop'

# Checks required and optional tools for this repo.
# Pure diagnostics: prints guidance; installs nothing.

$strict = $false
if ($args.Count -gt 0 -and $args[0] -eq '--strict') { $strict = $true }

function CmdExists($name) {
  $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
}

function PrintHeader($title) {
  Write-Host ""
  Write-Host $title
  Write-Host '----------------------------------------'
}

function Ok($name) { Write-Host "[ok]  $name" }
function Miss($name) { Write-Host "[miss] $name" }

function Hint([string[]]$lines) {
  foreach ($l in $lines) { Write-Host "      $l" }
}

$missingRequired = 0

$pyCmd = $null
if (CmdExists 'py') { $pyCmd = 'py' }
elseif (CmdExists 'python') { $pyCmd = 'python' }
elseif (CmdExists 'python3') { $pyCmd = 'python3' }

PrintHeader 'Required'

if (CmdExists 'git') {
  Ok 'git'
} else {
  Miss 'git'
  Hint @('winget install -e --id Git.Git', 'or: https://git-scm.com/downloads')
  $missingRequired++
}

if (CmdExists 'gh') {
  Ok 'gh'
} else {
  Miss 'gh'
  Hint @('winget install -e --id GitHub.cli', 'or: https://cli.github.com/')
  $missingRequired++
}

if ($pyCmd) {
  Ok $pyCmd
} else {
  Miss 'python (py/python)'
  Hint @('winget install -e --id Python.Python.3', 'or: https://www.python.org/downloads/')
  $missingRequired++
}

if ($pyCmd) {
  try {
    if ($pyCmd -eq 'py') { & py -3 -m pip --version | Out-Null }
    else { & $pyCmd -m pip --version | Out-Null }
    Ok 'pip'
  } catch {
    Miss 'pip'
    if ($pyCmd -eq 'py') { Hint @('py -3 -m ensurepip --upgrade', 'py -3 -m pip install --upgrade pip') }
    else { Hint @("$pyCmd -m ensurepip --upgrade", "$pyCmd -m pip install --upgrade pip") }
    $missingRequired++
  }

  try {
    if ($pyCmd -eq 'py') { & py -3 -c "import yaml" | Out-Null }
    else { & $pyCmd -c "import yaml" | Out-Null }
    Ok 'pyyaml'
  } catch {
    Miss 'pyyaml'
    if ($pyCmd -eq 'py') { Hint @('py -3 -m pip install --upgrade pyyaml') }
    else { Hint @("$pyCmd -m pip install --upgrade pyyaml") }
    $missingRequired++
  }
}

PrintHeader 'Optional'
Write-Host 'Optional apps are listed in the catalogue under library/shared/extras/.'

if (CmdExists 'rg') { Ok 'rg (ripgrep)' } else { Miss 'rg (ripgrep)'; Hint @('winget install -e --id BurntSushi.ripgrep', 'or: https://github.com/BurntSushi/ripgrep#installation') }
if (CmdExists 'fzf') { Ok 'fzf' } else { Miss 'fzf'; Hint @('winget install -e --id junegunn.fzf', 'or: https://github.com/junegunn/fzf#installation') }
if (CmdExists 'bat') { Ok 'bat' } else { Miss 'bat'; Hint @('winget install -e --id sharkdp.bat', 'or: https://github.com/sharkdp/bat') }
if (CmdExists 'yq') { Ok 'yq' } else { Miss 'yq'; Hint @('winget install -e --id mikefarah.yq', 'or: https://github.com/mikefarah/yq#install') }
if (CmdExists 'shellcheck') { Ok 'shellcheck' } else { Miss 'shellcheck'; Hint @('winget install -e --id koalaman.shellcheck', 'or: https://www.shellcheck.net/') }
if (CmdExists 'shfmt') { Ok 'shfmt' } else { Miss 'shfmt'; Hint @('winget install -e --id mvdan.shfmt', 'or: https://github.com/mvdan/sh#shfmt') }
if (CmdExists 'node') { Ok 'node' } else { Miss 'node'; Hint @('winget install -e --id OpenJS.NodeJS.LTS', 'purpose: needed for npx-based MCP servers') }
if (CmdExists 'claude') { Ok 'claude (Claude Code CLI)' } else { Miss 'claude (Claude Code CLI)'; Hint @('Install Claude Code: https://code.claude.com/') }
if (CmdExists 'opencode') { Ok 'opencode' } else { Miss 'opencode'; Hint @('Install OpenCode: https://opencode.ai/') }

Write-Host ""
if ($missingRequired -eq 0) {
  Write-Host 'Check result: OK (required present)'
} else {
  Write-Host "Check result: missing $missingRequired required item(s)"
  if ($strict) { exit 1 }
}
