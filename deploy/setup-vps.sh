#!/bin/bash

# GenX FX Trading Platform - Comprehensive VPS Setup Script
# This script is idempotent and automates the full setup of the server environment.

set -euo pipefail

# --- Configuration ---
APP_USER="genx"
APP_DIR="/opt/genx-trading"
REPO_URL="https://github.com/Mouy-leng/GenX_FX.git"
MIN_RAM_GB=4
MIN_DISK_GB=20

# --- Helper Functions ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${BLUE}>>> $1${NC}"; }

handle_error() {
    log_error "Script failed on line $1 with exit code $2"
    exit 1
}

trap 'handle_error $LINENO $?' ERR

# --- Pre-flight Checks ---
check_root() {
    log_step "Verifying root privileges..."
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root. Aborting."
        exit 1
    fi
    log_info "Root privileges verified."
}

check_github_token() {
    log_step "Checking for GitHub token..."
    if [ -z "$1" ]; then
        log_error "GitHub token is required. Please provide it as the first argument."
        log_error "Usage: sudo ./setup-vps.sh <YOUR_GITHUB_TOKEN>"
        exit 1
    fi
    GITHUB_TOKEN=$1
    log_info "GitHub token received."
}

check_system() {
    log_step "Checking system requirements..."
    source /etc/os-release
    if [[ "$ID" != "ubuntu" ]] || [[ ! "$VERSION_ID" =~ ^(20\.04|22\.04)$ ]]; then
        log_warn "This script is optimized for Ubuntu 20.04/22.04. Your version: $PRETTY_NAME"
    fi

    local mem_gb=$(free -g | awk '/^Mem:/{print $2}')
    if [[ $mem_gb -lt $MIN_RAM_GB ]]; then
        log_error "A minimum of ${MIN_RAM_GB}GB RAM is required. Found: ${mem_gb}GB. Aborting."
        exit 1
    fi

    local disk_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $disk_gb -lt $MIN_DISK_GB ]]; then
        log_error "A minimum of ${MIN_DISK_GB}GB free disk space is required. Found: ${disk_gb}GB. Aborting."
        exit 1
    fi
    log_info "System requirements met."
}

# --- Installation and Setup ---
update_system() {
    log_step "Updating system packages..."
    apt-get update && apt-get upgrade -y
    log_info "System packages updated."
}

install_dependencies() {
    log_step "Installing core dependencies..."
    apt-get install -y git curl wget nano htop ufw fail2ban build-essential libssl-dev \
        python3 python3-pip python3-venv postgresql postgresql-contrib redis-server
    log_info "Core dependencies installed."
}

setup_firewall() {
    log_step "Configuring firewall (UFW)..."
    ufw allow ssh
    ufw allow http
    ufw allow https
    ufw allow 8000/tcp # API
    ufw allow 9090/tcp # EA Socket
    ufw --force enable
    log_info "Firewall configured and enabled."
}

setup_user_and_dirs() {
    log_step "Setting up application user '$APP_USER' and directories..."
    if id "$APP_USER" &>/dev/null; then
        log_warn "User '$APP_USER' already exists. Skipping creation."
    else
        useradd -m -s /bin/bash "$APP_USER"
        usermod -aG sudo "$APP_USER"
        log_info "User '$APP_USER' created."
    fi

    mkdir -p "$APP_DIR"/{logs,models,backups,credentials,signal_output,data,scripts}
    log_info "Application directories created."
}

clone_repo() {
    log_step "Cloning application repository..."
    if [ -d "$APP_DIR/.git" ]; then
        log_warn "Repository already exists in $APP_DIR. Pulling latest changes..."
        su - "$APP_USER" -c "cd $APP_DIR && git config --global --add safe.directory $APP_DIR && git pull"
    else
        log_info "Cloning new repository..."
        git clone "https://${GITHUB_TOKEN}:x-oauth-basic@${REPO_URL#https://}" "$APP_DIR"
    fi
    log_info "Repository is up to date."
}

setup_python_env() {
    log_step "Setting up Python virtual environment..."
    su - "$APP_USER" -c "cd $APP_DIR && python3 -m venv venv"
    su - "$APP_USER" -c "cd $APP_DIR && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements-prod.txt"
    log_info "Python environment created and production dependencies installed."
}

setup_env_file() {
    log_step "Configuring environment file..."
    local env_file="$APP_DIR/.env"
    if [ -f "$env_file" ]; then
        log_warn ".env file already exists. Skipping creation."
    else
        su - "$APP_USER" -c "cp '$APP_DIR/.env.example' '$env_file'"
        log_info ".env file created from .env.example."
    fi
}

create_utility_scripts() {
    log_step "Creating utility scripts..."

    # Health Check Script
    cat > "$APP_DIR/scripts/health-check.sh" << 'EOF'
#!/bin/bash
echo "Performing health check..."
# Add actual health check logic here, e.g., curl to a health endpoint
curl http://localhost:8000/health
EOF

    # Backup Script
    cat > "$APP_DIR/scripts/backup.sh" << 'EOF'
#!/bin/bash
echo "Performing backup..."
# Add actual backup logic here, e.g., pg_dump and tar
BACKUP_FILE="/opt/genx-trading/backups/backup-$(date +%F).tar.gz"
tar -czf "$BACKUP_FILE" -C /opt/genx-trading .
echo "Backup created at $BACKUP_FILE"
EOF

    chmod +x "$APP_DIR/scripts"/*.sh
    log_info "Utility scripts created."
}

create_systemd_services() {
    log_step "Creating systemd services..."

    # Main application service
    cat > /etc/systemd/system/genx-trading.service <<EOF
[Unit]
Description=GenX FX Trading Platform
After=network.target postgresql.service redis-server.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python main.py live
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Monitoring service
    cat > /etc/systemd/system/genx-monitor.service <<EOF
[Unit]
Description=GenX FX Monitoring Service
After=genx-trading.service

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/python scripts/monitor.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable genx-trading.service
    systemctl enable genx-monitor.service
    log_info "Systemd services created and enabled."
}

setup_permissions() {
    log_step "Finalizing directory permissions..."
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    chmod 700 "$APP_DIR/.env"
    log_info "Permissions finalized."
}

# --- Main Execution ---
main() {
    log_info "Starting GenX FX VPS Setup..."

    check_root "$@"
    check_github_token "$@"
    check_system

    update_system
    install_dependencies
    setup_firewall
    setup_user_and_dirs

    clone_repo
    setup_python_env
    setup_env_file
    create_utility_scripts
    create_systemd_services
    setup_permissions

    echo -e "\n${GREEN}========================================${NC}"
    echo -e "${GREEN}  VPS Setup and Deployment Complete!  ${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo -e "\n${YELLOW}Next Steps:${NC}"
    echo "1. ${RED}CRITICAL:${NC} Edit the environment file with your credentials:"
    echo "   sudo nano $APP_DIR/.env"
    echo "2. Start the services using the management script:"
    echo "   sudo /opt/genx-trading/deploy/manage-vps.sh start"
    echo "3. Check the status of the services:"
    echo "   sudo /opt/genx-trading/deploy/manage-vps.sh status"
}

main "$@"