#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ./scripts/push_to_github.sh <github_repo_ssh_or_https_url>
#
# Example:
#   ./scripts/push_to_github.sh git@github.com:YOUR_ORG/ups-gcp-genai-agentic-starter.git

REMOTE_URL="${1:-}"
if [[ -z "${REMOTE_URL}" ]]; then
  echo "Missing remote URL"
  exit 1
fi

git init
git add .
git commit -m "Initial commit: UPS GCP GenAI + Agentic AI starter"
git branch -M main
git remote add origin "${REMOTE_URL}"
git push -u origin main
