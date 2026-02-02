# Singapore VPS - Quick Start Guide

## 🚀 Quick Deployment (5 Minutes)

### Prerequisites
- Windows VPS in Singapore
- RDP access to VPS
- MetaTrader 5 account (Exness recommended)
- Exness API credentials

---

## Step 1: Connect to VPS

On your local machine, open Remote Desktop:

```bash
mstsc /v:YOUR_VPS_IP_ADDRESS
```

Alternative options:
- Chrome Remote Desktop
- TeamViewer
- AnyDesk

---

## Step 2: Open PowerShell as Administrator

1. Right-click the Start menu
2. Select "Windows PowerShell (Administrator)"
3. Click "Yes" on the UAC prompt

---

## Step 3: Clone and Deploy

Copy and paste these commands into PowerShell:

```powershell
cd C:\
git clone https://github.com/A6-9V/my-drive-projects.git
cd my-drive-projects\trading-bridge
.\DEPLOY_NOW.ps1
```

The deployment script will automatically:
- ✓ Check Python installation (installs if needed)
- ✓ Install all Python dependencies
- ✓ Create configuration files
- ✓ Set up MT5 bridge
- ✓ Configure Windows firewall (port 5500)
- ✓ Check MetaTrader 5 installation

---

## Step 4: Configure API Credentials

Edit the broker configuration:

```powershell
notepad config\brokers.json
```

Add your Exness credentials:
```json
{
  "EXNESS": {
    "account_id": "YOUR_ACCOUNT_ID",
    "api_key": "YOUR_API_KEY",
    "api_secret": "YOUR_API_SECRET",
    "api_url": "https://api.exness.com",
    "enabled": true
  }
}
```

Get credentials from: https://my.exness.com → Settings → API

**Important:** Set `"enabled": true` to activate the broker!

---

## Step 5: Install MetaTrader 5 (if not installed)

1. Download from: https://www.exness.com/mt5/
2. Install to: `C:\Program Files\MetaTrader 5 EXNESS`
3. Login with your trading account

---

## Step 6: Compile the Expert Advisor

Run the MetaEditor script:

```powershell
.\open-metaeditor.ps1
```

In MetaEditor:
1. PythonBridgeEA.mq5 should open automatically
2. Press `F7` to compile
3. Wait for "0 errors, 0 warnings"
4. Close MetaEditor

---

## Step 7: Attach EA to Chart in MT5

1. Open MetaTrader 5
2. Open any chart (e.g., XAUUSD, EURUSD)
3. In Navigator panel → Expert Advisors → **PythonBridgeEA**
4. Drag the EA onto the chart
5. Configure settings:
   - **BridgePort:** 5500
   - **BrokerName:** EXNESS
   - **AutoExecute:** true
   - **DefaultLotSize:** 0.01 (start small!)
6. Click **OK**

Check the **Experts** tab for:
```
Bridge connection initialized on port 5500
```

---

## Step 8: Start the Trading Bridge

Launch the bridge server:

```powershell
.\start-bridge.ps1
```

**Keep this PowerShell window open!** The bridge must run continuously.

You should see:
```
Trading Bridge Server started on 0.0.0.0:5500
Waiting for connections from MT5 Expert Advisor...
```

---

## Step 9: Setup Auto-Start (Important!)

To ensure the bridge starts automatically when VPS reboots:

```powershell
schtasks /create /tn "TradingBridge" /tr "powershell -File C:\my-drive-projects\trading-bridge\start-bridge.ps1" /sc onstart /ru SYSTEM /f
```

This creates a Windows scheduled task that launches the bridge on system startup.

---

## Verify Everything Works

### 1. Check Bridge is Running

```powershell
netstat -an | findstr ":5500"
```

Should show:
```
TCP    0.0.0.0:5500    0.0.0.0:0    LISTENING
```

### 2. Check MT5 is Running

```powershell
Get-Process | Where-Object { $_.ProcessName -like "*terminal*" }
```

### 3. Check MT5 Experts Tab

Should show:
```
Bridge connection initialized on port 5500
✓ Successfully connected to Python bridge
```

### 4. Check Logs

```powershell
Get-Content logs\*.log -Tail 50
```

---

## Troubleshooting

### Cannot Connect to VPS?
- Check VPS is running in your provider's dashboard
- Verify RDP is enabled on the VPS
- Check your firewall rules allow RDP (port 3389)

### Bridge Won't Start?
```powershell
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check if port 5500 is already in use
netstat -ano | findstr ":5500"
```

### EA Won't Connect?
1. Verify MT5 is running
2. Check EA is attached to chart (look for smiley face icon)
3. Verify Python bridge is running (`start-bridge.ps1`)
4. Check Windows Firewall allows port 5500
5. Check EA settings match bridge port

### Trades Not Executing?
1. Verify API credentials in `config\brokers.json`
2. Check Exness API has "Trade" permission enabled
3. Verify account has sufficient balance
4. Check if market is open (Forex: Mon-Fri, 24h)
5. Review logs for error messages

### Check Log Files
```powershell
# View today's bridge log
Get-Content logs\bridge_*.log -Tail 100

# View all logs
Get-ChildItem logs\*.log | ForEach-Object { 
    Write-Host "`n=== $($_.Name) ===" -ForegroundColor Cyan
    Get-Content $_.FullName -Tail 20 
}
```

---

## Important Reminders

⚠️ **Start with DEMO account first!**
⚠️ **Use small position sizes (0.01 lots)**
⚠️ **Monitor first trades closely**
⚠️ **Keep VPS updated with Windows Updates**
⚠️ **Backup your configuration regularly**

---

## Singapore VPS - Trading Advantages

- **Location:** Singapore (optimal for Exness Singapore servers)
- **Latency:** <10ms to broker
- **Uptime:** 24/7 automated trading
- **Timezone:** SGT (UTC+8) - Asian market hours
- **Network:** High-speed connectivity to major financial hubs

---

## Next Steps

After successful deployment:

1. **Test the System:**
   - Start with small trades (0.01 lots)
   - Monitor for 24 hours
   - Check logs regularly

2. **Scale Up:**
   - Gradually increase position sizes
   - Add more currency pairs
   - Implement risk management

3. **Monitor Performance:**
   - Review daily logs
   - Track trade execution
   - Monitor API usage limits

4. **Maintain the System:**
   - Keep Windows updated
   - Update Python packages monthly
   - Backup configuration files
   - Monitor VPS resources (CPU, RAM, Disk)

---

## Support & Documentation

See these files for more information:
- **DEPLOYMENT_GUIDE.md** - Detailed deployment instructions
- **VPS_DEPLOY_COMMANDS.txt** - Command reference
- **README.md** - Project overview

---

**Status:** Ready for 24/7 Trading! 🚀

**Device:** NUNA 💻 | **User:** @mouyleng | **Org:** @A6-9V
**VPS:** Singapore 09 | **Trading:** 24/7
