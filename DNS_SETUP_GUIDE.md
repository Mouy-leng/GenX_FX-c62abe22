# DNS Setup Guide for lengkundee01.org

## Quick Start

This guide provides step-by-step instructions for configuring DNS records for lengkundee01.org with Namecheap.

---

## Prerequisites

- [x] Domain registered: lengkundee01.org (Order #191346179)
- [ ] VPS IP address obtained
- [ ] Namecheap account access
- [ ] Email: lengkundee01@gmail.com

---

## Step 1: Access Namecheap DNS Management

### Login to Namecheap
1. Go to https://www.namecheap.com
2. Click "Sign In" (top right)
3. Login with username: **LengNuna**
4. Enter password and complete 2FA if enabled

### Navigate to DNS Management
1. Click on "Domain List" in the left sidebar
2. Click "Manage" button next to **lengkundee01.org**
3. Select the "Advanced DNS" tab

---

## Step 2: Configure Basic DNS Records

### A Records (Main Domain)

Click "Add New Record" and configure:

#### Root Domain (@)
- **Type**: A Record
- **Host**: @
- **Value**: [203.147.134.218] (See VPS_CONFIGURATION.md or VPS dashboard)
- **TTL**: Automatic

#### WWW Subdomain
- **Type**: A Record
- **Host**: www
- **Value**: [203.147.134.218] (Same as root domain)
- **TTL**: Automatic

> **Note**: To find your VPS IP address, check [VPS_CONFIGURATION.md](VPS_CONFIGURATION.md) or login to your VPS provider dashboard.

### Example:
```
Type    Host    Value               TTL
A       @       203.0.113.10       Automatic
A       www     203.0.113.10       Automatic
```

---

## Step 3: Configure Subdomains

### Subdomain A Records

Add the following A records for subdomains:

#### API Subdomain
- **Type**: A Record
- **Host**: api
- **Value**: [203.147.134.218]
- **TTL**: Automatic

#### Trading Dashboard
- **Type**: A Record
- **Host**: trading
- **Value**: [203.147.134.218]
- **TTL**: Automatic

#### Documentation
- **Type**: A Record
- **Host**: docs
- **Value**: [203.147.134.218]
- **TTL**: Automatic

#### Status Page
- **Type**: A Record
- **Host**: status
- **Value**: [203.147.134.218]
- **TTL**: Automatic

### Complete Subdomain Configuration:
```
Type    Host       Value               TTL
A       api        203.0.113.10       Automatic
A       trading    203.0.113.10       Automatic
A       docs       203.0.113.10       Automatic
A       status     203.0.113.10       Automatic
```

---

## Step 4: Email Configuration (Optional)

### MX Records for Email

If you plan to use email with this domain:

#### Primary Mail Server
- **Type**: MX Record
- **Host**: @
- **Value**: mail.lengkundee01.org
- **Priority**: 10
- **TTL**: Automatic

#### Mail Server A Record
- **Type**: A Record
- **Host**: mail
- **Value**: [203.147.134.218]
- **TTL**: Automatic

---

## Step 5: Security Records

### SPF Record (Sender Policy Framework)

Prevent email spoofing:

- **Type**: TXT Record
- **Host**: @
- **Value**: v=spf1 a mx include:_spf.google.com ~all
- **TTL**: Automatic

### DMARC Record (Email Authentication)

- **Type**: TXT Record
- **Host**: _dmarc
- **Value**: v=DMARC1; p=none; rua=mailto:lengkundee01@gmail.com
- **TTL**: Automatic

---

## Step 6: Verification and Testing

### DNS Propagation Check

After configuring DNS records, check propagation:

1. **Online Tool**: https://dnschecker.org
   - Enter: lengkundee01.org
   - Check A, CNAME, MX records globally

2. **Command Line** (Windows):
   ```cmd
   nslookup lengkundee01.org
   nslookup api.lengkundee01.org
   nslookup trading.lengkundee01.org
   ```

3. **Command Line** (Linux/Mac):
   ```bash
   dig lengkundee01.org
   dig api.lengkundee01.org +short
   dig trading.lengkundee01.org +short
   ```

### Expected Results
```
lengkundee01.org          → 203.147.134.218
www.lengkundee01.org      → 203.147.134.218
api.lengkundee01.org      → 203.147.134.218
trading.lengkundee01.org  → 203.147.134.218
docs.lengkundee01.org     → 203.147.134.218
status.lengkundee01.org   → 203.147.134.218
```

---

## Step 7: Configure Web Server

### Nginx Configuration Example

Create server blocks for each subdomain:

#### Main Domain (/etc/nginx/sites-available/lengkundee01.org)
```nginx
server {
    listen 80;
    server_name lengkundee01.org www.lengkundee01.org;
    
    root /var/www/lengkundee01.org/html;
    index index.html index.htm;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

#### API Subdomain (/etc/nginx/sites-available/api.lengkundee01.org)
```nginx
server {
    listen 80;
    server_name api.lengkundee01.org;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Trading Dashboard (/etc/nginx/sites-available/trading.lengkundee01.org)
```nginx
server {
    listen 80;
    server_name trading.lengkundee01.org;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable Sites
```bash
sudo ln -s /etc/nginx/sites-available/lengkundee01.org /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/api.lengkundee01.org /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/trading.lengkundee01.org /etc/nginx/sites-enabled/

sudo nginx -t
sudo systemctl reload nginx
```

---

## Step 8: SSL Certificate Installation

### Install Certbot
```bash
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx
```

### Obtain SSL Certificates
```bash
# Main domain and www
sudo certbot --nginx -d lengkundee01.org -d www.lengkundee01.org

# Subdomains
sudo certbot --nginx -d api.lengkundee01.org
sudo certbot --nginx -d trading.lengkundee01.org
sudo certbot --nginx -d docs.lengkundee01.org
sudo certbot --nginx -d status.lengkundee01.org
```

### Test Auto-Renewal
```bash
sudo certbot renew --dry-run
```

### Certificate Renewal (Automatic)
Certbot automatically sets up a systemd timer:
```bash
sudo systemctl status certbot.timer
```

---

## Complete DNS Record Summary

After completing all steps, your DNS records should look like:

### A Records
```
Host       Type    Value               TTL
@          A       203.147.134.218        Automatic
www        A       203.147.134.218        Automatic
api        A       203.147.134.218        Automatic
trading    A       203.147.134.218        Automatic
docs       A       203.147.134.218        Automatic
status     A       203.147.134.218        Automatic
mail       A       203.147.134.218        Automatic (optional)
```

### MX Records (Optional)
```
Host       Type    Priority    Value                   TTL
@          MX      10          mail.lengkundee01.org   Automatic
```

### TXT Records
```
Host       Type    Value
@          TXT     v=spf1 include:_spf.google.com ~all
_dmarc     TXT     v=DMARC1; p=none; rua=mailto:lengkundee01@gmail.com
```

---

## Troubleshooting

### Issue: DNS Not Resolving

**Problem**: Domain doesn't resolve to IP address

**Solutions**:
1. Wait 24-48 hours for DNS propagation
2. Clear local DNS cache:
   - Windows: `ipconfig /flushdns`
   - Linux: `sudo systemd-resolve --flush-caches`
   - Mac: `sudo dscacheutil -flushcache`
3. Verify DNS records in Namecheap dashboard
4. Check if nameservers are Namecheap's:
   ```
   dns1.registrar-servers.com
   dns2.registrar-servers.com
   ```

### Issue: Website Not Loading

**Problem**: Domain resolves but website doesn't load

**Solutions**:
1. Check web server is running:
   ```bash
   sudo systemctl status nginx
   ```
2. Check firewall rules:
   ```bash
   sudo ufw status
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```
3. Verify web server configuration:
   ```bash
   sudo nginx -t
   ```
4. Check error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### Issue: SSL Certificate Error

**Problem**: HTTPS doesn't work or shows certificate error

**Solutions**:
1. Verify certificate installation:
   ```bash
   sudo certbot certificates
   ```
2. Check certificate expiry date
3. Renew certificate manually:
   ```bash
   sudo certbot renew
   ```
4. Verify Nginx SSL configuration
5. Test with SSL Labs: https://www.ssllabs.com/ssltest/

### Issue: Subdomain Not Working

**Problem**: Main domain works but subdomains don't

**Solutions**:
1. Verify subdomain A records exist in Namecheap
2. Check DNS propagation for subdomain:
   ```bash
   nslookup api.lengkundee01.org
   ```
3. Verify Nginx server block for subdomain exists
4. Check if server block is enabled:
   ```bash
   ls -la /etc/nginx/sites-enabled/
   ```
5. Restart Nginx:
   ```bash
   sudo systemctl restart nginx
   ```

---

## Important Notes

### DNS Propagation Time
- **Minimum**: 15-30 minutes
- **Average**: 2-4 hours
- **Maximum**: 24-48 hours

DNS changes don't happen instantly. Be patient and use online tools to check propagation status.

### TTL (Time To Live)
- **Automatic**: Namecheap manages TTL automatically
- **Before changes**: Lower TTL (300s) for faster propagation
- **After changes**: Higher TTL (3600s) for better performance

### Domain Privacy
- **Status**: ✅ Enabled (Free with registration)
- **WHOIS**: Contact information is private
- **Note**: Keep privacy enabled to protect personal information

---

## Checklist

Use this checklist to track your DNS setup progress:

### Initial Setup
- [ ] Access Namecheap DNS management
- [ ] Obtain VPS IP address
- [ ] Configure root (@) A record
- [ ] Configure www A record
- [ ] Test main domain resolution

### Subdomains
- [ ] Configure api.lengkundee01.org A record
- [ ] Configure trading.lengkundee01.org A record
- [ ] Configure docs.lengkundee01.org A record
- [ ] Configure status.lengkundee01.org A record
- [ ] Test all subdomain resolutions

### Web Server
- [ ] Install and configure Nginx
- [ ] Create server blocks for each domain/subdomain
- [ ] Test Nginx configuration
- [ ] Open firewall ports (80, 443)
- [ ] Test HTTP access

### SSL Certificates
- [ ] Install Certbot
- [ ] Obtain SSL certificate for main domain
- [ ] Obtain SSL certificates for subdomains
- [ ] Test HTTPS access
- [ ] Verify auto-renewal is working

### Optional Email
- [ ] Configure MX record
- [ ] Configure mail.lengkundee01.org A record
- [ ] Configure SPF TXT record
- [ ] Configure DMARC TXT record
- [ ] Test email sending

### Final Verification
- [ ] All domains resolve correctly
- [ ] All SSL certificates are valid
- [ ] HTTP redirects to HTTPS
- [ ] All services are accessible
- [ ] DNS propagation complete globally

---

## Related Documentation

- [Domain Configuration](DOMAIN_CONFIGURATION.md) - Complete domain details
- [VPS Configuration](VPS_CONFIGURATION.md) - VPS server information
- [Deployment Summary](A6-9V/Trading/GenX_FX/DEPLOYMENT_SUMMARY.md) - Application deployment

---

## Support Resources

### Namecheap Support
- **Knowledge Base**: https://www.namecheap.com/support/knowledgebase/subcategory/46/dns
- **Live Chat**: https://www.namecheap.com/support/live-chat/
- **Ticket System**: https://support.namecheap.com/

### DNS Tools
- **DNS Checker**: https://dnschecker.org
- **What's My DNS**: https://www.whatsmydns.net
- **MX Toolbox**: https://mxtoolbox.com/
- **SSL Labs**: https://www.ssllabs.com/ssltest/

---

**Guide Version**: 1.0  
**Created**: January 6, 2026  
**Domain**: lengkundee01.org  
**Order**: 191346179
