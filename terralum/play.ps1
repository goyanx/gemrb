# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$enginePath = Join-Path $repoRoot 'build\gemrb\gemrb'
if (-not (Test-Path -LiteralPath $enginePath)) {
    throw 'GemRB WSL build is missing. Build it first using the instructions in terralum/README.md.'
}

$runningGemRB = @(wsl --exec pgrep -a -x gemrb 2>$null)
$pgrepExit = $LASTEXITCODE
if ($pgrepExit -eq 0 -and $runningGemRB.Count -gt 0) {
    $runningList = $runningGemRB -join [Environment]::NewLine
    throw "GemRB is already running in WSL. Close the existing session before starting another:`n$runningList"
}
if ($pgrepExit -gt 1) {
    throw 'Could not check for an existing GemRB process in WSL; refusing to launch a duplicate.'
}

Push-Location $repoRoot
try {
    python tools/terralum/build_game.py
    if ($LASTEXITCODE -ne 0) { throw 'Could not assemble the Terralum game pack.' }
    wsl --cd $repoRoot --exec ./build/gemrb/gemrb -c terralum/build/terralum-wsl.cfg
    if ($LASTEXITCODE -ne 0) { throw "GemRB exited with code $LASTEXITCODE." }
} finally {
    Pop-Location
}
