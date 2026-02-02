# Website Deployment Guide - lengkundee01.org

## Overview

This guide provides step-by-step instructions for deploying the GenX_FX trading system documentation and services to lengkundee01.org.

---

## Deployment Architecture

### Services Overview

```
lengkundee01.org (Main Site)
├── lengkundee01.org              → Landing page / Documentation hub
├── www.lengkundee01.org          → Alias to main site
├── api.lengkundee01.org          → REST API for trading operations
├── trading.lengkundee01.org      → Trading dashboard and analytics
├── docs.lengkundee01.org         → Full documentation site
└── status.lengkundee01.org       → System health monitoring
```

### Technology Stack
- **Web Server**: Nginx 1.18+
- **SSL**: Let's Encrypt (Certbot)
- **Backend**: Python 3.9+ (Flask/FastAPI)
- **Documentation**: MkDocs or Jekyll
- **Monitoring**: Custom health checks + UptimeRobot
- **Process Manager**: systemd services

---

## Prerequisites

### Required Setup
- [x] Domain registered: lengkundee01.org
- [x] DNS configured (see [DNS_SETUP_GUIDE.md](DNS_SETUP_GUIDE.md))
- [ ] VPS with Ubuntu 22.04 LTS
- [ ] Root or sudo access to VPS
- [ ] SSH access configured

### Software Requirements
```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install essential packages
sudo apt-get install -y \
    nginx \
    python3 \
    python3-pip \
    python3-venv \
    git \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban
```

---

## Phase 1: Main Documentation Site

### Step 1.1: Install Static Site Generator

#### Option A: MkDocs (Recommended)
```bash
# Install MkDocs
pip3 install mkdocs mkdocs-material

# Create project structure
cd /var/www
sudo mkdir -p lengkundee01.org
sudo chown $USER:$USER lengkundee01.org
cd lengkundee01.org

# Initialize MkDocs project
mkdocs new .
```

#### Option B: Jekyll
```bash
# Install Ruby and Jekyll
sudo apt-get install ruby-full build-essential zlib1g-dev
gem install jekyll bundler

# Create Jekyll site
cd /var/www
sudo mkdir -p lengkundee01.org
sudo chown $USER:$USER lengkundee01.org
cd lengkundee01.org
jekyll new .
```

### Step 1.2: Copy Documentation

```bash
# Clone repository to a secure location (not /tmp for security)
sudo mkdir -p /opt/genx-deploy
sudo chown $USER:$USER /opt/genx-deploy

# Set repository URL (update if needed)
REPO_URL="https://github.com/Mouy-leng/GenX_FX-c62abe22.git"
git clone "$REPO_URL" /opt/genx-deploy/GenX_FX
cd /opt/genx-deploy/GenX_FX

# Copy documentation files
cp -r *.md /var/www/lengkundee01.org/docs/
cp -r A6-9V/Trading/GenX_FX/docs/* /var/www/lengkundee01.org/docs/

# Build static site
cd /var/www/lengkundee01.org
mkdocs build
```

### Step 1.3: Configure Nginx

Create: `/etc/nginx/sites-available/lengkundee01.org`
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name lengkundee01.org www.lengkundee01.org;
    
    root /var/www/lengkundee01.org/site;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'self';" always;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Cache static files
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/lengkundee01.org /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Phase 2: API Deployment

### Step 2.1: Prepare API Application

```bash
# Create API directory
sudo mkdir -p /var/www/api.lengkundee01.org
sudo chown $USER:$USER /var/www/api.lengkundee01.org
cd /var/www/api.lengkundee01.org

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask flask-cors gunicorn
```

### Step 2.2: Deploy API Code

Copy and adapt from repository:
```bash
# Copy API server
cp /opt/genx-deploy/GenX_FX/A6-9V/Trading/GenX_FX/local_server.py app.py

# Create production WSGI entry point
cat > wsgi.py << 'EOF'
from app import app

if __name__ == "__main__":
    app.run()
EOF
```

### Step 2.3: Create Systemd Service

