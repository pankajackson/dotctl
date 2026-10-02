#!/usr/bin/env bash
set -euo pipefail

echo "# Changelog"
echo

# Iterate tags in reverse chronological order
git tag --sort=-creatordate | while read -r tag; do
  date=$(git log -1 --format=%ad --date=short "$tag")

  echo "## $tag - $date"
  echo

  # commits in this tag range
  git log "${tag}^..${tag}" --pretty=format:"- %s" || true

  echo
  echo
done