# ================================================================================
# START TRADING BRIDGE - Launch the Python bridge server
# ================================================================================

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "TRADING BRIDGE SERVER" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Find Python command
$pythonCommand = $null
try {
    $null = & python3 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonCommand = "python3"
    }
} catch {}

if (-not $pythonCommand) {
    try {
        $null = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = "python"
        }
    } catch {}
}

if (-not $pythonCommand) {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please run DEPLOY_NOW.ps1 first." -ForegroundColor Yellow
    pause
    exit 1
}

# Check if bridge_server.py exists
$bridgeScript = Join-Path $PSScriptRoot "bridge_server.py"
if (-not (Test-Path $bridgeScript)) {
    Write-Host "ERROR: bridge_server.py not found!" -ForegroundColor Red
    Write-Host "Expected: $bridgeScript" -ForegroundColor Gray
    pause
    exit 1
}

# Check if config exists
$configFile = Join-Path $PSScriptRoot "config\brokers.json"
if (-not (Test-Path $configFile)) {
    Write-Host "WARNING: config/brokers.json not found!" -ForegroundColor Yellow
    Write-Host "Please configure your broker credentials." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting Trading Bridge on port 5500..." -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the bridge" -ForegroundColor Yellow
Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the bridge server
Set-Location $PSScriptRoot
& $pythonCommand bridge_server.py
