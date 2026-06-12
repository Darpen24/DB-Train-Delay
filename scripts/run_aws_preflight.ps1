$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $projectRoot ".venv\Scripts\python.exe"
$dbtProject = Join-Path $projectRoot "dbt\db_train_delay"
$profilesExample = Join-Path $dbtProject "profiles.yml.example"
$profilesTarget = Join-Path $dbtProject "profiles.yml"

if (-not (Test-Path $pythonExe)) {
    py -3.10 -m venv (Join-Path $projectRoot ".venv")
}

& $pythonExe -m pip install --upgrade pip setuptools wheel
& $pythonExe -m pip install -r (Join-Path $projectRoot "requirements.txt")
& $pythonExe -m pip install dbt-core dbt-duckdb dbt-athena-community

if (-not (Test-Path $profilesTarget)) {
    Copy-Item $profilesExample $profilesTarget
}

Push-Location $dbtProject
& $pythonExe -m dbt deps --profiles-dir .
& $pythonExe -m dbt seed --profiles-dir .
& $pythonExe -m dbt parse --profiles-dir .
Pop-Location

terraform -chdir=(Join-Path $projectRoot "infra\terraform") fmt -check

Write-Host "AWS preflight checks completed."
Write-Host "Next step: add terraform.tfvars and run terraform init/apply with AWS credentials."
