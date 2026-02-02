# Monitoring and Health Check Configuration

## 📊 Overview

This document describes the monitoring and health check setup for the GenX_FX application deployed on a custom domain.

## 🏥 Health Check Endpoints

### Basic Health Check
**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-06T14:33:27.640Z",
  "uptime": 3600
}
```

**Status Codes:**
- `200 OK` - Service is healthy
- `503 Service Unavailable` - Service is unhealthy

### Detailed Health Check
**Endpoint:** `GET /health/detailed`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-06T14:33:27.640Z",
  "uptime": 3600,
  "environment": "production",
  "version": "1.0.0",
  "services": {
    "database": {
      "status": "connected",
      "latency": 5
    },
    "redis": {
      "status": "connected",
      "latency": 2
    }
  },
  "system": {
    "memory": {
      "total": 4096,
      "free": 2048,
      "usage": "50%"
    },
    "cpu": {
      "cores": 4,
      "load": [1.5, 1.3, 1.2]
    }
  }
}
```

## 🔍 Monitoring Tools

### 1. Built-in Monitoring Script

Create `/var/www/genx-fx/monitor.sh`:

```bash
#!/bin/bash

DOMAIN="lengkundee01.org"
EMAIL="your-email@example.com"
LOG_FILE="/var/log/genx-fx-monitor.log"

# Check if site is up
check_health() {
    local url="https://$DOMAIN/health"
    local response=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ "$response" != "200" ]; then
        echo "$(date): Site DOWN - HTTP $response" >> "$LOG_FILE"
        echo "❌ Site is DOWN! HTTP Status: $response" | mail -s "Alert: $DOMAIN Down" "$EMAIL"
        
        # Attempt restart
        cd /var/www/genx-fx/ProductionApp
        docker-compose restart app
        
        return 1
    else
        echo "$(date): Site UP" >> "$LOG_FILE"
        return 0
    fi
}

# Check database connection
check_database() {
    local db_status=$(docker-compose -f /var/www/genx-fx/ProductionApp/docker-compose.yml exec -T mongo mongosh --quiet --eval "db.adminCommand('ping')")
    
    if [[ $db_status == *"ok"* ]]; then
        echo "$(date): Database OK" >> "$LOG_FILE"
        return 0
    else
        echo "$(date): Database ISSUE" >> "$LOG_FILE"
        echo "❌ Database connection issue" | mail -s "Alert: $DOMAIN Database" "$EMAIL"
        return 1
    fi
}

# Check disk space
check_disk() {
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
    
    if [ "$disk_usage" -gt 90 ]; then
        echo "$(date): Disk usage high: $disk_usage%" >> "$LOG_FILE"
        echo "⚠️  Disk usage is at $disk_usage%" | mail -s "Warning: $DOMAIN Disk Space" "$EMAIL"
        return 1
    fi
    
    return 0
}

# Check memory usage
check_memory() {
    local mem_usage=$(free | awk 'NR==2 {printf "%.0f", $3*100/$2}')
    
    if [ "$mem_usage" -gt 90 ]; then
        echo "$(date): Memory usage high: $mem_usage%" >> "$LOG_FILE"
        echo "⚠️  Memory usage is at $mem_usage%" | mail -s "Warning: $DOMAIN Memory" "$EMAIL"
        return 1
    fi
    
    return 0
}

# Check SSL certificate expiry
check_ssl() {
    local expiry_date=$(echo | openssl s_client -servername "$DOMAIN" -connect "$DOMAIN:443" 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)
    local expiry_epoch=$(date -d "$expiry_date" +%s)
    local current_epoch=$(date +%s)
    local days_until_expiry=$(( ($expiry_epoch - $current_epoch) / 86400 ))
    
    if [ "$days_until_expiry" -lt 30 ]; then
        echo "$(date): SSL certificate expires in $days_until_expiry days" >> "$LOG_FILE"
        echo "⚠️  SSL certificate expires in $days_until_expiry days" | mail -s "Warning: $DOMAIN SSL Expiry" "$EMAIL"
        return 1
    fi
    
    return 0
}

# Main monitoring function
main() {
    echo "=== Starting monitoring check at $(date) ===" >> "$LOG_FILE"
    
    check_health
    check_database
    check_disk
    check_memory
    check_ssl
    
    echo "=== Monitoring check completed at $(date) ===" >> "$LOG_FILE"
}

main
```

**Setup:**
```bash
chmod +x /var/www/genx-fx/monitor.sh

# Add to crontab (runs every 5 minutes)
crontab -e
# Add: */5 * * * * /var/www/genx-fx/monitor.sh
```

### 2. Uptime Monitoring Services (Recommended)

#### UptimeRobot (Free)
- **URL:** https://uptimerobot.com
- **Setup:**
  1. Create account
  2. Add monitor: `https://lengkundee01.org/health`
  3. Set check interval: 5 minutes
  4. Configure alerts: Email, SMS, Slack

#### Pingdom (Paid)
- **URL:** https://www.pingdom.com
- Advanced monitoring with detailed reports

#### StatusCake (Freemium)
- **URL:** https://www.statuscake.com
- Free tier with basic monitoring

