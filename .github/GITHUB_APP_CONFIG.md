# GitHub App Configuration for NUNA Device

## Overview
This document outlines the GitHub App configuration for the NUNA device (💻) managed by @mouyleng (🧑‍💻) under the @A6-9V organization (🏙️).

## GitHub App Details

### App Information
| Field | Value |
|-------|-------|
| **App Name** | `A6-9V-NUNA-Trading-Bot` |
| **Owner** | `A6-9V` (Organization) |
| **Device** | NUNA Device 💻 |
| **Managed By** | @mouyleng 🧑‍💻 |

### URLs Configuration
| URL Type | URL |
|----------|-----|
| **Homepage URL** | `https://github.com/A6-9V` |
| **Callback URL** | `https://lengkundee01.org/auth/github/callback` |
| **Webhook URL** | `https://lengkundee01.org/webhooks/github` |
| **Setup URL** | `https://lengkundee01.org/setup/github-app` |

### Webhook Configuration
```yaml
webhook:
  url: https://lengkundee01.org/webhooks/github
  secret: ${GITHUB_WEBHOOK_SECRET}  # Store in secrets manager
  content_type: application/json
  ssl_verification: enabled
  events:
    - push
    - pull_request
    - issues
    - issue_comment
    - check_run
    - check_suite
    - deployment
    - deployment_status
    - workflow_run
    - workflow_job
```

### OAuth Settings
```yaml
oauth:
  client_id: ${GITHUB_CLIENT_ID}
  client_secret: ${GITHUB_CLIENT_SECRET}
  redirect_uri: https://lengkundee01.org/auth/github/callback
  scopes:
    - user:email
    - read:org
    - repo
```

### Repository Permissions
| Permission | Access Level | Purpose |
|------------|--------------|---------|
| **Contents** | Read & Write | Push trading updates, configurations |
| **Metadata** | Read | Access repository info |
| **Pull requests** | Read & Write | Manage automated PRs |
| **Issues** | Read & Write | Track trading signals/alerts |
| **Actions** | Read & Write | Trigger deployment workflows |
| **Checks** | Read & Write | Report trading system health |
| **Deployments** | Read & Write | Manage VPS deployments |
| **Secrets** | Read | Access trading credentials |
| **Webhooks** | Read & Write | Configure event hooks |

### Organization Permissions
| Permission | Access Level | Purpose |
|------------|--------------|---------|
| **Members** | Read | Team access management |
| **Administration** | Read | Org settings access |

## Required Secrets

Store these in GitHub Secrets and/or your secrets manager:

```yaml
# GitHub App Credentials
GITHUB_APP_ID: "your_app_id"
GITHUB_APP_INSTALLATION_ID: "your_installation_id"
GITHUB_APP_PRIVATE_KEY: |
  -----BEGIN RSA PRIVATE KEY-----
  ... (base64 encoded if needed)
  -----END RSA PRIVATE KEY-----
GITHUB_APP_WEBHOOK_SECRET: "your_webhook_secret"

# OAuth Credentials
GITHUB_CLIENT_ID: "your_client_id"
GITHUB_CLIENT_SECRET: "your_client_secret"

# Trading System Credentials
TRADING_API_KEY: "your_trading_api_key"
TRADING_SECRET_KEY: "your_trading_secret_key"
```

## Installation Steps

### 1. Create GitHub App
1. Go to GitHub → Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Fill in the details from this configuration
4. Set permissions as specified above
5. Generate and download the private key

### 2. Install to Organization
1. Click "Install App" on the app page
2. Select **A6-9V** organization
3. Choose "Only select repositories"
4. Select the GenX_FX trading repository

### 3. Configure Webhooks
1. Set up your webhook receiver endpoint
2. Configure SSL certificate
3. Add the webhook secret to your secrets manager

### 4. Test Installation
```bash
# Test GitHub App token generation
curl -X POST \
  -H "Authorization: Bearer ${JWT_TOKEN}" \
  -H "Accept: application/vnd.github+json" \
  "https://api.github.com/app/installations/${INSTALLATION_ID}/access_tokens"
```

## Webhook Events Reference

### Trading-Related Events
| Event | Trigger | Action |
|-------|---------|--------|
| `push` | Code update | Deploy new trading logic |
| `deployment` | Deployment started | Track VPS deployment |
| `deployment_status` | Deployment completed | Verify system health |
| `workflow_run` | CI/CD completed | Update trading system |
| `check_run` | Check completed | Alert on failures |

### Custom Webhook Payload Processing
```python
# webhook_handler.py
from flask import Flask, request
import hmac
import hashlib

app = Flask(__name__)

@app.route('/webhooks/github', methods=['POST'])
def handle_webhook():
    signature = request.headers.get('X-Hub-Signature-256')
    payload = request.get_data()
    
    # Verify signature
    expected_signature = 'sha256=' + hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        return 'Invalid signature', 403
    
    event = request.headers.get('X-GitHub-Event')
    data = request.json
    
    # Handle events
    if event == 'push':
        handle_code_update(data)
    elif event == 'deployment':
        handle_deployment(data)
    elif event == 'workflow_run':
        handle_workflow(data)
    
    return 'OK', 200
```

## Integration with Trading System

### Automatic Deployment Flow
1. Code push to main branch triggers webhook
2. CI/CD workflow runs tests
3. On success, deployment to VPS Singapore
4. Trading system health check
5. Notification to @mouyleng

### Alert Configuration
```yaml
alerts:
  channels:
    - type: github_issue
      repository: A6-9V/GenX_FX
      labels: [trading-alert, automated]
    - type: webhook
      url: https://your-notification-service.com/alert
  triggers:
    - event: trading_error
      severity: high
    - event: model_update
      severity: info
    - event: risk_limit_breach
      severity: critical
```

## Security Considerations

1. **Private Key Protection**: Store private key in secure secrets manager
2. **Webhook Verification**: Always verify webhook signatures
3. **Token Rotation**: Rotate app credentials regularly
4. **Audit Logging**: Enable audit logs for all app actions
5. **IP Allowlisting**: Restrict webhook endpoints to GitHub IPs

## Contact

- **Organization**: @A6-9V
- **Device Owner**: @mouyleng
- **Device**: NUNA 💻
