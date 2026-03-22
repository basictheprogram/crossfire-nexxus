#!/usr/bin/env bash
set -e

# Grab info
COMMIT=$(git rev-parse HEAD)
BRANCH=$(git rev-parse --abbrev-ref HEAD)
DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')

# Write to version.json in your Django app
cat >src/version.json <<EOF
{
  "commit": "$COMMIT",
  "branch": "$BRANCH",
  "build_date": "$DATE"
}
EOF

# Optionally git add the file so it’s included in the commit
git add src/version.json
