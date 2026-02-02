# Domain Deployment Guide - GenX_FX

## 📋 Overview

This guide provides step-by-step instructions for deploying the GenX_FX application to your custom domain purchased from Namecheap or any other domain registrar.

## 🎯 Prerequisites

Before you begin, ensure you have:

- ✅ A domain name (from Namecheap or other registrar)
- ✅ A VPS or cloud server (AWS, DigitalOcean, Linode, etc.)
- ✅ SSH access to your server
- ✅ Root or sudo privileges
- ✅ Basic knowledge of DNS and server administration

## 🌐 Step 1: Domain Configuration (Namecheap)

### 1.1 Access Namecheap Dashboard

1. Log in to your Namecheap account
2. Navigate to **Domain List**
3. Click **Manage** next to your domain

### 1.2 Configure DNS Records

Navigate to **Advanced DNS** and add the following records:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | `YOUR_VPS_IP` | Automatic |
| A Record | www | `YOUR_VPS_IP` | Automatic |
| CNAME Record | api | `your-domain.com` | Automatic |
| CNAME Record | app | `your-domain.com` | Automatic |

**Example:**
```
A Record:    @        ->  192.168.1.100
A Record:    www      ->  192.168.1.100
CNAME:       api      ->  your-domain.com
CNAME:       app      ->  your-domain.com
```

### 1.3 Wait for DNS Propagation

DNS changes can take 1-48 hours to propagate. You can check propagation status at:
- https://www.whatsmydns.net/
- https://dnschecker.org/

## 🖥️ Step 2: Server Setup

### 2.1 Update System

```bash
# SSH into your server
ssh root@YOUR_VPS_IP

# Update system packages
sudo apt update && sudo apt upgrade -y
```

### 2.2 Install Required Software

```bash
# Install Docker and Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Nginx
sudo apt install nginx -y

# Install Certbot for SSL
sudo apt install certbot python3-certbot-nginx -y

# Install Git
sudo apt install git -y

# Install Node.js (LTS version)
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs
```

### 2.3 Configure Firewall

```bash
# Allow SSH, HTTP, HTTPS
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

## 📦 Step 3: Clone and Configure Application

### 3.1 Clone Repository

```bash
# Create application directory
sudo mkdir -p /var/www/genx-fx
cd /var/www/genx-fx

# Clone repository
sudo git clone https://github.com/Mouy-leng/GenX_FX-c62abe22.git .

# Set permissions
sudo chown -R $USER:$USER /var/www/genx-fx
```

### 3.2 Configure Environment Variables

```bash
# Navigate to ProductionApp
cd /var/www/genx-fx/ProductionApp

# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

**Update the following variables:**

```bash
# Production Configuration
NODE_ENV=production
PORT=3000

# Domain Configuration
DOMAIN=your-domain.com
CORS_ORIGIN=https://your-domain.com
API_URL=https://api.your-domain.com

# Database Configuration
MONGODB_URI=mongodb://mongo:27017/productionapp
DB_NAME=productionapp

# JWT Configuration (GENERATE A STRONG SECRET!)
JWT_SECRET=REPLACE_WITH_STRONG_RANDOM_SECRET_64_CHARS_OR_MORE
JWT_EXPIRE=7d

# Security
BCRYPT_SALT_ROUNDS=12

# Rate Limiting
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

**Generate a strong JWT secret:**
```bash
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

## 🔐 Step 4: SSL Certificate Setup

### 4.1 Obtain SSL Certificate

```bash
# Stop Nginx temporarily
sudo systemctl stop nginx

# Obtain certificate
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Start Nginx
sudo systemctl start nginx
```

### 4.2 Auto-Renewal Setup

```bash
# Test renewal
sudo certbot renew --dry-run

# Certbot automatically sets up auto-renewal via systemd timer
# Verify it's enabled:
sudo systemctl status certbot.timer
```

## 🌐 Step 5: Nginx Configuration

### 5.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/genx-fx
```

**Add the following configuration:**

```nginx
# HTTP - Redirect to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

# HTTPS - Main Application
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/genx-fx-access.log;
    error_log /var/log/nginx/genx-fx-error.log;

    # Root and index
    root /var/www/genx-fx/ProductionApp/public;
    index index.html;

    # Proxy settings
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 90;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:3000/health;
        access_log off;
    }

    # API endpoints
    location /api/ {
        proxy_pass http://localhost:3000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers (if needed)
        add_header Access-Control-Allow-Origin https://your-domain.com always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type" always;
    }

    # Static files with caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

### 5.2 Enable Site and Restart Nginx

```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/genx-fx /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

## 🐳 Step 6: Deploy with Docker

### 6.1 Update Docker Compose

Edit `/var/www/genx-fx/ProductionApp/docker-compose.yml`:

```bash
cd /var/www/genx-fx/ProductionApp
nano docker-compose.yml
```

Update the app service environment:

```yaml
environment:
  - NODE_ENV=production
  - PORT=3000
  - DOMAIN=your-domain.com
  - MONGODB_URI=mongodb://mongo:27017/productionapp
  - JWT_SECRET=${JWT_SECRET}
  - JWT_EXPIRE=7d
  - BCRYPT_SALT_ROUNDS=12
  - CORS_ORIGIN=https://your-domain.com
