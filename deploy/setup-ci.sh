#!/usr/bin/env bash
# Run once, on your own computer, to let GitHub Actions deploy to the server.
#
#   bash deploy/setup-ci.sh <user@host> <owner/repo>
#
# What it does, in order:
#   1. makes a new SSH key pair that exists only for deploys
#   2. adds the public half to the server, pinned to one command (`deploy ci`), so the key
#      cannot open a shell or do anything except ship a release
#   3. stores the private half, the server's address and its host key as GitHub Actions
#      secrets, and switches the deploy job on
#   4. deletes the private half from this computer; GitHub now holds the only copy
#
# Needs: ssh access to the server, and the GitHub CLI (`gh auth status` must be logged in).

set -euo pipefail

target="${1:?usage: setup-ci.sh <user@host> <owner/repo>}"
repo="${2:?usage: setup-ci.sh <user@host> <owner/repo>}"
host="${target#*@}"
key="$(mktemp -d)/dsai_vault_deploy"
trap 'rm -rf "$(dirname "$key")"' EXIT

echo "==> checking the server and its host key"
remote_home="$(ssh "$target" 'printf %s "$HOME"')"
ssh "$target" "test -x '$remote_home/dsai-vault/bin/deploy'" ||
	{ echo "the server has no ~/dsai-vault/bin/deploy yet: install the app there first" >&2; exit 1; }
# Reuse the host key this computer already trusts, rather than asking the network again.
known_hosts="$(ssh-keygen -F "$host" | grep -v '^#' || true)"
[[ -n "$known_hosts" ]] || { echo "no known_hosts entry for $host: connect with ssh once first" >&2; exit 1; }

echo "==> creating the deploy key"
ssh-keygen -q -t ed25519 -N "" -C "github-actions deploy ($repo)" -f "$key"

echo "==> adding it to the server, limited to 'deploy ci'"
line="restrict,command=\"$remote_home/dsai-vault/bin/deploy ci\" $(cat "$key.pub")"
printf '%s\n' "$line" | ssh "$target" '
	umask 077
	mkdir -p ~/.ssh
	touch ~/.ssh/authorized_keys
	read -r line
	printf "%s\n" "$line" >> ~/.ssh/authorized_keys'

echo "==> storing the secrets in $repo"
gh secret set DEPLOY_SSH_KEY --repo "$repo" <"$key"
printf '%s\n' "$known_hosts" | gh secret set DEPLOY_KNOWN_HOSTS --repo "$repo"
printf '%s' "$target" | gh secret set DEPLOY_TARGET --repo "$repo"
gh variable set DEPLOY_ENABLED --repo "$repo" --body true

echo "==> checking that the key is confined"
# Asking for a shell command must be refused by the deploy script.
if ssh -i "$key" -o IdentitiesOnly=yes -o BatchMode=yes "$target" 'id' 2>&1 | grep -q "may only run"; then
	echo "    good: the key can only deploy"
else
	echo "    WARNING: the key was not refused as expected. Check ~/.ssh/authorized_keys on the server." >&2
fi

echo
echo "Done. The next push to main deploys by itself."
echo "To revoke: delete the line ending in 'github-actions deploy ($repo)' from"
echo "~/.ssh/authorized_keys on the server."
