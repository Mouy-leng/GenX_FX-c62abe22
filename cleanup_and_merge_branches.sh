#!/bin/bash

# 🌿 Branch Cleanup and Merge Script for GenX_FX Repository
# This script helps manage branch merging and cleanup operations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    print_error "Not in a git repository!"
    exit 1
fi

# Ensure we're on main branch
current_branch=$(git branch --show-current)
if [ "$current_branch" != "main" ]; then
    print_warning "Not on main branch. Switching to main..."
    git checkout main
    git pull origin main
fi

print_header "🚀 GenX_FX Branch Management Script"

# Function to merge security-related branches
merge_security_branches() {
    print_header "🔒 Merging Security-Related Branches"
    
    security_branches=(
        "origin/dependabot/github_actions/github/codeql-action-3"
        "origin/dependabot/pip/safety-gte-2.3.0-and-lt-4.0.0"
        "origin/dependabot/pip/fastapi-0.117.1"
        "origin/dependabot/pip/pydantic-2.11.9"
        "origin/dependabot/npm_and_yarn/typescript-eslint-8.44.1"
    )
    
    for branch in "${security_branches[@]}"; do
        if git show-ref --verify --quiet refs/remotes/$branch; then
            print_info "Merging $branch..."
            if git merge $branch --no-ff -m "Merge $branch - Security updates"; then
                print_success "Successfully merged $branch"
            else
                print_error "Failed to merge $branch"
            fi
        else
            print_warning "Branch $branch not found, skipping..."
        fi
    done
}

# Function to merge dependency updates
merge_dependency_updates() {
    print_header "📦 Merging Dependency Updates"
    
    dependency_branches=(
        "origin/dependabot/pip/click-8.1.8"
        "origin/dependabot/pip/matplotlib-3.9.4"
        "origin/dependabot/pip/psutil-7.1.0"
        "origin/dependabot/pip/statsmodels-0.14.5"
        "origin/dependabot/pip/ta-lib-0.6.7"
        "origin/dependabot/pip/uvicorn-0.37.0"
        "origin/dependabot/pip/yfinance-0.2.66"
        "origin/dependabot/npm_and_yarn/eslint/js-9.36.0"
        "origin/dependabot/npm_and_yarn/recharts-3.2.1"
        "origin/dependabot/npm_and_yarn/tailwindcss-4.1.13"
    )
    
    for branch in "${dependency_branches[@]}"; do
        if git show-ref --verify --quiet refs/remotes/$branch; then
            print_info "Merging $branch..."
            if git merge $branch --no-ff -m "Merge $branch - Dependency update"; then
                print_success "Successfully merged $branch"
            else
                print_error "Failed to merge $branch"
            fi
        else
            print_warning "Branch $branch not found, skipping..."
        fi
    done
}

# Function to clean up old branches
cleanup_old_branches() {
    print_header "🗑️ Cleaning Up Old Branches"
    
    # List of branches to delete (old cursor branches)
    old_branches=(
        "cursor/check-google-cloud-build-and-count-environments-1696"
        "cursor/check-workspace-domain-suitability-dced"
        "cursor/connect-to-amp-api-and-main-cli-13f1"
        "cursor/connect-to-amp-service-26f2"
        "cursor/debug-and-refactor-deployed-trading-system-4de4"
        "cursor/decide-next-project-steps-and-excel-requirements-150e"
        "cursor/deploy-to-multiple-environments-with-cursor-agent-1f4e"
        "cursor/deploy-to-railway-with-token-820a"
        "cursor/fix-google-cloud-deployment-build-error-3dea"
        "cursor/fix-persistent-failure-3c36"
        "cursor/gather-cli-integrate-contributions-and-execute-deploy-96ea"
        "cursor/isolate-deploy-job-with-container-and-branch-5284"
        "cursor/manage-and-update-historymaker-1-package-e0f1"
        "cursor/retrieve-user-authentication-token-1958"
    )
    
    print_warning "The following branches will be deleted:"
    for branch in "${old_branches[@]}"; do
        echo "  - $branch"
    done
    
    read -p "Do you want to proceed with deletion? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for branch in "${old_branches[@]}"; do
            if git show-ref --verify --quiet refs/heads/$branch; then
                print_info "Deleting local branch $branch..."
                git branch -D $branch
                print_success "Deleted local branch $branch"
            fi
            
            if git show-ref --verify --quiet refs/remotes/origin/$branch; then
                print_info "Deleting remote branch $branch..."
                git push origin --delete $branch
                print_success "Deleted remote branch $branch"
            fi
        done
    else
        print_info "Branch deletion cancelled."
    fi
}

