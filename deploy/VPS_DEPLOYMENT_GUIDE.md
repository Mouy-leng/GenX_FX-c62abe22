# GenX FX Trading Platform - VPS Deployment Guide

This guide provides step-by-step instructions for deploying the GenX FX Trading Platform on a dedicated Virtual Private Server (VPS).

## 🎯 Overview

This guide details how to set up a dedicated VPS for the GenX FX Trading Platform. A dedicated VPS offers lower latency, dedicated resources, 24/7 automated trading, and enhanced security. The setup process is automated by a comprehensive script that prepares the entire environment.

## 📋 Prerequisites

### 1. VPS Requirements
- **Provider**: DigitalOcean, Vultr, Linode, or any provider offering Ubuntu.
- **OS**: Ubuntu 20.04 or 22.04 LTS.
- **Specifications**:
  - 2 vCPUs minimum (4 recommended)
  - 4GB RAM minimum (8GB recommended)
  - 20GB SSD storage minimum
- **Network**: A stable, high-bandwidth connection.

### 2. GitHub Personal Access Token
- You need a [GitHub Personal Access Token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) with `repo` scope. This is required to securely clone the private repository onto your VPS.

### 3. Broker Account
- An active trading account (e.g., Exness) with your credentials (login, password, server).

## 🚀 Deployment Workflow

The deployment process is straightforward. You will connect to your new VPS, clone the repository, and then run the automated setup script.

### Step 1: Connect to Your VPS
First, provision a new VPS with your chosen provider that meets the requirements above. Once it's ready, connect to the server as the `root` user via SSH.

```bash
ssh root@YOUR_VPS_IP
```

### Step 2: Install Git
The new server needs `git` to clone the repository. Install it using the package manager.
```bash
apt-get update
apt-get install -y git
```

### Step 3: Clone the Repository
Clone the GenX FX repository directly onto your VPS. You will use your GitHub username and the Personal Access Token you created.

```bash
git clone https://github.com/Mouy-leng/GenX_FX.git
```

### Step 4: Run the Automated Setup Script
Navigate into the `deploy` directory and run the `setup-vps.sh` script with `sudo`. Provide your GitHub token as the first argument. This script will configure the entire server for you.

```bash
cd GenX_FX/deploy
chmod +x setup-vps.sh
sudo ./setup-vps.sh <YOUR_GITHUB_TOKEN>
```
The script will perform the following actions:
-   Verify root privileges and system requirements.
-   Update all system packages.
-   Install all necessary dependencies (Python, PostgreSQL, Redis, etc.).
-   Configure the firewall (UFW) with secure rules.
-   Create a dedicated application user (`genx`) and directories.
-   Clone the application source code into `/opt/genx-trading`.
-   Set up a Python virtual environment and install all production dependencies.
-   Create utility scripts for management (`health-check.sh`, `backup.sh`).
-   Create and enable `systemd` services for the application and monitor.
-   Set final ownership and permissions.

### Step 5: Final Configuration
After the setup script is complete, the final step is to add your secret credentials to the environment file.

1.  **Edit the `.env` file:**
    ```bash
    sudo nano /opt/genx-trading/.env
    ```
2.  **Add your credentials:**
    Fill in your broker account details, any API keys, and other required settings.
3.  **Save and exit.**

## 📊 VPS Management

All ongoing management tasks (starting, stopping, monitoring, etc.) are handled by the `manage-vps.sh` script. Always run it with `sudo`.

**The script is located at `/opt/genx-trading/deploy/manage-vps.sh`**.

### Management Commands

| Command                               | Description                                                 |
| ------------------------------------- | ----------------------------------------------------------- |
| `sudo ./manage-vps.sh start`          | Starts all application services.                            |
| `sudo ./manage-vps.sh stop`           | Stops all application services.                             |
| `sudo ./manage-vps.sh restart`        | Restarts all application services.                          |
| `sudo ./manage-vps.sh status`         | Checks the status of all services.                          |
| `sudo ./manage-vps.sh logs [service]` | Tails logs for a service (e.g., `genx-trading`).            |
| `sudo ./manage-vps.sh backup`         | Runs a manual backup.                                       |
| `sudo ./manage-vps.sh health-check`   | Performs a system health check.                             |
| `sudo ./manage-vps.sh help`           | Displays the help message.                                  |

### Example: Starting the Application
After the initial setup and configuration, start the application:
```bash
sudo /opt/genx-trading/deploy/manage-vps.sh start
```

### Example: Checking Logs
To monitor the main application logs:
```bash
sudo /opt/genx-trading/deploy/manage-vps.sh logs genx-trading
```

## 🔒 Security Best Practices
-   **SSH Keys**: For enhanced security, disable password authentication and use SSH keys to connect to your VPS.
-   **Firewall**: The setup script configures a basic firewall. You can customize the rules further by editing `/etc/ufw/before.rules`.
-   **Regular Updates**: Periodically run `sudo apt update && sudo apt upgrade -y` to keep your server's packages up to date.