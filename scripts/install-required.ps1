$ErrorActionPreference = 'Stop'

# Prints install/upgrade commands for missing/outdated REQUIRED dependencies.
# Does not execute installs.

function CmdExists($name) {
  $null -ne (Get-Command $name -ErrorAction SilentlyContinue)
}

function PrintBlock($title, [string[]]$lines) {
  Write-Host ""
  Write-Host $title
  foreach ($l in $lines) { Write-Host "  $l" }
}

function ParseVersion($text) {
  $m = [regex]::Match($text, '(\d+\.\d+\.\d+)')
  if ($m.Success) { return [version]$m.Groups[1].Value }
  return $null
}

$wantGit = [version]'2.30.0'
$wantPy = [version]'3.9.0'
$wantPyYaml = [version]'6.0.0'

$missing = 0

$pyCmd = $null
if (CmdExists 'python') { $pyCmd = 'python' }
elseif (CmdExists 'python3') { $pyCmd = 'python3' }

# git
if (CmdExists 'git') {
  $haveGit = ParseVersion (git --version)
  if ($haveGit -and $haveGit -lt $wantGit) {
    $missing++
    PrintBlock 'git (upgrade)' @('winget upgrade --id Git.Git')
  }
} else {
  $missing++
  PrintBlock 'git (install)' @('winget install --id Git.Git', '# or: https://git-scm.com/downloads')
}

# gh
if (-not (CmdExists 'gh')) {
  $missing++
  PrintBlock 'gh (install)' @('winget install --id GitHub.cli', '# or: https://cli.github.com/')
}

# python
if ($pyCmd) {
  $havePy = ParseVersion (& $pyCmd --version)
  if ($havePy -and $havePy -lt $wantPy) {
    $missing++
    PrintBlock "$pyCmd (upgrade)" @('winget upgrade --id Python.Python.3')
  }
} else {
  $missing++
  PrintBlock 'python (install)' @('winget install --id Python.Python.3', '# or: https://www.python.org/downloads/')
}

# pip
if ($pyCmd) {
  try {
    & $pyCmd -m pip --version | Out-Null
  } catch {
    $missing++
    PrintBlock 'pip (install/upgrade)' @("$pyCmd -m ensurepip --upgrade", "$pyCmd -m pip install --upgrade pip")
  }

  # pyyaml
  $haveYaml = $null
  try {
    $haveYaml = & $pyCmd -c "import yaml; print(getattr(yaml,'__version__','0.0.0'))"
  } catch {
    $haveYaml = $null
  }
  if ($haveYaml) {
    $haveYamlVer = ParseVersion $haveYaml
    if (-not $haveYamlVer -or $haveYamlVer -lt $wantPyYaml) {
      $missing++
      PrintBlock 'pyyaml (upgrade)' @("$pyCmd -m pip install --upgrade pyyaml")
    }
  } else {
    $missing++
    PrintBlock 'pyyaml (install)' @("$pyCmd -m pip install --upgrade pyyaml")
  }
}

if ($missing -eq 0) {
  Write-Host "All required dependencies present; nothing to install." 
}
