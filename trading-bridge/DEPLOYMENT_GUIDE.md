# Trading Bridge - Deployment Guide

## Architecture Overview

The Trading Bridge system consists of three main components:

1. **MetaTrader 5 Expert Advisor (PythonBridgeEA.mq5)**
   - Runs inside MT5 platform
   - Connects to Python bridge via TCP socket
   - Sends trading signals and receives confirmations

2. **Python Bridge Server (bridge_server.py)**
   - Runs as a standalone Python application
   - Listens on port 5500 for MT5 connections
   - Communicates with broker APIs (Exness)
   - Handles trade execution and account management

3. **Broker API Integration**
   - Connects to broker's REST/WebSocket API
   - Executes trades, manages positions
   - Retrieves account information

```
┌─────────────────┐      TCP Socket      ┌──────────────────┐      REST API      ┌─────────────┐
│  MetaTrader 5   │◄────────────────────►│  Python Bridge   │◄──────────────────►│  Exness API │
│  (PythonBridgeEA)│      Port 5500       │  (bridge_server) │    HTTPS/WSS       │             │
└─────────────────┘                       └──────────────────┘                     └─────────────┘
```

---

## System Requirements

### VPS Specifications
- **OS:** Windows Server 2019/2022 or Windows 10/11
- **CPU:** 2+ cores
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 50GB SSD
- **Network:** 100 Mbps minimum
- **Location:** Singapore preferred (low latency to Exness)

### Software Requirements
- **Python:** 3.11 or higher
- **MetaTrader 5:** Latest version from Exness
- **Git:** For cloning repository
- **PowerShell:** 5.1 or higher (included in Windows)

---

## Installation Guide

### 1. Prepare the VPS

Connect to your VPS via RDP:
```bash
mstsc /v:YOUR_VPS_IP
```

### 2. Install Git (if not installed)

Download and install Git from: https://git-scm.com/download/win

Or use Chocolatey:
```powershell
choco install git -y
```

### 3. Clone Repository

```powershell
cd C:\
git clone https://github.com/A6-9V/my-drive-projects.git
cd my-drive-projects\trading-bridge
```

### 4. Run Deployment Script

The deployment script automates the entire setup:

```powershell
.\DEPLOY_NOW.ps1
```

This script will:
1. Check and install Python if needed
2. Install Python dependencies from requirements.txt
3. Create configuration directories
4. Generate broker configuration template
5. Configure Windows Firewall for port 5500
6. Check for MetaTrader 5 installation
7. Create logs directory

---

## Configuration

### Broker Configuration

Edit `config/brokers.json`:

```json
{
  "EXNESS": {
    "account_id": "12345678",
    "api_key": "your_api_key_here",
    "api_secret": "your_api_secret_here",
    "api_url": "https://api.exness.com",
    "enabled": true,
    "description": "Get credentials from: https://my.exness.com → Settings → API"
  }
}
```

**How to get Exness API credentials:**

1. Log in to https://my.exness.com
2. Go to **Settings** → **API**
3. Click **Create API Key**
4. Set permissions: **Trade**, **Read Account Info**
5. Copy the API Key and API Secret
6. Add your trading account ID

### Expert Advisor Configuration

When attaching the EA to a chart, configure:

- **BridgePort:** 5500 (must match Python bridge port)
- **BrokerName:** EXNESS (must match config file)
- **AutoExecute:** true (enable automatic trade execution)
- **DefaultLotSize:** 0.01 (start with small size)
- **Slippage:** 10 (maximum slippage in points)
- **EnableLogging:** true (enable detailed logging)

---

## Running the System

### Start the Python Bridge

```powershell
.\start-bridge.ps1
```

The bridge will:
1. Load broker configuration from `config/brokers.json`
2. Initialize broker API connections
3. Start TCP server on port 5500
4. Wait for MT5 connections
5. Log all activities to `logs/bridge_YYYYMMDD.log`

### Attach EA to MT5

1. Open MetaTrader 5
2. Open a chart (File → New Chart → select symbol)
3. In Navigator panel: Expert Advisors → PythonBridgeEA
4. Drag and drop onto chart
5. Configure settings (see above)
6. Enable AutoTrading (button in toolbar)

### Verify Connection

Check MT5 Experts tab for:
```
Bridge connection initialized on port 5500
✓ Successfully connected to Python bridge
```

Check Python bridge logs:
```powershell
Get-Content logs\bridge_*.log -Tail 20
```

Should show:
```
Client connected from ('127.0.0.1', XXXXX)
Received: {"action":"ping","broker":"EXNESS"}
```

---

## Auto-Start Configuration

### Create Windows Scheduled Task

