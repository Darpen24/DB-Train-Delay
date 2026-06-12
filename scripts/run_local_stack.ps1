$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    py -3.10 -m venv (Join-Path $projectRoot ".venv")
}

& $pythonExe -m pip install --upgrade pip setuptools wheel
& $pythonExe -m pip install -r (Join-Path $projectRoot "requirements.txt")
& $pythonExe (Join-Path $projectRoot "scripts\run_local_pipeline.py")
& $pythonExe -m pytest
& $pythonExe (Join-Path $projectRoot "scripts\generate_readme_assets.py")

Write-Host "Local stack completed successfully."
Write-Host "Run the dashboard with: .\.venv\Scripts\python.exe -m streamlit run dashboard\app.py"
