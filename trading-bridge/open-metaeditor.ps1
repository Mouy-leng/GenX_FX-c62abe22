# ================================================================================
# OPEN METAEDITOR - Script to open MetaEditor with PythonBridgeEA.mq5
# ================================================================================

Write-Host "Opening MetaEditor with PythonBridgeEA.mq5..." -ForegroundColor Cyan
Write-Host ""

# Find MetaTrader 5 installation
$mt5Paths = @(
    "C:\Program Files\MetaTrader 5 EXNESS",
    "C:\Program Files\MetaTrader 5",
    "C:\Program Files (x86)\MetaTrader 5"
)

$mt5Path = $null
foreach ($path in $mt5Paths) {
    if (Test-Path $path) {
        $mt5Path = $path
        break
    }
}

if (-not $mt5Path) {
    Write-Host "ERROR: MetaTrader 5 not found!" -ForegroundColor Red
    Write-Host "Please install MetaTrader 5 first." -ForegroundColor Yellow
    Write-Host "Download from: https://www.exness.com/mt5/" -ForegroundColor Cyan
    pause
    exit 1
}

Write-Host "Found MetaTrader 5 at: $mt5Path" -ForegroundColor Green

# Find MetaEditor
$metaEditorPath = Join-Path $mt5Path "metaeditor64.exe"
if (-not (Test-Path $metaEditorPath)) {
    $metaEditorPath = Join-Path $mt5Path "metaeditor.exe"
}

if (-not (Test-Path $metaEditorPath)) {
    Write-Host "ERROR: MetaEditor not found!" -ForegroundColor Red
    pause
    exit 1
}

# Find the MQL5 Expert Advisors directory
$dataFolder = Join-Path $env:APPDATA "MetaQuotes\Terminal"
$mql5Folders = Get-ChildItem -Path $dataFolder -Directory -ErrorAction SilentlyContinue | 
               Where-Object { Test-Path (Join-Path $_.FullName "MQL5") }

$expertsPath = $null
if ($mql5Folders) {
    $expertsPath = Join-Path $mql5Folders[0].FullName "MQL5\Experts"
}

if (-not $expertsPath) {
    # Create default path
    $expertsPath = Join-Path $mt5Path "MQL5\Experts"
}

# Ensure Experts directory exists
if (-not (Test-Path $expertsPath)) {
    New-Item -ItemType Directory -Path $expertsPath -Force | Out-Null
}

# Copy the EA to the Experts folder
$sourceEA = Join-Path $PSScriptRoot "MQL5\PythonBridgeEA.mq5"
$targetEA = Join-Path $expertsPath "PythonBridgeEA.mq5"

if (Test-Path $sourceEA) {
    Copy-Item -Path $sourceEA -Destination $targetEA -Force
    Write-Host "✓ Copied PythonBridgeEA.mq5 to Experts folder" -ForegroundColor Green
    Write-Host "  Location: $targetEA" -ForegroundColor Gray
} else {
    Write-Host "WARNING: PythonBridgeEA.mq5 not found in MQL5 folder" -ForegroundColor Yellow
    Write-Host "  Expected: $sourceEA" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Opening MetaEditor..." -ForegroundColor Cyan

# Open MetaEditor with the EA file
if (Test-Path $targetEA) {
    Start-Process -FilePath $metaEditorPath -ArgumentList "`"$targetEA`""
} else {
    Start-Process -FilePath $metaEditorPath
}

Write-Host ""
Write-Host "INSTRUCTIONS:" -ForegroundColor Yellow
Write-Host "1. PythonBridgeEA.mq5 should open in MetaEditor" -ForegroundColor White
Write-Host "2. Press F7 to compile" -ForegroundColor White
Write-Host "3. Wait for '0 errors, 0 warnings'" -ForegroundColor White
Write-Host "4. Close MetaEditor when compilation is complete" -ForegroundColor White
Write-Host ""