Create: `/etc/systemd/system/genx-api.service`
```ini
[Unit]
Description=GenX FX Trading API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/api.lengkundee01.org
Environment="PATH=/var/www/api.lengkundee01.org/venv/bin"
ExecStart=/var/www/api.lengkundee01.org/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 wsgi:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ensure correct ownership for the www-data service account:
```bash
sudo chown -R www-data:www-data /var/www/api.lengkundee01.org
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable genx-api
sudo systemctl start genx-api
sudo systemctl status genx-api
```

### Step 2.4: Configure Nginx for API

First, create rate limiting configuration in http context:

Create: `/etc/nginx/conf.d/rate-limit.conf`
```nginx
# Rate limiting zone - must be in http context
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
```

Then create: `/etc/nginx/sites-available/api.lengkundee01.org`
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name api.lengkundee01.org;
    
    # Handle CORS preflight OPTIONS requests
    location / {
        # Handle preflight requests
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' 'https://lengkundee01.org' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000;
            add_header 'Content-Type' 'text/plain; charset=utf-8';
            add_header 'Content-Length' 0;
            return 204;
        }
        
        # Rate limiting (zone defined in /etc/nginx/conf.d/rate-limit.conf)
        limit_req zone=api_limit burst=20;
        
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers for actual requests
        add_header 'Access-Control-Allow-Origin' 'https://lengkundee01.org' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'Content-Type, Authorization' always;
        add_header 'Access-Control-Allow-Credentials' 'true' always;
    }
    
    location /health {
        proxy_pass http://127.0.0.1:5000/health;
        access_log off;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/api.lengkundee01.org /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Phase 3: Trading Dashboard

### Step 3.1: Prepare Dashboard Application

```bash
# Create dashboard directory
sudo mkdir -p /var/www/trading.lengkundee01.org
sudo chown $USER:$USER /var/www/trading.lengkundee01.org
cd /var/www/trading.lengkundee01.org

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install flask plotly pandas
```

### Step 3.2: Create Simple Dashboard

Create: `app.py`
```python
from flask import Flask, render_template, jsonify
import plotly.graph_objs as go
import plotly.utils
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/performance')
def performance():
    # Mock data - replace with actual trading data
    # Integration tasks tracked in repository issues:
    # - Import from A6-9V/Trading/GenX_FX/main.py for real trading data
    # - Connect to trading database for historical performance
    # - Use MetaTrader 5 API for live account metrics
    # - See DEPLOYMENT_SUMMARY.md for available data sources
    data = {
        'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'values': [100, 150, 120, 180, 200]
    }
    return jsonify(data)

if __name__ == '__main__':
    # Development server only - do NOT use in production
    # In production, use Gunicorn via the systemd service
    app.run(debug=True)
```

Create the templates directory and template file:
```bash
mkdir -p templates
```

Create: `templates/dashboard.html`
```html
<!DOCTYPE html>
<html>
<head>
    <title>GenX FX Trading Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #333; }
        #chart { width: 100%; height: 500px; }
    </style>
</head>
<body>
    <h1>GenX FX Trading Dashboard</h1>
    <div id="chart"></div>
    <script>
        fetch('/api/performance')
            .then(response => response.json())
            .then(data => {
                var trace = {
                    x: data.labels,
                    y: data.values,
                    type: 'scatter'
                };
                Plotly.newPlot('chart', [trace]);
            });
    </script>
</body>
</html>
```

### Step 3.3: Create Systemd Service

First, install Gunicorn for production use:
```bash
pip install gunicorn
```

Create: `/etc/systemd/system/genx-dashboard.service`
```ini
[Unit]
Description=GenX FX Trading Dashboard
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/trading.lengkundee01.org
Environment="PATH=/var/www/trading.lengkundee01.org/venv/bin"
ExecStart=/var/www/trading.lengkundee01.org/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --timeout 120 app:app

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ensure correct ownership for the www-data service account:
```bash
sudo chown -R www-data:www-data /var/www/trading.lengkundee01.org
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable genx-dashboard
sudo systemctl start genx-dashboard
sudo systemctl status genx-dashboard
```

### Step 3.4: Configure Nginx for Dashboard

Create: `/etc/nginx/sites-available/trading.lengkundee01.org`
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name trading.lengkundee01.org;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/trading.lengkundee01.org /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Phase 4: SSL Certificates

### Step 4.1: Install Certbot

```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

### Step 4.2: Obtain Certificates

```bash
# Main domain
sudo certbot --nginx -d lengkundee01.org -d www.lengkundee01.org

# API
sudo certbot --nginx -d api.lengkundee01.org

# Trading dashboard
sudo certbot --nginx -d trading.lengkundee01.org

# Documentation
sudo certbot --nginx -d docs.lengkundee01.org

# Status page
sudo certbot --nginx -d status.lengkundee01.org
```

### Step 4.3: Test Auto-Renewal

```bash
sudo certbot renew --dry-run
```

### Step 4.4: Verify HTTPS

```bash
# Test each domain
curl -I https://lengkundee01.org
curl -I https://api.lengkundee01.org
curl -I https://trading.lengkundee01.org
```

---

## Phase 5: Security Configuration

### Step 5.1: Configure Firewall

```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check status
sudo ufw status verbose
```

### Step 5.2: Configure Fail2Ban

Create: `/etc/fail2ban/jail.local`
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
```

