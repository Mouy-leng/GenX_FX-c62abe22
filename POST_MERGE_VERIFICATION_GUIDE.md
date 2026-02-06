# Post-Merge Verification Guide

## Purpose
This guide provides step-by-step instructions to verify the deployment after merging the performance improvements PR.

---

## 1. Merge the PR

### Via GitHub Web Interface
1. Navigate to: https://github.com/Mouy-leng/GenX_FX-c62abe22/pull/[PR_NUMBER]
2. Click **"Merge pull request"**
3. Confirm merge

### Via Command Line (Local)
```bash
# Switch to main branch
git checkout main

# Pull latest changes
git pull origin main

# Merge the performance branch
git merge copilot/improve-slow-code-performance

# Push to GitHub
git push origin main
```

---

## 2. Deploy to VPS

### Connect to VPS
```bash
# SSH into your VPS (replace with your actual VPS IP/hostname)
ssh your-username@your-vps-ip
```

### Option A: Automated Deployment (Recommended)
```bash
# Navigate to project directory
cd /var/www/genx-fx

# Pull latest changes from main
git pull origin main

# Run deployment script
sudo ./deploy.sh
```

### Option B: Manual Deployment
```bash
# Navigate to ProductionApp
cd /var/www/genx-fx/ProductionApp

# Pull latest changes
git pull origin main

# Stop existing containers
docker-compose down

# Rebuild and start
docker-compose up -d --build

# Wait for services to start
sleep 10
```

---

## 3. Verify Docker Containers

### Check Running Containers
```bash
cd /var/www/genx-fx/ProductionApp
docker-compose ps
```

**Expected Output:**
```
NAME                COMMAND                  SERVICE   STATUS    PORTS
productionapp-app   "docker-entrypoint.s…"   app       Up        0.0.0.0:3000->3000/tcp
productionapp-mongo "docker-entrypoint.s…"   mongo     Up        0.0.0.0:27017->27017/tcp
productionapp-nginx "/docker-entrypoint.…"   nginx     Up        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
productionapp-redis "docker-entrypoint.s…"   redis     Up        0.0.0.0:6379->6379/tcp
```

### Check Container Health
```bash
# View detailed status
docker-compose ps -a

# Check logs for any errors
docker-compose logs --tail=50

# Follow logs in real-time
docker-compose logs -f app
```

---

## 4. Verify API Port Listening

### Test Health Endpoint
```bash
# From VPS
curl http://localhost:3000/health

# Expected response:
# {"status":"ok","timestamp":"2026-02-06T19:41:36.452Z","uptime":123.45}

# Test from external
curl http://lengkundee01.org/health
# or
curl http://YOUR_VPS_IP:3000/health
```

### Check Port Listening
```bash
# Check if port 3000 is listening
netstat -tlnp | grep 3000
# or
ss -tlnp | grep 3000

# Expected output:
# tcp  0  0  0.0.0.0:3000  0.0.0.0:*  LISTEN  [docker-proxy PID]
```

### Test API Endpoints
```bash
# Test authentication endpoint
curl -X POST http://localhost:3000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"TestPass123!"}'

# Should return 201 Created or 400 if user exists
```

---

## 5. Verify Expert Advisor (EA) Deployment

### Check EA Files on VPS
```bash
# Navigate to EA directory
cd /var/www/genx-fx/A6-9V/Trading/GenX_FX

# List EA files
ls -la *.mq5 *.ex5 2>/dev/null

# Expected files:
# - ExpertMAPSAR_Enhanced.mq5
# - ExpertMACD.mq5
# - ExpertMAMA.mq5
# - etc.
```

### MetaTrader 5 Location
The EA files need to be in MetaTrader's Expert Advisors directory:
```
C:\Program Files\MetaTrader 5\MQL5\Experts\
# or
C:\Users\[USERNAME]\AppData\Roaming\MetaQuotes\Terminal\[INSTANCE_ID]\MQL5\Experts\
```

**Manual Sync Required:**
1. Copy .mq5 files from repository to MT5 Experts folder
2. Open MetaEditor in MT5
3. Compile each .mq5 file to generate .ex5
4. Refresh Navigator in MT5 to see Expert Advisors

