# SPDX-FileCopyrightText: 2026 Golem Inc.
# SPDX-License-Identifier: GPL-2.0-or-later

$ErrorActionPreference = 'Stop'
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$enginePath = Join-Path $repoRoot 'build\gemrb\gemrb'
if (-not (Test-Path -LiteralPath $enginePath)) {
    throw 'GemRB WSL build is missing. Build it first using the instructions in terralum/README.md.'
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