# Function to set up branch protection
setup_branch_protection() {
    print_header "🔒 Setting Up Branch Protection"
    
    print_info "Setting up branch protection for main branch..."
    
    # Check if GitHub CLI is available
    if command -v gh &> /dev/null; then
        print_info "GitHub CLI found. Setting up branch protection..."
        
        # Get repository info
        repo_info=$(gh repo view --json owner,name)
        owner=$(echo $repo_info | jq -r '.owner.login')
        repo_name=$(echo $repo_info | jq -r '.name')
        
        # Set up branch protection rules
        gh api repos/$owner/$repo_name/branches/main/protection \
            --method PUT \
            --field required_status_checks='{"strict":true,"contexts":["ci/tests"]}' \
            --field enforce_admins=true \
            --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
            --field restrictions='{"users":[],"teams":[]}' \
            --field allow_force_pushes=false \
            --field allow_deletions=false
        
        print_success "Branch protection rules set up successfully!"
    else
        print_warning "GitHub CLI not found. Please set up branch protection manually:"
        echo "1. Go to repository settings"
        echo "2. Navigate to 'Branches' section"
        echo "3. Add rule for 'main' branch"
        echo "4. Enable required pull request reviews"
        echo "5. Enable required status checks"
        echo "6. Enable 'Restrict pushes that create files'"
    fi
}

# Function to show branch status
show_branch_status() {
    print_header "📊 Current Branch Status"
    
    echo "Current branch: $(git branch --show-current)"
    echo "Remote branches: $(git branch -r | wc -l)"
    echo "Local branches: $(git branch | wc -l)"
    echo ""
    
    print_info "Recent commits on main:"
    git log --oneline -5
    
    echo ""
    print_info "Branches with recent activity (last 7 days):"
    git for-each-ref --sort=-committerdate refs/remotes \
        --format='%(committerdate:short) %(refname:short)' \
        | head -10
}

# Function to run security checks
run_security_checks() {
    print_header "🔍 Running Security Checks"
    
    # Check for hardcoded secrets
    print_info "Scanning for hardcoded secrets..."
    if grep -r "your-super-secret-key-change-this-in-production" . --exclude-dir=.git --exclude="*.md" --exclude="*.sh" > /dev/null 2>&1; then
        print_error "Found hardcoded secrets in codebase!"
        grep -r "your-super-secret-key-change-this-in-production" . --exclude-dir=.git --exclude="*.md" --exclude="*.sh"
    else
        print_success "No hardcoded secrets found"
    fi
    
    # Check for JWT bypass vulnerabilities
    print_info "Checking for JWT bypass vulnerabilities..."
    if grep -r "TESTING.*credentials" . --exclude-dir=.git --exclude="*.md" > /dev/null 2>&1; then
        print_error "Potential JWT bypass vulnerability found!"
        grep -r "TESTING.*credentials" . --exclude-dir=.git --exclude="*.md"
    else
        print_success "No JWT bypass vulnerabilities found"
    fi
    
    # Check dependencies
    print_info "Checking for vulnerable dependencies..."
    if command -v pip-audit &> /dev/null; then
        pip-audit --desc --format=json > security_audit.json 2>/dev/null || true
        if [ -f security_audit.json ]; then
            vuln_count=$(jq '.vulnerabilities | length' security_audit.json 2>/dev/null || echo "0")
            if [ "$vuln_count" -gt 0 ]; then
                print_error "Found $vuln_count vulnerable dependencies!"
            else
                print_success "No vulnerable dependencies found"
            fi
        fi
    else
        print_warning "pip-audit not installed. Install with: pip install pip-audit"
    fi
}

# Main menu
show_menu() {
    echo ""
    print_header "🎯 Branch Management Menu"
    echo "1. Show branch status"
    echo "2. Merge security-related branches"
    echo "3. Merge dependency updates"
    echo "4. Clean up old branches"
    echo "5. Set up branch protection"
    echo "6. Run security checks"
    echo "7. Execute all operations"
    echo "8. Exit"
    echo ""
}

# Main execution
main() {
    while true; do
        show_menu
        read -p "Select an option (1-8): " choice
        
        case $choice in
            1)
                show_branch_status
                ;;
            2)
                merge_security_branches
                ;;
            3)
                merge_dependency_updates
                ;;
            4)
                cleanup_old_branches
                ;;
            5)
                setup_branch_protection
                ;;
            6)
                run_security_checks
                ;;
            7)
                print_header "🚀 Executing All Operations"
                show_branch_status
                merge_security_branches
                merge_dependency_updates
                run_security_checks
                setup_branch_protection
                print_success "All operations completed!"
                ;;
            8)
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 1-8."
                ;;
        esac
        
        echo ""
        read -p "Press Enter to continue..."
    done
}

# Check if script is run with arguments
if [ $# -eq 0 ]; then
    main
else
    case $1 in
        "security")
            merge_security_branches
            ;;
        "deps")
            merge_dependency_updates
            ;;
        "cleanup")
            cleanup_old_branches
            ;;
        "protect")
            setup_branch_protection
            ;;
        "status")
            show_branch_status
            ;;
        "audit")
            run_security_checks
            ;;
        "all")
            show_branch_status
            merge_security_branches
            merge_dependency_updates
            run_security_checks
            setup_branch_protection
            ;;
        *)
            echo "Usage: $0 [security|deps|cleanup|protect|status|audit|all]"
            echo "Or run without arguments for interactive menu"
            exit 1
            ;;
    esac
fi