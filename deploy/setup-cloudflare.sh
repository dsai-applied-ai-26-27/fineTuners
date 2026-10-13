#!/usr/bin/env bash
# Run once, on your own computer, to put the site online at its Cloudflare Pages address.
#
#   bash deploy/setup-cloudflare.sh <user@host> <pages-project> <origin-url> [branch]
#
#   e.g.  bash deploy/setup-cloudflare.sh me@203.0.113.5 dsai3 https://vault.203-0-113-5.sslip.io
#
# <origin-url> is a name that points at the server and that nobody needs to remember: it
# only connects Cloudflare to the server. What the script does, in order:
#
#   1. On the server: tells the Caddy that owns port 443 to answer for that name and pass
#      requests to the dsai-vault proxy. Caddy fetches a certificate for it by itself.
#   2. Signs wrangler (Cloudflare's command-line tool) in; a browser window asks you.
#   3. Stores the origin URL and the shared secret on the Pages project. The secret goes
#      from the server into a temporary file and on to Cloudflare; it is never displayed.
#   4. Uploads edge/_worker.js as the project's new production version, and checks the
#      public address.
#
# Needs: ssh access to the server, Node.js (for npx), curl. Safe to run again, for example
# after changing edge/_worker.js or after changing ORIGIN_SECRET on the server.

set -euo pipefail

usage="usage: setup-cloudflare.sh <user@host> <pages-project> <origin-url> [branch]"
target="${1:?$usage}"
project="${2:?$usage}"
origin="${3:?$usage}"
branch="${4:-main}"
[[ "$origin" == https://* ]] || { echo "the origin URL must start with https://" >&2; exit 1; }
origin="${origin%/}"
origin_host="${origin#https://}"
cd "$(dirname "$0")/.."

wrangler() { npx --yes wrangler@4 "$@"; }

echo "==> 1/4 server: answering for $origin_host"
ssh "$target" 'bash -s' -- "$origin_host" <<'REMOTE'
set -euo pipefail
name="$1"
container="$(docker ps --filter publish=443 --format '{{.Names}}' | head -n 1)"
[[ -n "$container" ]] || { echo "no container on this server publishes port 443" >&2; exit 1; }
caddyfile="$(docker inspect "$container" --format \
	'{{range .Mounts}}{{if eq .Destination "/etc/caddy/Caddyfile"}}{{.Source}}{{end}}{{end}}')"
[[ -f "$caddyfile" ]] || { echo "could not find the Caddyfile of container '$container'" >&2; exit 1; }

if grep -qF "$name" "$caddyfile"; then
	echo "    $caddyfile already mentions $name"
else
	backup="$caddyfile.bak-$(date +%Y%m%d%H%M%S)"
	cp "$caddyfile" "$backup"
	# Appending keeps the file's identity, which a single-file Docker mount depends on.
	cat >>"$caddyfile" <<EOF

# DSAI Vault. Requests arrive from the Cloudflare Pages proxy; the dsai-vault proxy
# container rejects anything that does not carry the shared secret.
$name {
	reverse_proxy dsai-vault:8080
}
EOF
	if ! docker exec "$container" caddy validate --config /etc/caddy/Caddyfile >/dev/null 2>&1; then
		cat "$backup" >"$caddyfile"
		echo "the new block did not validate; $caddyfile was put back as it was" >&2
		exit 1
	fi
	echo "    added a block to $caddyfile (previous version: $backup)"
fi
docker exec "$container" caddy reload --config /etc/caddy/Caddyfile >/dev/null 2>&1
echo "    reloaded '$container'"

# Remembered beside the site's own settings. That Caddyfile belongs to another project and
# may be replaced by it; deploy/restore-front.sh then puts the block back from this.
env_file="$HOME/dsai-vault/.env"
if [[ -f "$env_file" ]]; then
	kept="$(mktemp "$env_file.XXXXXX")" # created readable by its owner only
	grep -v '^ORIGIN_HOST=' "$env_file" >"$kept" || true
	printf 'ORIGIN_HOST=%s\n' "$name" >>"$kept"
	mv "$kept" "$env_file"
fi
REMOTE

echo "    waiting for the certificate"
for attempt in $(seq 1 30); do
	# Without the secret the server must answer 404; any answer at all means HTTPS works.
	code="$(curl -s -o /dev/null -m 10 -w '%{http_code}' "$origin/" || true)"
	[[ "$code" == 404 ]] && break
	sleep 4
done
if [[ "$code" != 404 ]]; then
	echo "$origin does not answer over HTTPS yet (got '$code', expected 404)." >&2
	echo "Look at the Caddy log on the server for the certificate error, then run this again." >&2
	exit 1
fi
echo "    $origin is up and refuses requests without the secret"

echo "==> 2/4 signing in to Cloudflare"
# `whoami` exits 0 either way, so go by what it says.
if wrangler whoami 2>&1 | grep -qi "not authenticated"; then
	echo "    a browser window opens: press Allow there within about a minute."
	echo "    If it times out, run 'npx wrangler@4 login' by itself, then this script again."
	wrangler login
else
	echo "    already signed in"
fi

echo "==> 3/4 storing ORIGIN_URL and ORIGIN_SECRET on the Pages project '$project'"
secrets="$(mktemp)"
trap 'rm -f "$secrets"' EXIT
chmod 600 "$secrets"
{
	printf 'ORIGIN_URL=%s\n' "$origin"
	ssh "$target" 'grep "^ORIGIN_SECRET=" ~/dsai-vault/.env'
} >"$secrets"
grep -q '^ORIGIN_SECRET=.\{32,\}' "$secrets" || { echo "could not read ORIGIN_SECRET from the server" >&2; exit 1; }
wrangler pages secret bulk "$secrets" --project-name "$project"
rm -f "$secrets"

echo "==> 4/4 uploading the proxy"
wrangler pages deploy edge --project-name "$project" --branch "$branch" --commit-dirty=true

echo
echo "==> https://$project.pages.dev"
for attempt in $(seq 1 15); do
	code="$(curl -s -o /dev/null -m 15 -w '%{http_code}' "https://$project.pages.dev/" || true)"
	title="$(curl -s -m 15 "https://$project.pages.dev/" | grep -o '<title>[^<]*' | head -n 1 || true)"
	[[ "$title" == *"DSAI Vault"* ]] && break
	sleep 4
done
echo "    HTTP $code ${title#<title>}"
if [[ "$title" == *"DSAI Vault"* ]]; then
	echo "The site is online."
else
	echo "Not the site yet. If the old page still shows, '$branch' is probably not this"
	echo "project's production branch: check with 'npx wrangler pages project list', then run"
	echo "this script again with the right branch as the fourth argument."
fi