---

## 6. Verify Real-time Synchronization

### A. GitHub Sync
```bash
# On VPS, check Git status
cd /var/www/genx-fx
git status
git log -3 --oneline

# Verify latest commits are present
git log --grep="performance" --oneline
```

### B. Forge MQL5 Sync
The repository includes a Git submodule reference to forge.mql5.io:

```bash
# Check submodules
git submodule status

# Update submodules
git submodule update --init --recursive

# Push to forge.mql5.io (if configured)
git push forge-mql5 main
```

**Note:** You may need to configure the forge.mql5.io remote:
```bash
# Check remotes
git remote -v

# Add forge.mql5.io remote if not present
git remote add forge-mql5 https://forge.mql5.io/A6-9V/mql5.git
```

### C. Monitor Application Logs
```bash
# Real-time application logs
cd /var/www/genx-fx/ProductionApp
docker-compose logs -f --tail=100

# Watch for:
# - API requests being processed
# - Database connections
# - No error messages
# - Performance improvements in action
```

---

## 7. Performance Verification

### Check Performance Improvements

#### Monitor Thread Responsiveness
```bash
# From VPS, check Python processes
ps aux | grep python

# Monitor with top (should see lower CPU usage)
top -p $(pgrep -f python_startup_manager.py)
```

#### Test Shutdown Responsiveness
```bash
# Time the shutdown (should be instant, not 10+ seconds)
time docker-compose restart app

# Should complete in ~5-10 seconds (vs 20+ seconds before)
```

#### Memory Usage
```bash
# Check memory usage (should be stable, not growing)
docker stats --no-stream

# Run for a few minutes and check again
sleep 300
docker stats --no-stream
```

---

## 8. Troubleshooting

### If Docker Containers Don't Start
```bash
# Check logs
docker-compose logs

# Remove volumes and restart
docker-compose down -v
docker-compose up -d --build
```

### If API Not Responding
```bash
# Check firewall
sudo ufw status
sudo ufw allow 3000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check nginx configuration
sudo nginx -t
sudo systemctl restart nginx
```

### If EA Files Not Visible in MT5
1. Ensure .mq5 files are in correct directory
2. Compile in MetaEditor (F7 or Ctrl+F7)
3. Check compilation errors
4. Restart MetaTrader 5
5. Refresh Navigator (F5)

### If forge.mql5.io Sync Fails
```bash
# Check authentication
git remote get-url forge-mql5

# Test connection
git ls-remote forge-mql5

# Push manually
git push forge-mql5 main --force
```

---

## 9. Final Verification Checklist

- [ ] PR merged successfully
- [ ] VPS deployment completed without errors
- [ ] Docker containers all running (4 containers: app, mongo, redis, nginx)
- [ ] API health endpoint responds with 200 OK
- [ ] Port 3000 listening and accessible
- [ ] Application logs show no errors
- [ ] EA files present in repository
- [ ] EA files synced to MT5 (if applicable)
- [ ] GitHub repository updated with latest commits
- [ ] forge.mql5.io synced (if configured)
- [ ] Performance improvements observable:
  - [ ] Faster shutdown times
  - [ ] Lower CPU usage in monitoring dashboard
  - [ ] Stable memory usage
  - [ ] No memory leaks

---

## 10. Monitoring Commands Reference

```bash
# Quick health check
curl -s http://localhost:3000/health | jq

# View all container logs
docker-compose logs --tail=100 -f

# Check resource usage
docker stats

# Monitor specific container
docker logs -f productionapp-app

# Check database connectivity
docker-compose exec mongo mongosh --eval "db.adminCommand('ping')"

# Test Redis
docker-compose exec redis redis-cli ping

# Check nginx status
docker-compose exec nginx nginx -t
```

---

## Support

For issues during deployment:
- Check logs: `docker-compose logs`
- Review MONITORING_GUIDE.md for detailed monitoring instructions
- See PERFORMANCE_IMPROVEMENTS.md for expected performance gains
- Check README.md for general setup instructions

---

**Last Updated:** 2026-02-06
**Related PR:** Performance: Fix blocking I/O, memory leak, and O(n²) algorithms
**Branch:** copilot/improve-slow-code-performance
