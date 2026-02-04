# GenX Remote Access System

This project contains the complete source code and configuration for a secure, modular remote access system. It integrates device identity, domain routing, user authentication via GitHub, and session management with Firebase to create a robust platform for remote operations and automation.

## 1. Project Overview

The system is designed around a microservices-style architecture, where different components handle specific tasks. The core idea is to secure a remote service (like LiteWriter) by placing a secure gateway in front of it. This gateway verifies both the user's identity (via GitHub) and the device's identity (via a unique fingerprint) before allowing access.

The main components are:
-   **NGINX Reverse Proxy**: The entry point that routes traffic from your domain (`remote.genxfx.org`) to the appropriate backend service.
-   **Secure Gateway**: A Python Flask application that enforces device authentication.
-   **Auth Service**: A Python Flask application that handles the GitHub OAuth2 flow.
-   **Firebase Integration**: Uses Firestore to store and validate user sessions, linking authenticated users to verified devices.
-   **Automation Scripts**: A conceptual script to automate tasks, such as creating GitHub issues from LiteWriter notes.
-   **VS Code Extension Concept**: A plan for a monitoring dashboard integrated into your editor.

## 2. Directory Structure

The project is organized into the following directories:

```
genx-remote-system/
│
├── auth_service/
│   ├── device_auth.py         # Logic for device fingerprinting
│   ├── github_oauth.py        # Flask app for GitHub OAuth flow
│   ├── secure_gateway.py      # Flask app for the secure proxy
│   └── requirements.txt       # Python dependencies for the auth services
│
├── firebase_integration/
│   ├── firebase_client.py     # Client for Firebase session management
│   ├── firebase_schema.json   # Defines the Firestore data structure
│   └── requirements.txt       # Python dependencies for Firebase
│
├── github_automation/
│   ├── litewriter_to_github.py # Conceptual script for automation
│   └── requirements.txt       # Dependencies for the automation script
│
├── nginx_proxy/
│   └── nginx.conf             # NGINX configuration for the reverse proxy
│
└── vscode_extension_concept/
    ├── package.json           # Manifest for the VS Code extension
    └── README.md              # Detailed concept documentation
```

## 3. Setup and Deployment Guide

### Step 1: Set Environment Variables

Security is paramount. All credentials, API keys, and secrets are loaded from environment variables. **Do not hardcode them.** Create a `.env` file (and add it to `.gitignore`) or export them in your shell.

**Required Variables:**
```bash
# For GitHub OAuth Service (auth_service/github_oauth.py)
export GITHUB_CLIENT_ID="0b2a311d5d0c1c62c1f6"
export GITHUB_CLIENT_SECRET="4e6aa3f4f9f9f3e99a411b5d0a71fc01f2e1c7d1"
export REDIRECT_URI="https://genxai.vercel.app/api/auth/callback/github" # Or your deployed callback URL

# For Firebase Integration (firebase_integration/firebase_client.py)
# You must download your service account key from the Firebase console
export FIREBASE_SERVICE_ACCOUNT_KEY="/path/to/your/genx-firebase-serviceAccountKey.json"

# For LiteWriter Automation (github_automation/litewriter_to_github.py)
export LITEWRITER_WEBDAV_URL="http://10.62.78.114:8000/webdav/"
export LITEWRITER_USER="genxdbxfx3@gmail.com"
export LITEWRITER_PASS="Leng12345@#$01"
# Create a GitHub Personal Access Token with 'repo' scope
export GITHUB_TOKEN="your_github_personal_access_token"
export GITHUB_REPO="your_github_username/your_repo_name"
```

### Step 2: Install Dependencies

Each service has its own `requirements.txt` file. Install the dependencies for each component.

```bash
# For the auth service and secure gateway
pip install -r auth_service/requirements.txt

# For the Firebase client
pip install -r firebase_integration/requirements.txt

# For the GitHub automation script
pip install -r github_automation/requirements.txt
```

### Step 3: Configure NGINX

The provided `nginx_proxy/nginx.conf` is ready to use. You will need to place it in your NGINX configuration directory (e.g., `/etc/nginx/sites-available/`) and create a symbolic link to it in `/etc/nginx/sites-enabled/`.

**Important**: The config is set up for HTTP. For production, you **must** configure SSL/TLS using a service like Let's Encrypt to enable HTTPS.

### Step 4: Run the Backend Services

The backend consists of two Flask applications that should be run using a production-grade WSGI server like Gunicorn.

1.  **Run the Secure Gateway**: This service listens for requests from NGINX and verifies device identity.
    ```bash
    cd auth_service/
    gunicorn --bind 127.0.0.1:5001 secure_gateway:app
    ```

2.  **Run the GitHub OAuth Service**: This service handles the authentication flow.
    ```bash
    cd auth_service/
    gunicorn --bind 127.0.0.1:5002 github_oauth:app
    ```
    *(Note: This service is for the auth flow itself. The secure gateway is the main entry point for proxied requests.)*

### Step 5: Run Automation Scripts

The `litewriter_to_github.py` script can be run manually or scheduled as a cron job.

```bash
python3 github_automation/litewriter_to_github.py
```
Remember to implement a proper WebDAV client for the `get_notes_from_webdav` function as noted in the script's comments.

## 4. How It All Works Together

1.  A user (or device) makes a request to `http://remote.genxfx.org`.
2.  NGINX receives the request and proxies it to the **Secure Gateway** on port `5001`.
3.  The Secure Gateway inspects the request headers for `X-Device-Fingerprint` and `X-Device-Build-Number`.
4.  It uses `device_auth.py` to verify that the fingerprint is valid for the authorized build number.
5.  If valid, the gateway forwards the request to the actual LiteWriter server (`http://10.62.78.114:8000`). If not, it returns a `403 Forbidden` error.
6.  User authentication is handled separately by the **GitHub OAuth Service**, which, upon successful login, creates a session in Firebase linking the user's GitHub ID to their verified device.

This architecture ensures that no request can reach your LiteWriter server without first passing a device identity check, providing a strong layer of security.