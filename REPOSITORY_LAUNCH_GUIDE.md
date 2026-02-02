# GenX_FX Repository Launch Guide

## Organization: A6-9V
**Complete Guide for Launching and Using the GenX_FX Trading Repository on Cloned Branch**

---

## 📋 Overview

This guide provides detailed instructions for launching the GenX_FX trading system repository on a cloned branch with MetaTrader 5 integration. The system is configured for the Exness-MT5Trial8 demo account with automated Expert Advisors.

---

## 🎯 Current Configuration

### MT5 Trading Platform Setup
**Account Information:**
- **Account Name:** Exness-MT5Trial8
- **Account Type:** Demo Account (Hedging)
- **Description:** "Im Good only for testing"
- **Balance/Equity/Free Margin:** 39,499.31 USD
- **Server:** Exness-MT5Trail8

### Configured Accounts
The system supports two accounts:
1. **Exness-MT5Real8** - Production trading account
2. **Exness-MT5Trial8** - Demo/testing account (currently active)

---

## 🗂️ Repository Structure

```
GenX_FX/
├── A6-9V_Enhanced_Master_Launcher.bat    # Main system launcher
├── A6-9V_Master_Launcher.bat             # Original launcher (backup)
├── MT_AutoLogin_Fixed.ps1                # MT4/5 automated login
├── Enable_MT_AutoTrading.ps1             # Enable Expert Advisors
├── A6-9V/
│   └── Trading/
│       └── GenX_FX/                      # Main trading application
├── scripts/                               # Utility scripts
├── ProductionApp/                         # Production environment
└── docs/                                  # Documentation
```

---

## 🚀 Launching the Repository on Cloned Branch

### Step 1: Clone and Checkout Branch

```bash
# Clone the repository
git clone https://github.com/Mouy-leng/GenX_FX-c62abe22.git
cd GenX_FX

# Checkout the specific branch
git checkout copilot/launch-repository-clone

# Verify you're on the correct branch
git branch --show-current
```

### Step 2: Verify Repository Structure

```bash
# List main files
ls -la

# Check for essential launcher scripts
ls -l *.bat *.ps1

# Verify A6-9V Trading directory
ls -la A6-9V/Trading/
```

### Step 3: Launch MetaTrader 5 Platform

#### Windows Environment:
```batch
# Run the enhanced master launcher
A6-9V_Enhanced_Master_Launcher.bat
```

This launcher will:
1. ✅ Start MT4 EXNESS terminal (if available)
2. ✅ Start MT5 EXNESS terminal
3. ⏰ Wait 15 seconds for platform initialization
4. 🔐 Execute automated login script
5. 🤖 Enable Expert Advisors and auto-trading

#### Manual PowerShell Launch:
```powershell
# Launch MT5 only with automated login
powershell -ExecutionPolicy Bypass -File "MT_AutoLogin_Fixed.ps1" -Platform mt5

# Launch both MT4 and MT5
powershell -ExecutionPolicy Bypass -File "MT_AutoLogin_Fixed.ps1" -Platform both
```

---

## 📊 Market Watch Configuration

The following currency pairs and assets should be visible in your Market Watch panel:

### Primary Trading Pairs:
- **XAUUSD** - Gold vs US Dollar
- **BTCUSD** - Bitcoin vs US Dollar
- **EURUSD** - Euro vs US Dollar
- **USDJPY** - US Dollar vs Japanese Yen
- **ETHUSD** - Ethereum vs US Dollar

### Additional Crypto Pairs:
- **BTCCNH** - Bitcoin vs Chinese Yuan
- **BTCXAU** - Bitcoin vs Gold
- **BTCZAR** - Bitcoin vs South African Rand

### Forex Pairs:
- **GBPJPY** - British Pound vs Japanese Yen
- **GBPUSD** - British Pound vs US Dollar
- **USDARS** - US Dollar vs Argentine Peso
- **USDCAD** - US Dollar vs Canadian Dollar
- **USDCHF** - US Dollar vs Swiss Franc

---

## 🤖 Expert Advisors Configuration

### Installed Expert Advisors (EAs)

The system includes the following Expert Advisors as shown in the Navigator panel:

#### Primary EAs:
1. **ExpertMAPSAR_Enhanced** - Enhanced Parabolic SAR trading system
2. **ExpertMAPSAR Enhanced** - Alternative enhanced version
3. **ExpertMAPSARSizeOptimized** - Position size optimized version
4. **ExpertMAPSAR** - Standard Parabolic SAR EA

