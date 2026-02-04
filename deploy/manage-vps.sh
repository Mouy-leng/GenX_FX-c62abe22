#!/bin/bash

# GenX FX Trading Platform - VPS Management Script
# This script provides commands to manage the GenX FX application services.

set -euo pipefail

# --- Configuration ---
APP_USER="genx"
APP_DIR="/opt/genx-trading"
SERVICES=("genx-trading" "genx-monitor")

# --- Helper Functions ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "\n${BLUE}>>> $1${NC}"; }

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run with sudo privileges."
        exit 1
    fi
}

# --- Service Management Functions ---
start_services() {
    log_step "Starting services..."
    for service in "${SERVICES[@]}"; do
        systemctl start "$service"
        log_info "$service started."
    done
}

stop_services() {
    log_step "Stopping services..."
    for service in "${SERVICES[@]}"; do
        systemctl stop "$service"
        log_info "$service stopped."
    done
}

restart_services() {
    log_step "Restarting services..."
    for service in "${SERVICES[@]}"; do
        systemctl restart "$service"
        log_info "$service restarted."
    done
}

status_services() {
    log_step "Checking service status..."
    for service in "${SERVICES[@]}"; do
        systemctl status "$service" --no-pager
    done
}

view_logs() {
    log_step "Tailing logs for $1..."
    if [ -z "$1" ]; then
        log_error "Please specify a service to log (e.g., 'genx-trading')."
        exit 1
    fi
    journalctl -u "$1" -f -n 100
}

# --- Administration Functions ---
run_backup() {
    log_step "Running backup script..."
    if [ -f "$APP_DIR/scripts/backup.sh" ]; then
        su - "$APP_USER" -c "$APP_DIR/scripts/backup.sh"
        log_info "Backup completed."
    else
        log_error "Backup script not found at $APP_DIR/scripts/backup.sh"
    fi
}

run_health_check() {
    log_step "Running health check..."
    if [ -f "$APP_DIR/scripts/health-check.sh" ]; then
        su - "$APP_USER" -c "$APP_DIR/scripts/health-check.sh"
        log_info "Health check completed. See logs for details."
    else
        log_error "Health check script not found at $APP_DIR/scripts/health-check.sh"
    fi
}

# --- Usage Information ---
usage() {
    echo "GenX FX VPS Management Script"
    echo "Usage: sudo ./manage-vps.sh [command]"
    echo ""
    echo "Commands:"
    echo "  start          Start all application services."
    echo "  stop           Stop all application services."
    echo "  restart        Restart all application services."
    echo "  status         Check the status of all services."
    echo "  logs [service] View live logs for a specific service (e.g., genx-trading)."
    echo "  backup         Run a manual backup."
    echo "  health-check   Perform a system health check."
    echo "  help           Display this help message."
}

# --- Main Execution ---
main() {
    check_root

    if [ -z "$1" ]; then
        usage
        exit 1
    fi

    case "$1" in
        start) start_services ;;
        stop) stop_services ;;
        restart) restart_services ;;
        status) status_services ;;
        logs) view_logs "$2" ;;
        backup) run_backup ;;
        health-check) run_health_check ;;
        help|--help|-h) usage ;;
        *)
            log_error "Unknown command: $1"
            usage
            exit 1
            ;;
    esac
}

main "$@"