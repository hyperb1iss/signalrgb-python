#!/bin/bash
set -e

# Ensure we're on the main branch
if [ "$(git rev-parse --abbrev-ref HEAD)" != "main" ]; then
    echo "You must be on the main branch to release."
    exit 1
fi

# Get the current version from pyproject.toml
current_version=$(poetry version -s)

# Ask for the new version
read -p "Current version is $current_version. What should the new version be? " new_version

# Update the version in pyproject.toml
poetry version $new_version

# Update documentation version
sed -i "s/version: $current_version/version: $new_version/" docs/index.md

# Commit the changes
git add pyproject.toml docs/index.md
git commit -m ":bookmark: Release: $new_version"

# Create and push the new tag
git tag -a v$new_version -m "Release: $new_version"
git push origin main --tags

echo "Release $new_version has been created and pushed. CI will handle the rest, including documentation deployment."
