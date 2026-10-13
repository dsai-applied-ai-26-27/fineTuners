#!/usr/bin/env bash
# Put the site's block back into the server's main Caddy, when it has gone missing.
#
#   ssh <server> 'bash -s' < deploy/restore-front.sh
#
# The symptom is the public address answering 525 for everyone: "SSL handshake failed".
# Cloudflare reaches the server under the origin name, and the Caddy that owns port 443
# answers for that name only because its Caddyfile has a block for it. That file belongs
# to another project on the server. When that project is deployed again its own copy of
# the file replaces it, the block is gone, Caddy has no certificate to show for the name,
# and the handshake fails. Nothing in this project is broken when that happens.
#
# What this does, the same careful way deploy/setup-cloudflare.sh added the block the
# first time:
#
#   - finds the origin name: in ~/dsai-vault/.env (ORIGIN_HOST) or, failing that, in the
#     newest copy of the Caddyfile that still has the block (the copies named
#     Caddyfile.bak-… that lie beside it);
#   - APPENDS the block to the file as it is now. The file is never replaced, so every
#     other site in it stays exactly as it is;
#   - keeps a copy of the file first, and applies the change only if Caddy accepts it;
#   - reloads Caddy, which keeps running connections. If the reload were refused, Caddy
#     would go on with the configuration it has;
#   - asks another site of that Caddy the same thing before and after, to show it was
#     not disturbed.
#
# It prints no host name and no address, and can be run again: with the block in place it
# changes nothing.

set -euo pipefail

BLOCK="reverse_proxy dsai-vault:8080"
env_file="$HOME/dsai-vault/.env"

container="$(docker ps --filter publish=443 --format '{{.Names}}' | head -n 1)"
[ -n "$container" ] || { echo "no container on this server publishes port 443" >&2; exit 1; }
caddyfile="$(docker inspect "$container" --format \
	'{{range .Mounts}}{{if eq .Destination "/etc/caddy/Caddyfile"}}{{.Source}}{{end}}{{end}}')"
[ -f "$caddyfile" ] || { echo "could not find the Caddyfile of container '$container'" >&2; exit 1; }
dir="$(dirname "$caddyfile")"

# The name of the site whose block passes requests to `$2`, in the Caddyfile `$1`.
site_of() {
	awk -v up="$2" '/^[^ \t#}{][^{]*\{[ \t]*$/ {site=$1} index($0, up) {print site; exit}' "$1"
}

name="$(sed -n 's/^ORIGIN_HOST=//p' "$env_file" 2>/dev/null | head -n 1)"
if [ -z "$name" ]; then
	for copy in $(ls -t "$dir"/Caddyfile.bak-* 2>/dev/null); do
		if grep -qF "$BLOCK" "$copy"; then
			name="$(site_of "$copy" "$BLOCK")"
			[ -n "$name" ] && break
		fi
	done
fi
if [ -z "$name" ]; then
	echo "The origin name is not in $env_file and no copy of the Caddyfile has the block." >&2
	echo "Nothing was changed. Run deploy/setup-cloudflare.sh again: it asks for the name." >&2
	exit 1
fi

# Another site of the same Caddy, asked before anything is touched and again afterwards.
other="$(awk '/^[^ \t#}{][^{]*\{[ \t]*$/ {print $1; exit}' "$caddyfile")"
probe() {
	curl -s -o /dev/null -m 10 -w '%{http_code}' --resolve "$1:443:127.0.0.1" "https://$1/" \
		2>/dev/null || echo "no answer"
}
before=""
[ -n "$other" ] && [ "$other" != "$name" ] && before="$(probe "$other")"

if grep -qF "$name" "$caddyfile"; then
	echo "The Caddyfile already has the block: nothing appended."
else
	copy="$caddyfile.bak-$(date +%Y%m%d%H%M%S)"
	cp -p "$caddyfile" "$copy"
	# Appending keeps the file's identity, which a single-file Docker mount depends on.
	printf '\n# DSAI Vault. Requests arrive from the Cloudflare Pages proxy; the dsai-vault proxy\n# container rejects anything that does not carry the shared secret.\n%s {\n\t%s\n}\n' \
		"$name" "$BLOCK" >>"$caddyfile"
	if ! docker exec "$container" caddy validate --config /etc/caddy/Caddyfile >/dev/null 2>&1; then
		cat "$copy" >"$caddyfile"
		echo "Caddy did not accept the file with the block. It was put back as it was." >&2
		exit 1
	fi
	echo "Appended the block. The file as it was before: $(basename "$copy")"
fi

if docker exec "$container" caddy reload --config /etc/caddy/Caddyfile >/dev/null 2>&1; then
	echo "Reloaded '$container' (a reload, not a restart)."
else
	echo "The reload was refused: Caddy goes on with what it had. The block is in the file" >&2
	echo "and takes effect when that container is next restarted." >&2
	exit 1
fi

# Remember the name where the next run finds it without needing an old copy of the file.
if [ -f "$env_file" ] && ! grep -q '^ORIGIN_HOST=' "$env_file"; then
	printf 'ORIGIN_HOST=%s\n' "$name" >>"$env_file"
fi

sleep 4
[ -n "$before" ] && echo "The other site, same request before and after: $before -> $(probe "$other")"
echo "This site at the server, without the secret (404 is right): $(probe "$name")"
echo "Sites in the Caddyfile now: $(grep -c '^[^ 	#}{][^{]*{[ 	]*$' "$caddyfile")"