To start the bridge automatically on VPS boot:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File C:\my-drive-projects\trading-bridge\start-bridge.ps1"
$trigger = New-ScheduledTaskTrigger -AtStartup
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName "TradingBridge" -Action $action -Trigger $trigger -Principal $principal -Settings $settings
```

Or use the simple command:
```powershell
schtasks /create /tn "TradingBridge" /tr "powershell -File C:\my-drive-projects\trading-bridge\start-bridge.ps1" /sc onstart /ru SYSTEM /f
```

### Auto-Start MetaTrader 5

Add MT5 to Windows startup:

1. Press `Win + R`
2. Type `shell:startup` and press Enter
3. Create a shortcut to `terminal64.exe`
4. Location: `C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe`

Or use PowerShell:
```powershell
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\MetaTrader5.lnk")
$Shortcut.TargetPath = "C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe"
$Shortcut.Save()
```

---

## Monitoring and Maintenance

### Check System Status

```powershell
# Check if bridge is running
Get-Process python -ErrorAction SilentlyContinue

# Check if MT5 is running
Get-Process terminal64 -ErrorAction SilentlyContinue

# Check port 5500 is listening
netstat -ano | findstr ":5500"

# View latest logs
Get-Content logs\*.log -Tail 50
```

### Log Files

Logs are stored in `logs/` directory:
- `bridge_YYYYMMDD.log` - Daily log files
- Contains all bridge activities, connections, trades

### Performance Monitoring

Monitor VPS resources:
```powershell
# CPU usage
Get-Counter '\Processor(_Total)\% Processor Time'

# Memory usage
Get-Counter '\Memory\Available MBytes'

# Network usage
Get-Counter '\Network Interface(*)\Bytes Total/sec'
```

---

## Security Best Practices

### 1. Secure API Credentials

- Never commit `config/brokers.json` to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Use API keys with minimal required permissions

### 2. Firewall Configuration

```powershell
# Allow only local connections to port 5500
New-NetFirewallRule -DisplayName "Trading Bridge (Local Only)" `
    -Direction Inbound `
    -LocalPort 5500 `
    -Protocol TCP `
    -Action Allow `
    -RemoteAddress 127.0.0.1
```

### 3. Windows Updates

Keep your VPS updated:
```powershell
# Check for updates
Get-WindowsUpdate

# Install updates
Install-WindowsUpdate -AcceptAll -AutoReboot
```

### 4. Backup Configuration

```powershell
# Backup configuration
$backupDir = "C:\Backups\trading-bridge-$(Get-Date -Format 'yyyyMMdd')"
New-Item -ItemType Directory -Path $backupDir
Copy-Item -Path "config\*" -Destination $backupDir -Recurse
Copy-Item -Path "logs\*" -Destination $backupDir -Recurse
```

---

## Troubleshooting

### Bridge Won't Start

**Error: "Address already in use"**
```powershell
# Find process using port 5500
netstat -ano | findstr ":5500"

# Kill the process (replace PID with actual process ID)
Stop-Process -Id PID -Force
```

**Error: "No module named 'aiohttp'"**
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### EA Can't Connect

1. **Check bridge is running:**
   ```powershell
   Get-Process python -ErrorAction SilentlyContinue
   ```

2. **Check port is open:**
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 5500
   ```

3. **Check firewall:**
   ```powershell
   Get-NetFirewallRule -DisplayName "*Trading Bridge*"
   ```

4. **Check EA settings:**
   - BridgePort must be 5500
   - AutoTrading must be enabled in MT5

### Trades Not Executing

1. **Check API credentials** in `config/brokers.json`
2. **Verify broker is enabled:** `"enabled": true`
3. **Check API permissions** on Exness portal
4. **Review logs** for error messages:
   ```powershell
   Select-String -Path logs\*.log -Pattern "error" | Select-Object -Last 10
   ```

### High Latency

1. **Check VPS location** - should be Singapore
2. **Check network latency** to broker:
   ```powershell
   Test-Connection -ComputerName api.exness.com -Count 10
   ```
3. **Monitor VPS resources** - CPU/RAM usage
4. **Close unnecessary applications**

---

## Advanced Configuration

### Multiple Brokers

Add more brokers to `config/brokers.json`:

```json
{
  "EXNESS": {
    "account_id": "12345678",
    "api_key": "key1",
    "api_secret": "secret1",
    "enabled": true
  },
  "BROKER2": {
    "account_id": "87654321",
    "api_key": "key2",
    "api_secret": "secret2",
    "enabled": true
  }
}
```

### Custom Port

To use a different port:

1. Edit `bridge_server.py`:
   ```python
   bridge = TradingBridge(host="0.0.0.0", port=5501)
   ```

2. Update firewall rule
3. Update EA parameter: `BridgePort = 5501`

---

## Support

For issues or questions:

1. Check logs: `logs/bridge_*.log`
2. Review this guide: `DEPLOYMENT_GUIDE.md`
3. See quick start: `VPS_QUICK_START.md`
4. Check command reference: `VPS_DEPLOY_COMMANDS.txt`

---

**Device:** NUNA 💻 | **User:** @mouyleng | **Org:** @A6-9V
**VPS:** Singapore 09 | **Trading:** 24/7
