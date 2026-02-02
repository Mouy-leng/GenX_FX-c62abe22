# DNS Configuration Guide for Namecheap Domain

## 📋 Overview

This guide provides step-by-step instructions for configuring your Namecheap domain to point to your GenX_FX deployment server.

## 🎯 Prerequisites

- Namecheap account with domain purchased
- VPS or cloud server with a static IP address
- Access to Namecheap dashboard

## 📝 Step-by-Step Configuration

### Step 1: Get Your Server IP Address

First, determine your server's IP address:

```bash
# On your server, run:
curl ifconfig.me

# Or
hostname -I

# Or check your hosting provider's dashboard
```

### Step 2: Access Namecheap Dashboard

1. Log in to your Namecheap account at https://namecheap.com
2. Click on **Account** in the top navigation
3. Go to **Dashboard**
4. Find your domain and click **Manage**

### Step 3: Navigate to Advanced DNS

1. In the domain management page, click on the **Advanced DNS** tab
2. You'll see the DNS records management interface

### Step 4: Configure DNS Records

Remove any existing A records and CNAME records, then add the following:

#### Basic Configuration (Recommended)

| Type | Host | Value | TTL |
|------|------|-------|-----|
| A Record | @ | 203.147.134.218 | Automatic |
| A Record | www | 203.147.134.218 | Automatic |

**Example:**
```
Type: A Record
Host: @
Value: 192.168.1.100
TTL: Automatic

Type: A Record
Host: www
Value: 192.168.1.100
TTL: Automatic
```

#### Advanced Configuration (Optional)

Add these records if you want subdomains for API or other services:

| Type | Host | Value | TTL |
|------|------|-------|-----|
| CNAME Record | api | lengkundee01.org | Automatic |
| CNAME Record | app | lengkundee01.org | Automatic |
| CNAME Record | admin | lengkundee01.org | Automatic |

**Note:** Replace `lengkundee01.org` with your actual domain name.

### Step 5: Configure Email (Optional)

If you want to use email with your domain:

| Type | Host | Value | Priority | TTL |
|------|------|-------|----------|-----|
| MX Record | @ | mail.lengkundee01.org | 10 | Automatic |

### Step 6: Add TXT Records for Security (Recommended)

#### SPF Record (Email Security)
```
Type: TXT Record
Host: @
Value: v=spf1 include:_spf.google.com ~all
TTL: Automatic
```

#### DKIM Record (if using email)
Follow your email provider's instructions

#### DMARC Record (Email Authentication)
```
Type: TXT Record
Host: _dmarc
Value: v=DMARC1; p=quarantine; rua=mailto:admin@lengkundee01.org
TTL: Automatic
```

## 🔄 DNS Propagation

### Understanding DNS Propagation

After updating DNS records:
- **Minimum time:** 1-2 hours
- **Maximum time:** 48 hours
- **Average time:** 4-6 hours

### Check DNS Propagation Status

Use these tools to verify DNS propagation:

1. **WhatsMyDNS**: https://www.whatsmydns.net/
   - Enter your domain
   - Select A record
   - See propagation worldwide

2. **DNS Checker**: https://dnschecker.org/
   - Enter your domain
   - Check multiple locations

3. **Command Line Tools**:
   ```bash
   # Check A record
   nslookup lengkundee01.org
   
   # Check with specific DNS server (Google)
   nslookup lengkundee01.org 8.8.8.8
   
   # Detailed DNS query
   dig lengkundee01.org
   
   # Check all records
   dig lengkundee01.org ANY
   ```

## ✅ Verification Steps

### 1. Verify DNS Records

```bash
# From your local machine
dig lengkundee01.org

# Expected output should show your server IP
# lengkundee01.org.     300     IN      A       192.168.1.100
```

### 2. Test HTTP Connection

```bash
# Test basic connectivity
curl -I http://lengkundee01.org

# Should return HTTP response headers
```

### 3. Verify WWW Subdomain

```bash
# Test www subdomain
dig www.lengkundee01.org

# Should also point to your server IP
```

