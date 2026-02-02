# GitHub Secrets Configuration Guide

## 📋 Overview

This guide explains how to configure GitHub Secrets for automated deployment of GenX_FX to your domain.

## 🔐 Required Secrets

To enable automated deployment via GitHub Actions, you need to configure the following secrets in your GitHub repository.

### How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret listed below

## 📝 Secret Definitions

### 1. Server Access Secrets

#### `SSH_PRIVATE_KEY`
**Description:** Private SSH key for accessing your server  
**How to get:**
```bash
# On your local machine, generate SSH key pair
ssh-keygen -t ed25519 -C "github-actions@genx-fx"

# Display private key (copy this to GitHub Secret)
cat ~/.ssh/id_ed25519

# Copy public key to server
ssh-copy-id user@your-server-ip
```
**Value:** Paste the entire private key including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`

#### `SERVER_HOST`
**Description:** Your server's IP address or hostname  
**Value:** `192.168.1.100` or `server.example.com`

#### `SERVER_USER`
**Description:** SSH username for your server  
**Value:** `root` or `ubuntu` or your server username

### 2. Domain Configuration Secrets

#### `DOMAIN`
**Description:** Your primary domain name  
**Value:** `your-domain.com` (without https:// or www)

### 3. Application Secrets

#### `JWT_SECRET`
**Description:** Secret key for JWT token generation  
**How to generate:**
```bash
# Generate a strong 64-character random string
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"
```
**Value:** The generated random string (e.g., `a1b2c3d4e5f6...`)

### 4. Docker Registry Secrets (Optional)

#### `DOCKER_USERNAME`
**Description:** Docker Hub username  
**Value:** Your Docker Hub username

#### `DOCKER_PASSWORD`
**Description:** Docker Hub password or access token  
**Value:** Your Docker Hub password or personal access token

**How to get Docker Hub access token:**
1. Log in to Docker Hub
2. Go to Account Settings → Security
3. Click "New Access Token"
4. Copy the token

### 5. Notification Secrets (Optional)

#### `SLACK_WEBHOOK_URL`
**Description:** Slack webhook URL for deployment notifications  
**How to get:**
1. Go to https://api.slack.com/apps
2. Create a new app
3. Enable "Incoming Webhooks"
4. Create a webhook URL
5. Copy the webhook URL

**Value:** `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`

## 📊 Complete Secrets List

| Secret Name | Required | Description |
|-------------|----------|-------------|
| `SSH_PRIVATE_KEY` | ✅ Yes | SSH private key for server access |
| `SERVER_HOST` | ✅ Yes | Server IP address or hostname |
| `SERVER_USER` | ✅ Yes | SSH username |
| `DOMAIN` | ✅ Yes | Your domain name |
| `JWT_SECRET` | ✅ Yes | JWT secret for authentication |
| `DOCKER_USERNAME` | ⚠️ Optional | Docker Hub username |
| `DOCKER_PASSWORD` | ⚠️ Optional | Docker Hub password/token |
| `SLACK_WEBHOOK_URL` | ⚠️ Optional | Slack webhook for notifications |

## 🔧 Setup Instructions

### Step 1: Generate SSH Key for GitHub Actions

On your local machine:

```bash
# Generate new SSH key pair
ssh-keygen -t ed25519 -f ~/.ssh/github-actions-genx-fx -C "github-actions"

# Display private key (for GitHub Secret)
cat ~/.ssh/github-actions-genx-fx

# Display public key (for server)
cat ~/.ssh/github-actions-genx-fx.pub
```

### Step 2: Add Public Key to Server

```bash
# SSH to your server
ssh user@your-server-ip

# Add public key to authorized_keys
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys

# Set correct permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### Step 3: Test SSH Connection

From your local machine:

```bash
# Test SSH with the new key
ssh -i ~/.ssh/github-actions-genx-fx user@your-server-ip

# Should connect without password
```

### Step 4: Add Secrets to GitHub

1. Go to https://github.com/Mouy-leng/GenX_FX-c62abe22/settings/secrets/actions
2. Click **New repository secret** for each secret:

```
Name: SSH_PRIVATE_KEY
Value: [Paste contents of ~/.ssh/github-actions-genx-fx]

Name: SERVER_HOST
Value: your-server-ip

Name: SERVER_USER
Value: your-username

Name: DOMAIN
Value: your-domain.com

Name: JWT_SECRET
Value: [Generated random string]
```

