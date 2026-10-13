#!/usr/bin/env bash
# The server side of every deploy. On the server this file is ~/dsai-vault/bin/deploy.
#
#   deploy install <folder> [host]   put compose.yaml, Caddyfile and this script in place;
#                                    on first use also create .env with new secrets
#   deploy app <commit>              reads a .tar.gz of the code on standard input:
#                                    build the image, migrate, restart, re-sync content
#   deploy content                   reads a .tar.gz of course files on standard input:
#                                    validate them, then replace the live ones and load them
#   deploy status | logs | restart   look at, or restart, what is running
#   deploy setenv NAME               set one value in .env, read from standard input
#   deploy backup                    copy the database to ~/dsai-vault/backups/
#   deploy schedule-backup           do that every night (adds a line to the crontab)
#   deploy restore <file>            replace the database with one of those copies
#   deploy manage <args>             run manage.py inside the running container
#   deploy ci                        the only thing the GitHub Actions key may run
#
# Nothing here needs root; the user must be allowed to run docker. docs/DEPLOYMENT.md
# explains the whole arrangement.

set -euo pipefail
umask 022

ROOT="${DSAI_ROOT:-$HOME/dsai-vault}"
KEEP_RELEASES=3

say() { printf '\n==> %s\n' "$*"; }
die() {
	printf 'deploy: %s\n' "$*" >&2
	exit 1
}

compose() { docker compose --project-directory "$ROOT" --file "$ROOT/compose.yaml" "$@"; }

# Two deploys at once would trip over each other; the second one stops here.
lock() {
	exec 9>"$ROOT/.deploy.lock"
	flock --nonblock 9 || die "another deploy is running, try again in a minute"
}

random_secret() { openssl rand -hex 32; }

cmd_install() {
	local source="${1:-}" host="${2:-}"
	[[ -f "$source/compose.yaml" && -f "$source/Caddyfile" && -f "$source/deploy.sh" ]] ||
		die "usage: deploy install <folder with compose.yaml, Caddyfile, deploy.sh> [public-host]"

	mkdir -p "$ROOT/bin" "$ROOT/courses" "$ROOT/releases"
	install -m 644 "$source/compose.yaml" "$ROOT/compose.yaml"
	install -m 644 "$source/Caddyfile" "$ROOT/Caddyfile"
	install -m 755 "$source/deploy.sh" "$ROOT/bin/deploy"
	say "installed compose.yaml, Caddyfile and bin/deploy in $ROOT"

	if [[ ! -f "$ROOT/.env" ]]; then
		[[ -n "$host" ]] || die "first install: also give the public host name, e.g. dsai3.pages.dev"
		# The secrets are generated here and written straight to the file: they never
		# appear on screen or in a log.
		(
			umask 077
			{
				printf 'PUBLIC_HOST=%s\n' "$host"
				printf 'DJANGO_SECRET_KEY=%s\n' "$(random_secret)"
				printf 'ORIGIN_SECRET=%s\n' "$(random_secret)"
			} >"$ROOT/.env"
		)
		say "wrote $ROOT/.env with new secrets (readable by you only)"
	else
		say "kept the existing $ROOT/.env"
	fi

	# The proxy joins the Docker network of whatever already serves port 443 here.
	if ! grep -q '^FRONT_NETWORK=' "$ROOT/.env"; then
		local front network
		front="$(docker ps --filter publish=443 --format '{{.Names}}' | head -n 1)"
		[[ -n "$front" ]] ||
			die "no container publishes port 443; add FRONT_NETWORK=<docker network> to $ROOT/.env"
		network="$(docker inspect "$front" \
			--format '{{range $k, $v := .NetworkSettings.Networks}}{{println $k}}{{end}}' | head -n 1)"
		printf 'FRONT_NETWORK=%s\n' "$network" >>"$ROOT/.env"
		say "the proxy will join '$network', the Docker network of '$front'"
	fi

	if docker image inspect dsai-vault:live >/dev/null 2>&1; then
		say "run 'deploy restart' for the new configuration to take effect"
	fi
}

wait_until_up() {
	local attempt
	for attempt in $(seq 1 30); do
		if compose exec -T web python deploy/smoke.py >/dev/null 2>&1; then
			return 0
		fi
		sleep 2
	done
	compose logs --tail 40 web >&2 || true
	die "the site did not come up within a minute; the log lines above say why"
}

check_proxy() {
	# From inside the proxy container, so the secret is read there and never printed.
	# shellcheck disable=SC2016
	compose exec -T proxy sh -c \
		'wget -q -O /dev/null --header "X-Origin-Auth: $ORIGIN_SECRET" http://127.0.0.1:8080/' ||
		die "the proxy does not answer a request that carries the secret"
	if compose exec -T proxy wget -q -O /dev/null http://127.0.0.1:8080/ 2>/dev/null; then
		die "the proxy answers WITHOUT the secret: do not put this online"
	fi
	echo "  proxy: answers with the secret, refuses without it"
}