```

### 6.2 Start Services

```bash
# Build and start services
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f app
```

## ✅ Step 7: Verification

### 7.1 Test Health Endpoints

```bash
# Test HTTP redirect
curl -I http://your-domain.com

# Test HTTPS
curl https://your-domain.com/health

# Test API
curl https://your-domain.com/api/health
```

### 7.2 Verify SSL Certificate

```bash
# Check SSL certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com
```

### 7.3 Check Application Logs

```bash
# Application logs
docker-compose logs -f app

# Nginx access logs
sudo tail -f /var/log/nginx/genx-fx-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/genx-fx-error.log
```

## 🔄 Step 8: Continuous Deployment

### 8.1 Create Deployment Script

```bash
sudo nano /var/www/genx-fx/deploy.sh
```

```bash
#!/bin/bash

echo "🚀 Starting deployment..."

# Navigate to project directory
cd /var/www/genx-fx

# Pull latest changes
git pull origin main

# Navigate to ProductionApp
cd ProductionApp

# Rebuild and restart services
docker-compose down
docker-compose up -d --build

echo "✅ Deployment completed!"
echo "📊 Checking service status..."
docker-compose ps
```

```bash
# Make executable
sudo chmod +x /var/www/genx-fx/deploy.sh
```

### 8.2 Deploy Updates

```bash
# Run deployment script
cd /var/www/genx-fx
./deploy.sh
```

## 📊 Step 9: Monitoring Setup

### 9.1 Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/genx-fx
```

```
/var/log/nginx/genx-fx-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 `cat /var/run/nginx.pid`
    endscript
}
```

### 9.2 Setup Health Check Monitoring

Create a monitoring script:

```bash
nano /var/www/genx-fx/monitor.sh
```

```bash
#!/bin/bash

DOMAIN="your-domain.com"
EMAIL="your-email@example.com"

# Check if site is up
if ! curl -sf https://$DOMAIN/health > /dev/null; then
    echo "❌ Site is DOWN!" | mail -s "Site Down Alert: $DOMAIN" $EMAIL
    # Restart services
    cd /var/www/genx-fx/ProductionApp
    docker-compose restart
fi
```

```bash
chmod +x /var/www/genx-fx/monitor.sh

# Add to crontab (every 5 minutes)
crontab -e
# Add: */5 * * * * /var/www/genx-fx/monitor.sh
```

## 🔒 Step 10: Security Hardening

### 10.1 Configure Fail2Ban

```bash
sudo apt install fail2ban -y

# Create custom jail for nginx
sudo nano /etc/fail2ban/jail.local
```

```ini
[nginx-http-auth]
enabled = true

[nginx-botsearch]
enabled = true

[nginx-badbots]
enabled = true
port = http,https
```

```bash
sudo systemctl restart fail2ban
```

### 10.2 Setup Automatic Security Updates

```bash
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 10.3 Secure MongoDB

```bash
# Access MongoDB container
docker-compose exec mongo mongosh

# Create admin user
use admin
db.createUser({
  user: "admin",
  pwd: "STRONG_PASSWORD_HERE",
  roles: ["root"]
})

# Enable authentication in docker-compose.yml
```

## 🎯 Deployment Checklist

Before going live, verify:

- [ ] DNS records configured and propagated
- [ ] SSL certificate obtained and installed
- [ ] Environment variables configured correctly
- [ ] Strong JWT secret generated
- [ ] MongoDB secured with authentication
- [ ] Nginx configured and tested
- [ ] Docker services running correctly
- [ ] Firewall rules configured
- [ ] Health endpoints responding
- [ ] HTTPS redirect working
- [ ] Logs being written correctly
- [ ] Monitoring setup and working
- [ ] Backup strategy implemented
- [ ] Security headers configured
- [ ] Rate limiting enabled
- [ ] CORS configured correctly

## 🆘 Troubleshooting

### DNS Not Resolving

```bash
# Check DNS propagation
nslookup your-domain.com
dig your-domain.com

# Flush local DNS cache
sudo systemd-resolve --flush-caches
```

### SSL Certificate Issues

```bash
# Check certificate validity
sudo certbot certificates

# Renew certificate manually
sudo certbot renew --force-renewal
```

### Nginx Errors

```bash
# Check configuration syntax
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### Docker Issues

```bash
# Check container logs
docker-compose logs app

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Application Not Accessible

```bash
# Check if services are running
docker-compose ps

# Check nginx status
sudo systemctl status nginx

# Check if port is listening
sudo netstat -tulpn | grep :3000
```

## 📚 Additional Resources

- **Namecheap DNS Guide:** https://www.namecheap.com/support/knowledgebase/article.aspx/319/2237/how-can-i-set-up-an-a-address-record-for-my-domain
- **Let's Encrypt Documentation:** https://letsencrypt.org/docs/
- **Nginx Documentation:** https://nginx.org/en/docs/
- **Docker Documentation:** https://docs.docker.com/
- **Node.js Best Practices:** https://github.com/goldbergyoni/nodebestpractices

## 🎉 Deployment Complete!

Your GenX_FX application should now be accessible at:
- **Main Site:** https://your-domain.com
- **API:** https://your-domain.com/api
- **Health Check:** https://your-domain.com/health

---

**Last Updated:** January 2026  
**Version:** 1.0.0

For support, create an issue at: https://github.com/Mouy-leng/GenX_FX-c62abe22/issues