### Step 5: Verify Configuration

1. Go to **Actions** tab in your repository
2. Manually trigger the "Deploy to Production Domain" workflow
3. Monitor the workflow execution
4. Check for any errors

## 🧪 Testing Secrets

Create a test workflow to verify secrets are configured correctly:

```yaml
name: Test Secrets
on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test SSH Connection
        run: |
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > key.pem
          chmod 600 key.pem
          ssh -i key.pem -o StrictHostKeyChecking=no \
            ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }} \
            "echo 'SSH connection successful'"
      
      - name: Test Domain
        run: |
          echo "Domain: ${{ secrets.DOMAIN }}"
          curl -I https://${{ secrets.DOMAIN }} || echo "Domain not yet accessible"
```

## 🔒 Security Best Practices

### SSH Key Security
- ✅ Use separate SSH keys for GitHub Actions
- ✅ Use ed25519 keys (more secure than RSA)
- ✅ Never share private keys
- ✅ Rotate keys periodically (every 6-12 months)
- ✅ Use key passphrases when possible

### JWT Secret Security
- ✅ Use at least 64 characters
- ✅ Use cryptographically random generation
- ✅ Never reuse secrets across environments
- ✅ Rotate secrets periodically
- ✅ Never commit secrets to code

### Docker Credentials
- ✅ Use access tokens instead of passwords
- ✅ Limit token permissions to push/pull only
- ✅ Set token expiration dates
- ✅ Rotate tokens periodically

## 🔄 Rotating Secrets

### When to Rotate
- Every 6-12 months (routine)
- When a team member leaves
- When credentials may be compromised
- When changing servers or domains

### How to Rotate

#### SSH Keys
1. Generate new key pair
2. Add new public key to server
3. Update `SSH_PRIVATE_KEY` secret in GitHub
4. Test deployment
5. Remove old public key from server

#### JWT Secret
1. Generate new secret
2. Update `JWT_SECRET` in GitHub
3. Deploy application
4. Users will need to re-authenticate

#### Docker Credentials
1. Create new access token
2. Update `DOCKER_PASSWORD` in GitHub
3. Revoke old token

## 📋 Troubleshooting

### SSH Connection Fails

**Error:** `Permission denied (publickey)`

**Solutions:**
1. Verify private key format (should start with `-----BEGIN OPENSSH PRIVATE KEY-----`)
2. Check public key is in server's `~/.ssh/authorized_keys`
3. Verify server user is correct
4. Check SSH service is running on server: `sudo systemctl status ssh`

### Domain Not Accessible

**Error:** `Could not resolve host`

**Solutions:**
1. Verify DNS records are configured
2. Wait for DNS propagation (up to 48 hours)
3. Test with `nslookup your-domain.com`
4. Ensure DOMAIN secret doesn't include `https://` or `www`

### Deployment Fails

**Error:** Various deployment errors

**Solutions:**
1. Check all secrets are set correctly
2. Verify server has Docker and Docker Compose installed
3. Ensure `/var/www/genx-fx` directory exists with correct permissions
4. Check server has enough disk space
5. Review GitHub Actions logs for specific errors

## 📚 Additional Resources

- **GitHub Secrets Documentation:** https://docs.github.com/en/actions/security-guides/encrypted-secrets
- **SSH Key Generation:** https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key
- **Docker Access Tokens:** https://docs.docker.com/docker-hub/access-tokens/
- **Slack Webhooks:** https://api.slack.com/messaging/webhooks

## ✅ Final Checklist

Before enabling automated deployment:

- [ ] All required secrets configured in GitHub
- [ ] SSH key pair generated and configured
- [ ] Public key added to server
- [ ] SSH connection tested successfully
- [ ] JWT secret generated (64+ characters)
- [ ] Domain DNS configured and propagated
- [ ] Server prepared with required software
- [ ] Test deployment executed successfully
- [ ] Rollback plan documented
- [ ] Team notified of automated deployment setup

---

**Last Updated:** January 2026  
**Version:** 1.0.0

For deployment guide, see [DOMAIN_DEPLOYMENT_GUIDE.md](DOMAIN_DEPLOYMENT_GUIDE.md)
