#!/bin/bash

# GenX_FX Git Workflow Automation Script
# This script automates the process of pulling, committing, pushing,
# and merging a feature branch into the main branch.

set -e

# --- Configuration ---
MAIN_BRANCH="${MAIN_BRANCH:-main}"
REMOTE_NAME="${REMOTE_NAME:-origin}"


# --- Colors for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Functions for formatted output ---
print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# --- Start of Workflow ---

# 1. Check for uncommitted changes
print_info "Step 1: Checking for uncommitted changes..."
if [ -z "$(git status --porcelain)" ]; then
    print_warning "No changes to commit. Exiting."
    exit 0
fi
print_success "Working directory has changes to be committed."
echo ""

# 2. Get the current feature branch name
print_info "Step 2: Getting current branch name..."
BRANCH_NAME=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH_NAME" == "$MAIN_BRANCH" ]; then
    print_error "You are on the main branch. This script should be run from a feature branch."
    exit 1
fi
print_success "Current branch is '$BRANCH_NAME'."
echo ""

# 3. Pull latest changes for the current branch
print_info "Step 3: Pulling latest changes for '$BRANCH_NAME'..."
git pull --recurse-submodules "$REMOTE_NAME" "$BRANCH_NAME"
print_success "Successfully pulled latest changes."
echo ""

# 4. Prompt for a commit message
print_info "Step 4: Preparing to commit changes..."
read -p "Enter your commit message: " COMMIT_MESSAGE
if [ -z "$COMMIT_MESSAGE" ]; then
    print_error "Commit message cannot be empty."
    exit 1
fi

# 5. Add and commit all changes
git add .
git commit -m "$COMMIT_MESSAGE"
print_success "Changes committed with message: \"$COMMIT_MESSAGE\""
echo ""

# 6. Push changes to the remote feature branch
print_info "Step 6: Pushing changes to remote branch '$BRANCH_NAME'..."
git push "$REMOTE_NAME" "$BRANCH_NAME"
print_success "Successfully pushed to $REMOTE_NAME/$BRANCH_NAME."
echo ""

# 7. Switch to the main branch
print_info "Step 7: Switching to the '$MAIN_BRANCH' branch..."
git checkout "$MAIN_BRANCH"
print_success "Switched to '$MAIN_BRANCH' branch."
echo ""

# 8. Pull latest changes for main
print_info "Step 8: Pulling latest changes for '$MAIN_BRANCH'..."
git pull --recurse-submodules "$REMOTE_NAME" "$MAIN_BRANCH"
print_success "Successfully pulled latest changes for '$MAIN_BRANCH'."
echo ""

# 9. Merge the feature branch into main
print_info "Step 9: Merging '$BRANCH_NAME' into '$MAIN_BRANCH'..."
git merge "$BRANCH_NAME"
print_success "Successfully merged '$BRANCH_NAME' into '$MAIN_BRANCH'."
echo ""

# 10. Push the updated main branch
print_info "Step 10: Pushing updated '$MAIN_BRANCH' branch..."
git push "$REMOTE_NAME" "$MAIN_BRANCH"
print_success "Successfully pushed '$MAIN_BRANCH' branch."
echo ""

# 11. Delete the local feature branch
print_info "Step 11: Deleting local feature branch '$BRANCH_NAME'..."
read -p "Are you sure you want to delete the local branch '$BRANCH_NAME'? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git branch -d "$BRANCH_NAME"
    print_success "Successfully deleted local branch '$BRANCH_NAME'."
else
    print_warning "Skipped deletion of local branch '$BRANCH_NAME'."
fi
echo ""

# 12. Delete the remote feature branch
print_info "Step 12: Deleting remote feature branch '$BRANCH_NAME'..."
read -p "Are you sure you want to delete the remote branch '$REMOTE_NAME/$BRANCH_NAME'? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push "$REMOTE_NAME" --delete "$BRANCH_NAME"
    print_success "Successfully deleted remote branch '$REMOTE_NAME/$BRANCH_NAME'."
else
    print_warning "Skipped deletion of remote branch '$REMOTE_NAME/$BRANCH_NAME'."
fi
echo ""

print_success "Git workflow completed successfully!"
