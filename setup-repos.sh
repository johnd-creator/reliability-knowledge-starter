#!/usr/bin/env bash
set -euo pipefail

# The workspace is one mono repository. Keep this helper idempotent for fresh
# checkouts and never create nested repositories inside subprojects.
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$repo_root"

if [ ! -d .git ]; then
  git init
fi
git branch -M main
echo "Mono repository ready at $repo_root"
