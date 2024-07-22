#!/bin/bash
set -eo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_color() {
    printf "${!1}%s${NC}\n" "$2"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required tools
for cmd in git poetry sed; do
    if ! command_exists "$cmd"; then
        print_color "RED" "Error: $cmd is not installed. Please install it and try again."
        exit 1
    fi
done

# Ensure we're on the main branch
if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
    print_color "RED" "Error: You must be on the main branch to release."
    exit 1
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_color "RED" "Error: You have uncommitted changes. Please commit or stash them before releasing."
    exit 1
fi

# Get the current version from pyproject.toml
current_version=$(poetry version -s)

# Ask for the new version
read -p "Current version is $current_version. What should the new version be? " new_version

# Validate new version format (simple check)
if ! [[ $new_version =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_color "RED" "Error: Invalid version format. Please use semantic versioning (e.g., 1.2.3)."
    exit 1
fi

# Update the version in pyproject.toml
poetry version $new_version

# Update documentation version
if [ -f docs/index.md ]; then
    sed -i "s/version: $current_version/version: $new_version/" docs/index.md
else
    print_color "YELLOW" "Warning: docs/index.md not found. Skipping documentation version update."
fi

# Show changes and ask for confirmation
print_color "YELLOW" "The following files will be modified:"
git status --porcelain

read -p "Do you want to proceed with these changes? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_color "RED" "Release cancelled."
    exit 1
fi

# Commit the changes
git add pyproject.toml docs/index.md
git commit -m ":bookmark: Release: $new_version"

# Create and push the new tag
git tag -a v$new_version -m "Release: $new_version"
git push origin main --tags

print_color "GREEN" "Release $new_version has been created and pushed."