Enable and start:
```bash
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
sudo systemctl status fail2ban
```

### Step 5.3: Enhance Nginx Security

Update all Nginx configs to include:
```nginx
# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self'; frame-ancestors 'self'; object-src 'none'; base-uri 'self';" always;

# Hide Nginx version
server_tokens off;
```

---

## Phase 6: Monitoring and Maintenance

### Step 6.1: System Health Checks

Create: `/usr/local/bin/health-check.sh`
```bash
#!/bin/bash

# Check services
services=("nginx" "genx-api" "genx-dashboard")

for service in "${services[@]}"; do
    if ! systemctl is-active --quiet "$service"; then
        echo "⚠️  $service is not running!"
        systemctl restart "$service"
    else
        echo "✅ $service is running"
    fi
done

# Check disk space
df -h | grep -E '^/dev/' | awk '{ print $1 ": " $5 " used" }'

# Check SSL certificates
certbot certificates | grep -E 'Expiry Date'
```

Make executable:
```bash
sudo chmod +x /usr/local/bin/health-check.sh
```

### Step 6.2: Setup Cron Jobs

```bash
# Edit crontab
sudo crontab -e

# Add health check (every 5 minutes)
*/5 * * * * /usr/local/bin/health-check.sh >> /var/log/health-check.log 2>&1

# SSL renewal check (daily)
0 0 * * * certbot renew --quiet

# Nginx log rotation (weekly)
0 0 * * 0 sudo logrotate /etc/logrotate.d/nginx
```

### Step 6.3: External Monitoring

Sign up for UptimeRobot (free tier):
- Monitor https://lengkundee01.org
- Monitor https://api.lengkundee01.org/health
- Monitor https://trading.lengkundee01.org
- Alert to: lengkundee01@gmail.com

---

## Deployment Checklist

### Pre-Deployment
- [ ] VPS provisioned and accessible
- [ ] DNS records configured and propagated
- [ ] Domain resolves to VPS IP
- [ ] SSH access configured
- [ ] Required software installed

### Main Site Deployment
- [ ] Static site generator installed
- [ ] Documentation copied and built
- [ ] Nginx configured for main site
- [ ] Site accessible via HTTP
- [ ] SSL certificate obtained
- [ ] HTTPS working correctly

### API Deployment
- [ ] API application deployed
- [ ] Systemd service created and running
- [ ] Nginx reverse proxy configured
- [ ] API accessible via HTTP
- [ ] SSL certificate obtained
- [ ] API endpoints tested

### Dashboard Deployment
- [ ] Dashboard application deployed
- [ ] Systemd service created and running
- [ ] Nginx reverse proxy configured
- [ ] Dashboard accessible via HTTP
- [ ] SSL certificate obtained
- [ ] Dashboard functionality tested

### Security Configuration
- [ ] Firewall configured and enabled
- [ ] Fail2Ban installed and configured
- [ ] Security headers added to Nginx
- [ ] All HTTP redirects to HTTPS
- [ ] SSL certificates auto-renew

### Monitoring Setup
- [ ] Health check script created
- [ ] Cron jobs configured
- [ ] External monitoring (UptimeRobot) setup
- [ ] Alert notifications configured
- [ ] Log rotation configured

### Final Verification
- [ ] All domains accessible via HTTPS
- [ ] No SSL certificate warnings
- [ ] API endpoints responding correctly
- [ ] Dashboard loading and functional
- [ ] Health checks passing
- [ ] Monitoring alerts working

---

## Troubleshooting

### Service Not Starting

```bash
# Check service status
sudo systemctl status genx-api

# View logs
sudo journalctl -u genx-api -n 50

# Test application directly
cd /var/www/api.lengkundee01.org
source venv/bin/activate
python wsgi.py
```

### Nginx Configuration Error

```bash
# Test configuration
sudo nginx -t

# Check error logs
sudo tail -f /var/log/nginx/error.log

# Restart Nginx
sudo systemctl restart nginx
```

### SSL Certificate Issues

```bash
# List certificates
sudo certbot certificates

# Renew specific certificate
sudo certbot renew --cert-name lengkundee01.org

# Force renewal
sudo certbot renew --force-renewal
```

---

## Related Documentation

- [Domain Configuration](DOMAIN_CONFIGURATION.md)
- [DNS Setup Guide](DNS_SETUP_GUIDE.md)
- [VPS Configuration](VPS_CONFIGURATION.md)
- [Deployment Summary](A6-9V/Trading/GenX_FX/DEPLOYMENT_SUMMARY.md)

---

**Guide Version**: 1.0  
**Created**: January 6, 2026  
**Domain**: lengkundee01.org  
**Target Platform**: Ubuntu 22.04 LTS
