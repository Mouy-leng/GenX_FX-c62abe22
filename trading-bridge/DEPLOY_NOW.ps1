# ================================================================================
# TRADING BRIDGE - AUTOMATED DEPLOYMENT SCRIPT
# ================================================================================
# Device: NUNA 💻 | User: @mouyleng 🧑‍💻 | Org: @A6-9V 🏙️
# VPS: Singapore 09 | Trading: 24/7
# ================================================================================

Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "TRADING BRIDGE - AUTOMATED DEPLOYMENT" -ForegroundColor Cyan
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "✓ Running as Administrator" -ForegroundColor Green
Write-Host ""

# ================================================================================
# STEP 1: CHECK PYTHON INSTALLATION
# ================================================================================
Write-Host "STEP 1: Checking Python installation..." -ForegroundColor Cyan

$pythonCommand = $null
$pythonVersion = $null

# Try python3 first
try {
    $pythonVersion = & python3 --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        $pythonCommand = "python3"
    }
} catch {}

# Try python if python3 not found
if (-not $pythonCommand) {
    try {
        $pythonVersion = & python --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCommand = "python"
        }
    } catch {}
}

if ($pythonCommand) {
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found. Installing Python..." -ForegroundColor Yellow
    
    # Download Python installer
    $pythonInstaller = "$env:TEMP\python-installer.exe"
    $pythonUrl = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
    
    Write-Host "  Downloading Python 3.11.7..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $pythonUrl -OutFile $pythonInstaller
    
    Write-Host "  Installing Python..." -ForegroundColor Yellow
    Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet", "InstallAllUsers=1", "PrependPath=1" -Wait
    
    # Refresh environment variables
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")
    
    # Check again
    try {
        $pythonVersion = & python --version 2>&1
        $pythonCommand = "python"
        Write-Host "✓ Python installed successfully: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "✗ Python installation failed. Please install Python manually." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# ================================================================================
# STEP 2: INSTALL PYTHON DEPENDENCIES
# ================================================================================
Write-Host "STEP 2: Installing Python dependencies..." -ForegroundColor Cyan

$requirementsFile = Join-Path $PSScriptRoot "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Host "  Installing packages from requirements.txt..." -ForegroundColor Yellow
    & $pythonCommand -m pip install --upgrade pip --quiet
    & $pythonCommand -m pip install -r $requirementsFile --quiet
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        Write-Host "  Run manually: pip install -r requirements.txt" -ForegroundColor Yellow
    }
} else {
    Write-Host "✗ requirements.txt not found!" -ForegroundColor Red
}

Write-Host ""

# ================================================================================
# STEP 3: CREATE CONFIGURATION FILES
# ================================================================================
Write-Host "STEP 3: Creating configuration files..." -ForegroundColor Cyan

$configDir = Join-Path $PSScriptRoot "config"
if (-not (Test-Path $configDir)) {
    New-Item -ItemType Directory -Path $configDir -Force | Out-Null
}

$brokersConfig = Join-Path $configDir "brokers.json"
if (-not (Test-Path $brokersConfig)) {
    $defaultConfig = @{
        "EXNESS" = @{
            "account_id" = "YOUR_ACCOUNT_ID"
            "api_key" = "YOUR_API_KEY"
            "api_secret" = "YOUR_API_SECRET"
            "api_url" = "https://api.exness.com"
            "enabled" = $false
        }
    } | ConvertTo-Json -Depth 4
    
    Set-Content -Path $brokersConfig -Value $defaultConfig
    Write-Host "✓ Created config/brokers.json (template)" -ForegroundColor Green
    Write-Host "  IMPORTANT: Edit this file with your API credentials!" -ForegroundColor Yellow
} else {
    Write-Host "✓ config/brokers.json already exists" -ForegroundColor Green
}

# Create logs directory
$logsDir = Join-Path $PSScriptRoot "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Write-Host "✓ Created logs directory" -ForegroundColor Green
} else {
    Write-Host "✓ logs directory already exists" -ForegroundColor Green
}

Write-Host ""

# ================================================================================
# STEP 4: CONFIGURE WINDOWS FIREWALL
# ================================================================================
Write-Host "STEP 4: Configuring Windows Firewall (Port 5500)..." -ForegroundColor Cyan

try {
    # Check if rule already exists
    $existingRule = Get-NetFirewallRule -DisplayName "Trading Bridge Port 5500" -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "✓ Firewall rule already exists" -ForegroundColor Green
    } else {
        New-NetFirewallRule -DisplayName "Trading Bridge Port 5500" `
                            -Direction Inbound `
                            -LocalPort 5500 `
                            -Protocol TCP `
                            -Action Allow | Out-Null
        Write-Host "✓ Firewall rule created for port 5500" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ Failed to configure firewall: $_" -ForegroundColor Red
    Write-Host "  You may need to configure firewall manually" -ForegroundColor Yellow
}

Write-Host ""

# ================================================================================
# STEP 5: CHECK METATRADER 5 INSTALLATION
# ================================================================================
Write-Host "STEP 5: Checking MetaTrader 5 installation..." -ForegroundColor Cyan

$mt5Paths = @(
    "C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe",
    "C:\Program Files\MetaTrader 5\terminal64.exe",
    "C:\Program Files (x86)\MetaTrader 5\terminal64.exe"
)

$mt5Found = $false
foreach ($path in $mt5Paths) {
    if (Test-Path $path) {
        Write-Host "✓ MetaTrader 5 found at: $path" -ForegroundColor Green
        $mt5Found = $true
        break
    }
}

if (-not $mt5Found) {
    Write-Host "✗ MetaTrader 5 not found" -ForegroundColor Yellow
    Write-Host "  Download from: https://www.exness.com/mt5/" -ForegroundColor Yellow
    Write-Host "  Install to: C:\Program Files\MetaTrader 5 EXNESS" -ForegroundColor Yellow
}

Write-Host ""

# ================================================================================
# DEPLOYMENT COMPLETE
# ================================================================================
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Configure API Credentials:" -ForegroundColor White
Write-Host "   notepad config\brokers.json" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Install MetaTrader 5 (if not installed):" -ForegroundColor White
Write-Host "   https://www.exness.com/mt5/" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Compile the Expert Advisor:" -ForegroundColor White
Write-Host "   .\open-metaeditor.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Start the Trading Bridge:" -ForegroundColor White
Write-Host "   .\start-bridge.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. Attach EA to MT5 chart" -ForegroundColor White
Write-Host ""
Write-Host "=================================================================================" -ForegroundColor Cyan
Write-Host ""

pause
