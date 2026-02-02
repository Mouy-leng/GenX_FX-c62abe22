# Logs Directory

This directory stores daily log files from the trading bridge server.

## Log Files

- **Format:** `bridge_YYYYMMDD.log`
- **Rotation:** Daily (one file per day)
- **Retention:** Keep logs for at least 30 days

## What's Logged

- Connection events (MT5 EA connections/disconnections)
- Trading signals received from MT5
- API calls to broker
- Trade execution results
- Errors and warnings
- System status messages

## Viewing Logs

### View latest logs
```powershell
Get-Content logs\*.log -Tail 50
```

### View logs in real-time
```powershell
Get-Content logs\bridge_*.log -Wait
```

### Search for errors
```powershell
Select-String -Path logs\*.log -Pattern "error" -CaseSensitive:$false
```

### View specific date
```powershell
Get-Content logs\bridge_20260202.log
```

## Log Maintenance

### Archive old logs
```powershell
$archivePath = "C:\logs-archive\$(Get-Date -Format 'yyyyMM')"
New-Item -ItemType Directory -Path $archivePath -Force
Move-Item -Path "logs\*.log" -Destination $archivePath -Exclude "bridge_$(Get-Date -Format 'yyyyMMdd').log"
```

### Delete old logs (>30 days)
```powershell
Get-ChildItem logs\*.log | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | Remove-Item
```
