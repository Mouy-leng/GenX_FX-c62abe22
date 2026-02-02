# Quick Start: Domain Deployment

This guide helps you quickly deploy GenX_FX to your Namecheap domain in under 30 minutes.

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] A domain name from Namecheap (or other registrar)
- [ ] A VPS server (DigitalOcean, AWS, Linode, etc.)
- [ ] SSH access to your server
- [ ] Your server's IP address
- [ ] Basic command line knowledge

## ⚡ 5-Step Quick Deployment

### Step 1: Configure DNS (5 minutes)

1. Log in to Namecheap dashboard
2. Go to **Domain List** → **Manage** → **Advanced DNS**
3. Add these records:

```
Type: A Record
Host: @
Value: YOUR_SERVER_IP

Type: A Record  
Host: www
Value: YOUR_SERVER_IP
```

4. Save and wait for DNS propagation (1-48 hours)

**Verify DNS:**
```bash
nslookup lengkundee01.org
```

### Step 2: Server Setup (10 minutes)

SSH into your server and run:

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git and Nginx
sudo apt install git nginx certbot python3-certbot-nginx -y

# Configure firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

### Step 3: Clone and Configure (5 minutes)

```bash
# Create directory and clone
sudo mkdir -p /var/www/genx-fx
cd /var/www/genx-fx
sudo git clone https://github.com/Mouy-leng/GenX_FX-c62abe22.git .
sudo chown -R $USER:$USER /var/www/genx-fx

# Configure environment
cd ProductionApp
cp .env.example .env

# Edit .env file
nano .env
```

**Update these values in .env:**
```bash
NODE_ENV=production
DOMAIN=lengkundee01.org
APP_URL=https://lengkundee01.org
CORS_ORIGIN=https://lengkundee01.org

# Generate a strong JWT secret
JWT_SECRET=YOUR_STRONG_SECRET_HERE
```

**Generate JWT secret:**
```bash
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```

### Step 4: Setup SSL Certificate (5 minutes)

```bash
# Stop nginx temporarily
sudo systemctl stop nginx

# Get SSL certificate (replace with your domain and email)
sudo certbot certonly --standalone \
  -d lengkundee01.org \
  -d www.lengkundee01.org \
  --email your-email@example.com \
  --agree-tos \
  --non-interactive

# Start nginx
sudo systemctl start nginx
```

### Step 5: Deploy Application (5 minutes)

```bash
# Run deployment script
cd /var/www/genx-fx
chmod +x deploy.sh
sudo ./deploy.sh

# Configure nginx
sudo nano /etc/nginx/sites-available/genx-fx
```

**Paste this nginx configuration** (replace `lengkundee01.org` with your actual domain):

```nginx
server {
    listen 80;
    server_name lengkundee01.org www.lengkundee01.org;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name lengkundee01.org www.lengkundee01.org;

    ssl_certificate /etc/letsencrypt/live/lengkundee01.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/lengkundee01.org/privkey.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable and restart nginx:**
```bash
sudo ln -s /etc/nginx/sites-available/genx-fx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## ✅ Verification

Test your deployment:

```bash
# Check health endpoint
curl https://lengkundee01.org/health

# Check SSL
curl -I https://lengkundee01.org

# Check application
curl https://lengkundee01.org/
```

Visit in browser:
- https://lengkundee01.org
- https://lengkundee01.org/health

## 🎉 Success!

Your GenX_FX application is now live!

## 🔄 Updating Your Deployment

To update your application after code changes:

```bash
cd /var/www/genx-fx
git pull origin main
sudo ./deploy.sh
```

## 🚨 Troubleshooting

### DNS Not Resolving
```bash
# Check DNS propagation
nslookup lengkundee01.org
dig lengkundee01.org

# Wait and try again (can take up to 48 hours)
```

### SSL Certificate Failed
```bash
# Check if port 80 is free
sudo netstat -tulpn | grep :80

# Try with nginx plugin instead
sudo certbot --nginx -d lengkundee01.org -d www.lengkundee01.org
```

### Application Not Starting
```bash
# Check logs
cd /var/www/genx-fx/ProductionApp
docker-compose logs app

# Restart services
docker-compose restart

# Check if ports are in use
sudo netstat -tulpn | grep :3000
```

### Can't Access Application
```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check firewall
sudo ufw status

# Check if containers are running
docker-compose ps
```

## 📚 Next Steps

Now that your application is deployed:

1. **Setup Monitoring:** See [MONITORING_GUIDE.md](MONITORING_GUIDE.md)
2. **Configure Backups:** Setup automated database backups
3. **Enable Monitoring:** Use UptimeRobot or similar service
4. **Review Security:** Check [CREDENTIAL_SECURITY_REPORT.md](CREDENTIAL_SECURITY_REPORT.md)
5. **Setup CI/CD:** Configure GitHub Actions for automated deployment

## 🔒 Security Checklist

After deployment, ensure:

- [ ] Strong JWT secret configured
- [ ] SSL certificate installed and auto-renewing
- [ ] Firewall configured correctly
- [ ] MongoDB secured with authentication
- [ ] Regular backups configured
- [ ] Monitoring alerts setup
- [ ] Server security updates enabled

## 📞 Need Help?

- **Detailed Guide:** [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md)
- **DNS Help:** [DNS_CONFIGURATION_GUIDE.md](DNS_CONFIGURATION_GUIDE.md)
- **Monitoring:** [MONITORING_GUIDE.md](MONITORING_GUIDE.md)
- **Issues:** https://github.com/Mouy-leng/GenX_FX-c62abe22/issues

## 🎯 Common Commands Reference

```bash
# View application logs
cd /var/www/genx-fx/ProductionApp && docker-compose logs -f app

# Restart application
cd /var/www/genx-fx/ProductionApp && docker-compose restart

# Stop application
cd /var/www/genx-fx/ProductionApp && docker-compose down

# Start application
cd /var/www/genx-fx/ProductionApp && docker-compose up -d

# Check SSL expiry
sudo certbot certificates

# Renew SSL manually
sudo certbot renew

# Check nginx status
sudo systemctl status nginx

# Restart nginx
sudo systemctl restart nginx
```

---

**Estimated Total Time:** 30 minutes (excluding DNS propagation)

**Last Updated:** January 2026  
**Version:** 1.0.0
