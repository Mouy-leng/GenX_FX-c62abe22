# Domain Configuration - lengkundee01.org

## Domain Registration Details

**Registration Information:**
- **Domain**: lengkundee01.org
- **Registrar**: Namecheap
- **Order Date**: January 6, 2026 09:25:04 AM EST
- **Order Number**: 191346179
- **Transaction ID**: 233117631
- **Duration**: 1 year
- **Renewal Date**: January 6, 2027

**Account Information:**
- **Username**: LengNuna
- **Email**: lengkundee01@gmail.com
- **Order Reference**: lengnuna-203.147.134.218-313f02f318644a85aa03ebe038f5367f

**Domain Privacy:**
- **Status**: Enabled (Free)
- **Protection**: WHOIS information protected

---

## Cost Breakdown

| Item | Quantity | Duration | Price | Subtotal |
|------|----------|----------|-------|----------|
| Domain Registration | 1 | 1 year | $6.98 | $6.98 |
| ICANN Fee | 1 | - | $0.20 | $0.20 |
| Domain Privacy | 1 | 1 year | $0.00 | $0.00 |
| **Total** | | | | **$7.18** |

**Payment Method**: Credit Card ending in 5724

---

## DNS Configuration

### Recommended DNS Setup

#### A Records (IPv4)
```
@ (root)          A    203.147.134.218
www               A    203.147.134.218
```

#### CNAME Records
```
docs              CNAME    lengkundee01.org
api               CNAME    lengkundee01.org
trading           CNAME    lengkundee01.org
```

#### MX Records (Email)
```
@                 MX   10   mail.lengkundee01.org
```

#### TXT Records (Verification & Security)
```
@                 TXT  "v=spf1 include:_spf.google.com ~all"
_dmarc            TXT  "v=DMARC1; p=none; rua=mailto:lengkundee01@gmail.com"
```

### Namecheap DNS Management
1. Log into Namecheap account: https://www.namecheap.com
2. Navigate to Domain List → lengkundee01.org → Manage
3. Select "Advanced DNS" tab
4. Add/modify DNS records as listed above

---

## Intended Use

### Primary Purpose
- **Trading System Documentation**: Host GenX_FX trading system documentation
- **API Endpoint**: Provide accessible API endpoint for trading services
- **Dashboard**: Host trading performance dashboard
- **Status Page**: System status and uptime monitoring

### Subdomain Structure
- **lengkundee01.org**: Main landing page / documentation hub
- **docs.lengkundee01.org**: Comprehensive trading system documentation
- **api.lengkundee01.org**: REST API endpoints for trading operations
- **trading.lengkundee01.org**: Trading dashboard and analytics
- **status.lengkundee01.org**: System health and uptime status

---

## SSL Certificate

### Current Status
- **Type**: Free Domain Privacy included with registration
- **HTTPS**: Not yet configured

### Recommended SSL Setup
1. **Let's Encrypt (Free)**
   - Automated certificate renewal
   - Wildcard support for subdomains
   - 90-day validity with auto-renewal

2. **Installation Steps**:
   ```bash
   # Using certbot
   sudo apt-get update
   sudo apt-get install certbot python3-certbot-nginx
   
   # Obtain certificate
   sudo certbot --nginx -d lengkundee01.org -d www.lengkundee01.org
   
   # Auto-renewal (already configured by certbot)
   sudo certbot renew --dry-run
   ```

---

## Website Deployment Plan

### Phase 1: Basic Documentation Site
**Timeline**: Week 1
- [ ] Set up static site generator (Jekyll, Hugo, or MkDocs)
- [ ] Deploy GenX_FX documentation
- [ ] Configure DNS A records
- [ ] Install SSL certificate
- [ ] Test domain access

### Phase 2: Trading Dashboard
**Timeline**: Week 2-3
- [ ] Deploy Flask/Django application
- [ ] Set up trading.lengkundee01.org subdomain
- [ ] Integrate with existing trading system
- [ ] Configure authentication
- [ ] Test dashboard functionality

### Phase 3: API Endpoint
**Timeline**: Week 3-4
- [ ] Deploy REST API (from `local_server.py`)
- [ ] Configure api.lengkundee01.org subdomain
- [ ] Implement API authentication
- [ ] Set up rate limiting
- [ ] Test API endpoints

### Phase 4: Status Monitoring
**Timeline**: Week 4
- [ ] Set up uptime monitoring (UptimeRobot, Pingdom)
- [ ] Configure status.lengkundee01.org
- [ ] Integrate system health checks
- [ ] Set up alerting (email, SMS)

---

## Server Requirements

### Recommended VPS Specifications
- **OS**: Ubuntu 22.04 LTS or later
- **RAM**: 2GB minimum (4GB recommended)
- **Storage**: 20GB SSD minimum
- **CPU**: 2 cores minimum
- **Bandwidth**: 2TB/month minimum