### 3. Docker Health Checks

Already configured in `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD", "node", "-e", "require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1);})"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Check container health:**
```bash
docker-compose ps
# Look for "healthy" status

docker inspect --format='{{.State.Health.Status}}' productionapp_app_1
```

## 📈 Log Management

### 1. Application Logs

**Location:** `/var/www/genx-fx/ProductionApp/logs/`

**View logs:**
```bash
# Real-time application logs
docker-compose logs -f app

# Last 100 lines
docker-compose logs --tail=100 app

# MongoDB logs
docker-compose logs mongo

# Redis logs
docker-compose logs redis
```

### 2. Nginx Logs

**Locations:**
- Access log: `/var/log/nginx/genx-fx-access.log`
- Error log: `/var/log/nginx/genx-fx-error.log`

**View logs:**
```bash
# Real-time access log
sudo tail -f /var/log/nginx/genx-fx-access.log

# Real-time error log
sudo tail -f /var/log/nginx/genx-fx-error.log

# Search for errors
sudo grep "error" /var/log/nginx/genx-fx-error.log

# Count 404 errors
sudo grep "404" /var/log/nginx/genx-fx-access.log | wc -l
```

### 3. System Logs

```bash
# System journal
sudo journalctl -u docker -f

# Nginx service logs
sudo journalctl -u nginx -f

# System errors
sudo journalctl -p err -f
```

### 4. Log Rotation

Already configured in deployment guide. Verify with:

```bash
# Check log rotation config
cat /etc/logrotate.d/genx-fx

# Test log rotation
sudo logrotate -f /etc/logrotate.d/genx-fx
```

## 📊 Performance Monitoring

### 1. Application Metrics

Monitor these key metrics:

**Response Time:**
```bash
# Test API response time
curl -w "@curl-format.txt" -o /dev/null -s https://lengkundee01.org/health

# curl-format.txt content:
time_namelookup:  %{time_namelookup}\n
time_connect:  %{time_connect}\n
time_appconnect:  %{time_appconnect}\n
time_pretransfer:  %{time_pretransfer}\n
time_redirect:  %{time_redirect}\n
time_starttransfer:  %{time_starttransfer}\n
time_total:  %{time_total}\n
```

**Request Rate:**
```bash
# Count requests per minute
sudo tail -10000 /var/log/nginx/genx-fx-access.log | awk '{print $4}' | cut -d: -f1-2 | sort | uniq -c
```

### 2. Database Monitoring

```bash
# MongoDB status
docker-compose exec mongo mongosh --eval "db.serverStatus()"

# Database size
docker-compose exec mongo mongosh --eval "db.stats()"

# Connection count
docker-compose exec mongo mongosh --eval "db.serverStatus().connections"
```

### 3. System Resources

```bash
# CPU usage
top -bn1 | grep "Cpu(s)"

# Memory usage
free -h

# Disk usage
df -h

# Docker container stats
docker stats --no-stream
```

## 🚨 Alert Configuration

### Email Alerts

Configure in monitoring script:
```bash
EMAIL="your-email@example.com"
```

### Slack Alerts

Use Slack webhooks:
```bash
SLACK_WEBHOOK="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

send_slack_alert() {
    local message="$1"
    curl -X POST "$SLACK_WEBHOOK" -H 'Content-Type: application/json' -d "{\"text\":\"$message\"}"
}
```

### SMS Alerts (via Twilio)

```bash
TWILIO_SID="your_sid"
TWILIO_TOKEN="your_token"
TWILIO_FROM="+1234567890"
TWILIO_TO="+1234567890"

send_sms_alert() {
    local message="$1"
    curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_SID/Messages.json" \
        --data-urlencode "From=$TWILIO_FROM" \
        --data-urlencode "To=$TWILIO_TO" \
        --data-urlencode "Body=$message" \
        -u "$TWILIO_SID:$TWILIO_TOKEN"
}
```

## 📋 Monitoring Checklist

Daily monitoring tasks:

- [ ] Check application health endpoint
- [ ] Review error logs for issues
- [ ] Verify all containers are running
- [ ] Check disk space usage
- [ ] Review access logs for unusual activity
- [ ] Verify backup completion
- [ ] Check SSL certificate status
- [ ] Monitor response times
- [ ] Review database performance
- [ ] Check for security alerts

## 🔧 Troubleshooting

### High CPU Usage
```bash
# Identify processes
top -bn1 | head -20

# Check Docker containers
docker stats

# Restart if needed
docker-compose restart
```

### High Memory Usage
```bash
# Clear page cache
sudo sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'

# Restart containers
docker-compose restart
```

### Slow Response Times
```bash
# Check database performance
docker-compose exec mongo mongosh --eval "db.currentOp()"

# Check slow queries
docker-compose logs app | grep "slow"
```

## 📚 Additional Tools

- **Prometheus + Grafana**: Advanced metrics and dashboards
- **ELK Stack**: Centralized log management
- **New Relic**: Application performance monitoring
- **Datadog**: Infrastructure monitoring
- **Sentry**: Error tracking and monitoring

---

**Last Updated:** January 2026  
**Version:** 1.0.0

For deployment instructions, see [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md)