# Whether the Caddy that owns port 443 still has this site's block. That file belongs to
# another project on the server; when that project is deployed again, its own copy of the
# file replaces it and the block is gone. The public address then answers 525 ("SSL
# handshake failed") for everyone, with nothing wrong in here. deploy/restore-front.sh
# puts the block back.
front_door() {
	local container caddyfile
	container="$(docker ps --filter publish=443 --format '{{.Names}}' | head -n 1)"
	if [[ -z "$container" ]]; then
		echo "nothing on this server publishes port 443"
		return 1
	fi
	caddyfile="$(docker inspect "$container" --format \
		'{{range .Mounts}}{{if eq .Destination "/etc/caddy/Caddyfile"}}{{.Source}}{{end}}{{end}}')"
	if [[ -f "$caddyfile" ]] && grep -qF "reverse_proxy dsai-vault:8080" "$caddyfile"; then
		echo "the main Caddy ('$container') passes requests on to this site"
		return 0
	fi
	echo "MISSING: the main Caddy ('$container') has no block for this site, so the"
	echo "         public address answers 525. Put it back from your computer with:"
	echo "           ssh <server> 'bash -s' < deploy/restore-front.sh"
	return 1
}

prune() {
	local old
	# Newest first; everything after the first few goes, with its image.
	while IFS= read -r old; do
		[[ -n "$old" ]] || continue
		rm -rf "${ROOT:?}/releases/$old"
		docker image rm "dsai-vault:$old" >/dev/null 2>&1 || true
	done < <(ls -1t "$ROOT/releases" | tail -n "+$((KEEP_RELEASES + 1))")
	docker image prune --force --filter "label=dsai.commit" >/dev/null 2>&1 || true
}

cmd_app() {
	local commit="${1:-}"
	[[ "$commit" =~ ^[0-9a-f]{7,40}$ ]] || die "usage: deploy app <commit> < release.tar.gz"
	[[ -f "$ROOT/compose.yaml" && -f "$ROOT/.env" ]] || die "run 'deploy install' first"
	lock

	local release="$ROOT/releases/$commit"
	rm -rf "$release"
	mkdir -p "$release"
	say "unpacking release $commit"
	tar -xzf - -C "$release" --no-same-owner --no-same-permissions
	[[ -f "$release/Dockerfile" ]] || die "the archive has no Dockerfile: is it this project?"

	say "building the image"
	docker build --tag "dsai-vault:$commit" --label "dsai.commit=$commit" "$release"
	docker tag "dsai-vault:$commit" dsai-vault:live

	say "applying database migrations"
	compose run --rm --no-deps -T web python manage.py migrate --noinput

	say "starting the new version"
	compose up --detach --remove-orphans
	wait_until_up

	# New code may render content differently, so load the course files again. A course
	# the new code rejects keeps its old rows; the failure is reported at the end.
	say "loading course content"
	local content_ok=1
	compose exec -T web python manage.py sync_content || content_ok=0

	say "checking the result"
	compose exec -T web python deploy/smoke.py
	check_proxy
	# Said, not enforced: this deploy did its work either way, and the fix is elsewhere.
	echo "  front: $(front_door || true)"
	prune

	[[ "$content_ok" == 1 ]] || die "version $commit is live, but some course content did not load (see above)"
	say "version $commit is live"
}

cmd_content() {
	docker image inspect dsai-vault:live >/dev/null 2>&1 || die "deploy the app before any content"
	lock

	local incoming="$ROOT/incoming"
	rm -rf "$incoming"
	mkdir -p "$incoming"
	say "unpacking course files"
	tar -xzf - -C "$incoming" --no-same-owner --no-same-permissions
	[[ -n "$(find "$incoming" -mindepth 2 -maxdepth 2 -name course.yaml -print -quit)" ]] ||
		die "the archive contains no course (expected <course>/course.yaml)"

	# The same check authors run locally, against the new files, before anything live
	# changes. If it fails the script stops here and the site is untouched.
	say "validating"
	compose run --rm --no-deps -T \
		--volume "$incoming:/incoming:ro" --env DSAI_COURSES_DIR=/incoming \
		web python manage.py sync_content --check

	say "replacing the live course files"
	rsync --archive --delete "$incoming/" "$ROOT/courses/"
	rm -rf "$incoming"

	say "loading into the database"
	compose exec -T web python manage.py sync_content
	say "content is live"
}