#### Additional EAs:
5. **ExpertMACD** - MACD indicator-based trading system
6. **ExpertMAMA** - MESA Adaptive Moving Average system
7. **bridges3rd** - Bridge/connector EA
8. **Advisors_backup_20251226_235613** - Backup configuration

### Enabling Expert Advisors

#### Method 1: Automated Script
```powershell
# Run the EA enabler script
powershell -ExecutionPolicy Bypass -File "Enable_MT_AutoTrading.ps1"
```

#### Method 2: Manual Activation
1. Open MetaTrader 5 platform
2. Press **Ctrl+E** to enable Expert Advisors
3. Click the **AutoTrading** button in the toolbar (should turn green)
4. Verify "Expert Advisors" tab shows active status

#### Method 3: Platform Settings
1. Go to **Tools → Options** (Ctrl+O)
2. Navigate to **Expert Advisors** tab
3. Check the following options:
   - ✅ Allow automated trading
   - ✅ Allow DLL imports
   - ✅ Allow WebRequest for listed URL

---

## 🔐 Account Login Configuration

### MT5 EXNESS Account:
```
Login:    279260115
Password: Leng12345@#$01
Server:   Exness-MT5Trail8
```

### MT4 EXNESS Account (if needed):
```
Login:    70559995
Password: Leng12345@#$01
Server:   Exness-Trail9
```

**Security Note:** These credentials are for demo accounts. Never commit real trading credentials to version control.

---

## 🔄 System Launch Workflow

### Phase 1: MetaTrader Platform Setup (15-20 seconds)
```
1. Launch MT5 EXNESS terminal
2. Wait for platform initialization
3. Execute automated login script
4. Enable Expert Advisors and auto-trading
```

### Phase 2: Core System Components (5-10 seconds)
```
1. Start Python Management System
2. Launch GenX-FX Trading System
3. Activate virtual environments
```

### Phase 3: Development Environment (5-10 seconds)
```
1. Open Cursor IDE
2. Launch trading dashboards (TradingView, Yahoo Finance)
3. Open Code With Me collaboration session
```

### Phase 4: Verification & Monitoring (ongoing)
```
1. Verify MT5 process is running
2. Check connection status
3. Confirm Expert Advisors are active
4. Start system monitoring (Task Manager)
```

---

## ✅ Verification Checklist

### Post-Launch Verification:

- [ ] **MT5 Platform Running**
  ```bash
  # Windows: Check if MT5 is running
  tasklist /FI "IMAGENAME eq terminal64.exe"
  
  # Linux/Mac: Check process
  ps aux | grep -i metatrader
  ```

- [ ] **Account Login Successful**
  - Verify connection status shows "Exness-MT5Trial8"
  - Check account balance displays: 39,499.31 USD
  - Confirm equity and free margin match balance

- [ ] **Expert Advisors Enabled**
  - AutoTrading button is green/active
  - Expert Advisors tab shows "AutoTrading enabled"
  - EAs are loaded on charts (if configured)

- [ ] **Market Watch Active**
  - All configured symbols are visible
  - Bid/Ask prices are updating
  - Daily change percentages shown

- [ ] **Navigator Panel**
  - Both accounts visible (Exness-MT5Real8, Exness-MT5Trial8)
  - Trial8 account is highlighted/active
  - All Expert Advisors are listed

---

## 🛠️ Troubleshooting

### Issue: MT5 Not Starting

**Solution:**
```bash
# Verify MT5 installation path
# Windows default: C:\Program Files\MetaTrader 5 EXNESS\terminal64.exe

# Check if process exists
tasklist | findstr terminal64

# If not found, verify installation or check alternative path
```

### Issue: Login Fails

**Solution:**
1. Manually login using credentials provided above
2. Verify server name is exactly: `Exness-MT5Trail8`
3. Check internet connection
4. Ensure demo account is still active

### Issue: Expert Advisors Not Enabling

**Solution:**
```powershell
# Re-run the enabler script with administrator privileges
powershell -ExecutionPolicy Bypass -File "Enable_MT_AutoTrading.ps1"

# Or manually:
# 1. Open MT5
# 2. Press Ctrl+E
# 3. Click AutoTrading button in toolbar
# 4. Verify green indicator appears
```

### Issue: Market Watch Symbols Missing

**Solution:**
1. Right-click in Market Watch window
2. Select "Show All" or "Symbols"
3. Search for missing symbols (XAUUSD, BTCUSD, etc.)
4. Right-click symbol → "Show"

### Issue: GenX-FX Python System Not Starting

