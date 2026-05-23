#!/usr/bin/env bash
set -euo pipefail

echo "# Recent Changelog"
echo

git log --pretty=format:"- %h | %ad | %s" --date=short -n 100