cmd_setenv() {
	# The value comes on standard input, so it never appears in a command line, in the
	# shell history or in a log.
	local name="${1:-}" value tmp
	[[ "$name" =~ ^[A-Z][A-Z0-9_]*$ ]] || die "usage: deploy setenv NAME   (value on standard input)"
	[[ -f "$ROOT/.env" ]] || die "run 'deploy install' first"
	IFS= read -r value || true
	[[ -n "$value" ]] || die "no value arrived on standard input"
	tmp="$(mktemp "$ROOT/.env.XXXXXX")" # created readable by its owner only
	grep -v "^$name=" "$ROOT/.env" >"$tmp" || true
	printf '%s=%s\n' "$name" "$value" >>"$tmp"
	mv "$tmp" "$ROOT/.env"
	say "set $name in $ROOT/.env; 'deploy restart' applies it"
}

cmd_backup() {
	# Accounts and progress exist only in the database, so it needs copies. SQLite's own
	# backup gives a consistent file even while the site is in use. It is written next to
	# the database by the Python inside the container, then copied out to the host.
	local stamp name
	stamp="$(date +%Y%m%d-%H%M%S)"
	name="db-$stamp.sqlite3"
	mkdir -p "$ROOT/backups"
	chmod 700 "$ROOT/backups"
	compose exec -T web python - <<'PY'
import sqlite3

source = sqlite3.connect("/data/db.sqlite3")
target = sqlite3.connect("/data/backup.sqlite3")
with target:
    source.backup(target)
target.close()
source.close()
PY
	docker cp "$(compose ps --quiet web):/data/backup.sqlite3" "$ROOT/backups/$name"
	compose exec -T web rm -f /data/backup.sqlite3
	chmod 600 "$ROOT/backups/$name"
	# Keep the newest fourteen.
	ls -1t "$ROOT/backups"/db-*.sqlite3 | tail -n +15 | xargs --no-run-if-empty rm -f
	say "saved $ROOT/backups/$name ($(du -h "$ROOT/backups/$name" | cut -f1))"
}

cmd_schedule_backup() {
	# One line in this user's crontab: a backup every night. Safe to run twice.
	local line="17 3 * * * $ROOT/bin/deploy backup >/dev/null 2>&1"
	if crontab -l 2>/dev/null | grep -qF "$ROOT/bin/deploy backup"; then
		say "the nightly backup is already scheduled"
		return
	fi
	(
		crontab -l 2>/dev/null || true
		printf '%s\n' "$line"
	) | crontab -
	say "scheduled: a backup every night at 03:17, the newest fourteen kept in $ROOT/backups"
}

cmd_restore() {
	local file="${1:-}"
	[[ -f "$file" ]] || die "usage: deploy restore <backup file>"
	lock
	say "stopping the site"
	compose stop web
	say "putting $file in place"
	# In a one-off container, as the app's own user so the file ends up owned by it. The
	# old write-ahead files belong to the database being replaced and must go with it.
	compose run --rm --no-deps -T web sh -c \
		'rm -f /data/db.sqlite3-wal /data/db.sqlite3-shm && cat > /data/db.sqlite3' <"$file"
	compose start web
	wait_until_up
	say "restored. Publish again if course content changed since that backup."
}

cmd_status() {
	compose ps
	printf '\nversion: %s\n' "$(docker image inspect dsai-vault:live --format '{{ index .Config.Labels "dsai.commit" }}' 2>/dev/null || echo 'nothing deployed')"
	printf 'courses: %s\n' "$(find "$ROOT/courses" -mindepth 2 -maxdepth 2 -name course.yaml 2>/dev/null | wc -l)"
	printf 'front:   %s\n' "$(front_door || true)"
}

cmd_ci() {
	# In ~/.ssh/authorized_keys the GitHub Actions key is pinned to "deploy ci", so
	# whatever that key asks for, this function runs instead. The request itself arrives
	# in SSH_ORIGINAL_COMMAND, and exactly one shape of it is accepted.
	local request="${SSH_ORIGINAL_COMMAND:-}"
	[[ "$request" =~ ^app\ ([0-9a-f]{40})$ ]] || die "this key may only run: app <full commit id>"
	cmd_app "${BASH_REMATCH[1]}"
}

command="${1:-}"
shift || true
case "$command" in
install) cmd_install "$@" ;;
app) cmd_app "$@" ;;
content) cmd_content ;;
status) cmd_status ;;
logs) compose logs --tail "${1:-100}" web proxy ;;
restart) compose up --detach --force-recreate ;;
setenv) cmd_setenv "$@" ;;
backup) cmd_backup ;;
schedule-backup) cmd_schedule_backup ;;
restore) cmd_restore "$@" ;;
manage)
	# Docker wants a terminal for `exec` unless told otherwise, and there is none when
	# this is run as: ssh host "dsai-vault/bin/deploy manage ...".
	if [[ -t 0 ]]; then
		compose exec web python manage.py "$@"
	else
		compose exec -T web python manage.py "$@"
	fi
	;;
ci) cmd_ci ;;
*) die "unknown command '${command}'. See the top of $0 for the list." ;;
esac
