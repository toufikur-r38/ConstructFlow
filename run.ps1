$ErrorActionPreference = "Stop"
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Virtual environment missing. Follow the setup steps in README.md first.'
}
& $pythonPath (Join-Path $PSScriptRoot 'main.py')