### Required Software Stack
```bash
# Web Server
nginx 1.18+ or Apache 2.4+

# Application Runtime
python 3.9+
Node.js 16+ (if using frontend framework)

# Database (if needed)
PostgreSQL 14+ or MySQL 8.0+

# Process Manager
pm2 (for Node.js) or systemd services

# SSL
certbot (Let's Encrypt)
```

---

## Security Considerations

### Domain Security
- [x] Domain privacy enabled (WHOIS protection)
- [ ] Two-factor authentication (2FA) on Namecheap account
- [ ] Strong password for domain registrar account
- [ ] Regular security audit of DNS records

### Website Security
- [ ] SSL/TLS certificate installed and configured
- [ ] HTTP to HTTPS redirect
- [ ] Security headers (HSTS, CSP, X-Frame-Options)
- [ ] DDoS protection (Cloudflare free plan)
- [ ] Regular security updates
- [ ] Firewall configured (UFW or iptables)
- [ ] Fail2ban for brute force protection

### API Security
- [ ] API key authentication
- [ ] Rate limiting implemented
- [ ] CORS properly configured
- [ ] Input validation and sanitization
- [ ] SQL injection prevention
- [ ] XSS protection

---

## Maintenance Schedule

### Daily
- Monitor website uptime
- Check SSL certificate validity
- Review access logs for suspicious activity

### Weekly
- Review DNS records
- Check domain registration status
- Update website content
- Review API usage metrics

### Monthly
- Security audit
- Update server packages
- Review and optimize performance
- Backup website and database

### Annually (Before Expiration)
- **Renewal Date**: January 6, 2027
- Renew domain registration
- Review and update documentation
- Audit all subdomains and services

---

## Integration with GenX_FX System

### Current System Components
- **VPS Subscription**: ID 6759730 (Auto-renewal enabled)
- **Trading Platform**: MetaTrader 5 (Exness-MT5Trail8)
- **Trading Account**: 279260115 (Demo)
- **Email**: lengkundee01@gmail.com
- **Docker Hub**: lengkundee01@gmail.com

### Domain Integration Points
1. **Documentation Hosting**: Deploy system guides to docs.lengkundee01.org
2. **API Deployment**: Host trading API on api.lengkundee01.org
3. **Dashboard Access**: Trading dashboard on trading.lengkundee01.org
4. **Status Monitoring**: System health on status.lengkundee01.org

---

## Quick Links

### Namecheap Account
- **Dashboard**: https://www.namecheap.com/myaccount/
- **Domain Management**: https://ap.www.namecheap.com/domains/domaincontrolpanel/lengkundee01.org/domain
- **DNS Management**: https://ap.www.namecheap.com/domains/domaincontrolpanel/lengkundee01.org/advancedns

### Related Documentation
- [VPS Configuration](VPS_CONFIGURATION.md)
- [Deployment Summary](A6-9V/Trading/GenX_FX/DEPLOYMENT_SUMMARY.md)
- [Documentation Index](DOCUMENTATION_INDEX.md)
- [Repository Launch Guide](REPOSITORY_LAUNCH_GUIDE.md)

### Domain Tools
- **DNS Lookup**: https://www.nslookup.io/domains/lengkundee01.org/dns-records/
- **SSL Check**: https://www.ssllabs.com/ssltest/analyze.html?d=lengkundee01.org
- **WHOIS**: https://www.namecheap.com/domains/whois/result?domain=lengkundee01.org

---

## Troubleshooting

### Common Issues

#### DNS Not Resolving
1. Check DNS propagation: https://dnschecker.org
2. Verify DNS records in Namecheap dashboard
3. Wait 24-48 hours for full propagation
4. Clear local DNS cache: `ipconfig /flushdns` (Windows) or `sudo systemd-resolve --flush-caches` (Linux)

#### SSL Certificate Issues
1. Verify domain ownership
2. Check firewall rules (ports 80, 443)
3. Renew certificate: `sudo certbot renew`
4. Check certificate expiry: `sudo certbot certificates`

#### Website Not Accessible
1. Verify web server is running: `sudo systemctl status nginx`
2. Check server logs: `sudo tail -f /var/log/nginx/error.log`
3. Test local access: `curl localhost`
4. Verify DNS resolution: `nslookup lengkundee01.org`

---

## Contact Information

**Domain Owner**: LengNuna  
**Technical Contact**: lengkundee01@gmail.com  
**Order Support**: Namecheap 24/7 Support

**Support Resources**:
- Namecheap Knowledge Base: https://www.namecheap.com/support/knowledgebase/
- Namecheap Live Chat: https://www.namecheap.com/support/live-chat/general/
- Namecheap Ticket System: https://support.namecheap.com/index.php?/Tickets/Submit

---

**Document Version**: 1.0  
**Last Updated**: January 6, 2026  
**Next Review**: February 6, 2026
