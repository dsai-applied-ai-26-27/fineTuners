#!/usr/bin/env bash
# Run once, on your own computer, to switch on "Continue with Google" on the live site.
#
#   bash deploy/setup-google.sh <user@host> <client-secret.json>
#
# <client-secret.json> is the file Google Cloud Console offers for download when you create
# an OAuth client of type "Web application" (docs/DEPLOYMENT.md, "Accounts", has the
# clicks). What the script does, in order:
#
#   1. reads the client id and the client secret out of that file
#   2. puts the current deploy/ configuration on the server, because compose.yaml is what
#      hands the two values to Django
#   3. stores both in the server's .env. They travel over ssh on standard input: never in
#      a command line, never printed
#   4. restarts the containers
#   5. adds the same two values to your local .env, so signing in with Google also works
#      on http://localhost:8000 (start it with: uv run --env-file .env python manage.py runserver)
#
# Needs: ssh access to the server and uv. Run it from the commit you are about to deploy.
# On Windows start it with Git Bash by its full path (see docs/DEPLOYMENT.md).

set -euo pipefail

usage="usage: setup-google.sh <user@host> <client-secret.json>"
target="${1:?$usage}"
file="${2:?$usage}"
[[ -f "$file" ]] || { echo "no such file: $file" >&2; exit 1; }
cd "$(dirname "$0")/.."

echo "==> 1/5 reading $file"
# Two lines: the id, then the secret. Kept in variables, never echoed.
mapfile -t credentials < <(uv run --no-project python - "$file" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1], encoding="utf-8"))
client = data.get("web") or data.get("installed") or {}
print(client.get("client_id", ""))
print(client.get("client_secret", ""))
PY
)
client_id="${credentials[0]:-}"
client_secret="${credentials[1]:-}"
client_id="${client_id%$'\r'}"
client_secret="${client_secret%$'\r'}"
[[ "$client_id" == *.apps.googleusercontent.com && -n "$client_secret" ]] ||
	{ echo "that file does not look like a Google OAuth client (type: Web application)" >&2; exit 1; }
echo "    client ${client_id%%-*}-…"

echo "==> 2/5 server: installing the current configuration"
git archive HEAD deploy | ssh "$target" '
	set -e
	rm -rf ~/dsai-vault/setup && mkdir -p ~/dsai-vault/setup
	tar -x -C ~/dsai-vault/setup
	bash ~/dsai-vault/setup/deploy/deploy.sh install ~/dsai-vault/setup/deploy' | sed 's/^/    /'

echo "==> 3/5 server: storing the client id and secret"
printf '%s\n' "$client_id" | ssh "$target" 'dsai-vault/bin/deploy setenv GOOGLE_OAUTH_CLIENT_ID' >/dev/null
printf '%s\n' "$client_secret" | ssh "$target" 'dsai-vault/bin/deploy setenv GOOGLE_OAUTH_CLIENT_SECRET' >/dev/null
echo "    stored"

echo "==> 4/5 server: restarting"
ssh "$target" 'dsai-vault/bin/deploy restart' >/dev/null 2>&1
echo "    restarted"

echo "==> 5/5 this computer: .env"
touch .env
chmod 600 .env 2>/dev/null || true
grep -v -e '^GOOGLE_OAUTH_CLIENT_ID=' -e '^GOOGLE_OAUTH_CLIENT_SECRET=' .env >.env.tmp || true
{
	cat .env.tmp
	printf 'GOOGLE_OAUTH_CLIENT_ID=%s\n' "$client_id"
	printf 'GOOGLE_OAUTH_CLIENT_SECRET=%s\n' "$client_secret"
} >.env
rm -f .env.tmp
echo "    written (.env is ignored by git)"

host="$(ssh "$target" 'sed -n "s/^PUBLIC_HOST=//p" ~/dsai-vault/.env')"
echo
echo "Done. Google must list exactly these under 'Authorised redirect URIs' of the client:"
echo "    https://$host/accounts/google/login/callback/"
echo "    http://localhost:8000/accounts/google/login/callback/"
echo
echo "The button appears once the code with sign-in is deployed. You can delete $file now;"
echo "the secret can be shown again, or replaced, in Google Cloud Console."