## 🐛 Troubleshooting

### Issue: DNS Not Resolving

**Solutions:**
1. Wait longer (DNS can take up to 48 hours)
2. Clear local DNS cache:
   ```bash
   # Windows
   ipconfig /flushdns
   
   # Mac
   sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
   
   # Linux
   sudo systemd-resolve --flush-caches
   ```
3. Check if records are configured correctly in Namecheap
4. Try accessing from a different network

### Issue: WWW Not Working

**Solution:**
Make sure you have both @ and www A records pointing to your IP

### Issue: Subdomain Not Resolving

**Solutions:**
1. Verify CNAME record is created correctly
2. Ensure TTL has expired and changes have propagated
3. Use CNAME record with your domain, not the IP address

### Issue: Changes Not Taking Effect

**Solutions:**
1. Lower TTL to 300 seconds (5 minutes) before making changes
2. Wait for the old TTL to expire
3. Make changes
4. Increase TTL back to default after verification

## 📊 DNS Record Cheat Sheet

### A Record
- **Purpose**: Point domain to IP address
- **Host**: @ (root domain) or subdomain name
- **Value**: Server IP address (IPv4)

### AAAA Record
- **Purpose**: Point domain to IPv6 address
- **Host**: @ or subdomain name
- **Value**: Server IPv6 address

### CNAME Record
- **Purpose**: Create alias for domain
- **Host**: Subdomain name (api, www, app)
- **Value**: Target domain name
- **Note**: Cannot be used with @ (root domain)

### MX Record
- **Purpose**: Configure email servers
- **Host**: @ or subdomain
- **Value**: Mail server address
- **Priority**: Lower number = higher priority

### TXT Record
- **Purpose**: Add text information (SPF, DKIM, verification)
- **Host**: @ or subdomain
- **Value**: Text string

## 🔐 Security Best Practices

1. **Enable Domain Lock** in Namecheap dashboard
2. **Enable Two-Factor Authentication** for Namecheap account
3. **Use strong passwords**
4. **Keep contact information updated**
5. **Enable WhoisGuard** (privacy protection)
6. **Set up DNS CAA records** to prevent unauthorized SSL certificates

### CAA Record Example
```
Type: CAA Record
Host: @
Value: 0 issue "letsencrypt.org"
TTL: Automatic
```

## 📝 Complete Configuration Example

For domain: **example.com**
Server IP: **192.168.1.100**

```
# Basic Records
A      @       192.168.1.100        Automatic
A      www     192.168.1.100        Automatic

# Subdomains
CNAME  api     example.com          Automatic
CNAME  app     example.com          Automatic

# Email (if using)
MX     @       mail.example.com     10         Automatic
TXT    @       v=spf1 include:_spf.google.com ~all   Automatic

# Security
CAA    @       0 issue "letsencrypt.org"      Automatic
```

## 🚀 After DNS Configuration

Once DNS is configured and propagated:

1. ✅ Run SSL setup script: `sudo ./setup-ssl.sh`
2. ✅ Update .env file with your domain
3. ✅ Deploy application: `sudo ./deploy.sh`
4. ✅ Configure Nginx with your domain
5. ✅ Test HTTPS: `https://lengkundee01.org`

## 📚 Additional Resources

- **Namecheap DNS Documentation**: https://www.namecheap.com/support/knowledgebase/article.aspx/319/2237/how-can-i-set-up-an-a-address-record-for-my-domain
- **DNS Basics**: https://www.cloudflare.com/learning/dns/what-is-dns/
- **TTL Explained**: https://www.cloudflare.com/learning/dns/glossary/ttl/
- **DNS Record Types**: https://www.cloudflare.com/learning/dns/dns-records/

## 🆘 Need Help?

If you encounter issues:
1. Check Namecheap support documentation
2. Contact Namecheap support
3. Verify server is accessible via IP first
4. Check firewall rules on server
5. Review server logs for errors

---

**Last Updated:** January 2026  
**Version:** 1.0.0

For more information, see [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md)