**Solution:**
```bash
# Navigate to trading system directory
cd A6-9V/Trading/GenX_FX

# Check if virtual environment exists
ls -la venv/

# Activate virtual environment
# Windows:
venv\Scripts\activate.bat

# Linux/Mac:
source venv/bin/activate

# Install requirements if needed
pip install -r requirements.txt

# Run the application
python main.py
```

---

## 🖥️ Desktop Layout Reference

Based on the Exness MT5 trading platform screen, your layout should include:

### Left Panel - Navigator:
- Accounts section with Exness-MT5Real8 and Exness-MT5Trial8
- Indicators library
- Expert Advisors list (all 8 EAs)

### Left Panel - Market Watch:
- Symbol list with bid/ask prices
- Daily change percentages
- Quick access to all trading pairs

### Bottom Panel - Trade Information:
- Balance: 39,499.31 USD
- Equity: 39,499.31 USD
- Free Margin: 39,499.31 USD

### Main Chart Area:
- Active trading charts
- Expert Advisors attached to charts
- Technical indicators overlay

---

## 📈 System Status Indicators

| Component | Expected Status | Verification Command |
|-----------|----------------|----------------------|
| 🟢 MT5 Running | terminal64.exe active | `tasklist /FI "IMAGENAME eq terminal64.exe"` |
| 🟢 Account Connected | Server: Exness-MT5Trial8 | Check MT5 status bar |
| 🟢 Auto-Trading | Expert Advisors enabled | Green AutoTrading button |
| 🟢 Balance Display | 39,499.31 USD shown | Check bottom panel |
| 🟢 Market Watch | All symbols updating | Verify bid/ask prices change |

---

## 🔒 Security Considerations

1. **Demo Account:** Currently using Exness-MT5Trial8 for testing
2. **Credentials:** Login details are stored in launcher scripts
3. **Desktop Lock:** System automatically locks desktop after launch
4. **Auto-Trading:** Requires manual verification for safety

**Important:** Before switching to live trading (Exness-MT5Real8):
- Test all Expert Advisors thoroughly on demo account
- Verify risk management settings
- Ensure sufficient account balance
- Review EA performance logs

---

## 📞 Support and Documentation

### Additional Resources:
- **Master System README:** `A6-9V_Master_System_README.md`
- **Local README:** `README-local.md`
- **Credential Setup:** `AUTONOMOUS_CREDENTIAL_SETUP.md`
- **Security Report:** `CREDENTIAL_SECURITY_REPORT.md`

### Code With Me Session:
- **URL:** https://code-with-me.global.jetbrains.com/ZhaX8frcoZS0qveUMv8vAg
- **Platform:** JetBrains IntelliJ IDEA

### Quick Links:
- Documentation index: `docs/README.md`
- Project management: `docs/PLANE_PROJECT_MANAGEMENT.md`
- GitHub App setup: `docs/GITHUB_APP_SETUP.md`

---

## 🚨 Trading Reminders

### Pre-Trading Checklist:
- [ ] Account login verified
- [ ] Internet connection stable
- [ ] Expert Advisors enabled
- [ ] Auto-trading button active
- [ ] Sufficient account balance confirmed
- [ ] Trading hours verified
- [ ] Economic calendar checked
- [ ] Risk management settings configured

### Risk Management:
- Monitor account balance and margin levels continuously
- Set appropriate stop-loss levels for all trades
- Never risk more than you can afford to lose
- Keep detailed trading journal
- Test strategies on demo before live trading

---

## 📊 System Version Information

**System Version:** Enhanced v2.0  
**Last Updated:** 2026-01-04  
**Organization:** A6-9V  
**Branch:** copilot/launch-repository-clone  
**Repository:** Mouy-leng/GenX_FX-c62abe22

---

**🎯 Status: OPERATIONAL | GenX_FX Repository Ready for Launch on Cloned Branch**

---

## Quick Start Summary

```bash
# 1. Clone and checkout branch
git clone https://github.com/Mouy-leng/GenX_FX-c62abe22.git
cd GenX_FX
git checkout copilot/launch-repository-clone

# 2. Launch the system (Windows)
A6-9V_Enhanced_Master_Launcher.bat

# 3. Verify MT5 connection
# - Check: Exness-MT5Trial8 shown in title bar
# - Verify: Balance shows 39,499.31 USD
# - Confirm: AutoTrading button is green

# 4. Start trading with Expert Advisors!
```

---

*This guide is part of the A6-9V GenX_FX Trading System documentation.*
