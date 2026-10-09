#!/usr/bin/env bash
# Run once, on your own computer, to connect the Cloudflare Pages address to the server.
#
#   bash deploy/setup-cloudflare.sh <user@host> <pages-project> <origin-url> [branch]
#
#   e.g.  bash deploy/setup-cloudflare.sh me@203.0.113.5 dsai3 https://origin.example.com
#
# What it does, in order:
#   1. signs wrangler (Cloudflare's command-line tool) in; a browser window asks you
#   2. stores the server's address and the shared secret on the Pages project. The secret
#      is piped straight from the server to Cloudflare and never shown.
#   3. uploads edge/_worker.js as the project's new production version
#
# Needs: Node.js (for npx) and ssh access to the server. Run it again after changing
# edge/_worker.js, or after changing ORIGIN_SECRET on the server.

set -euo pipefail

target="${1:?usage: setup-cloudflare.sh <user@host> <pages-project> <origin-url> [branch]}"
project="${2:?missing Pages project name}"
origin="${3:?missing origin URL, e.g. https://origin.example.com}"
branch="${4:-main}"
cd "$(dirname "$0")/.."

wrangler() { npx --yes wrangler@4 "$@"; }

echo "==> signing in to Cloudflare (a browser window opens)"
wrangler login

echo "==> storing ORIGIN_URL and ORIGIN_SECRET on the Pages project '$project'"
printf '%s' "$origin" | wrangler pages secret put ORIGIN_URL --project-name "$project"
ssh "$target" 'sed -n "s/^ORIGIN_SECRET=//p" ~/dsai-vault/.env' | tr -d '\r\n' |
	wrangler pages secret put ORIGIN_SECRET --project-name "$project"

echo "==> uploading the proxy"
wrangler pages deploy edge --project-name "$project" --branch "$branch" --commit-dirty=true

echo
echo "==> https://$project.pages.dev answers:"
sleep 5
curl -sS -o /dev/null -w '    HTTP %{http_code}\n' "https://$project.pages.dev/" || true
echo "200 means the site is online. If it still shows the old page, wait a minute; if it"
echo "says 'not connected', the branch '$branch' is not the project's production branch"
echo "(see: npx wrangler pages project list)."
