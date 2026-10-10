#!/usr/bin/env bash
# Fetch Docker Official Images for a CI job, patiently.
#
#   bash .github/scripts/pull-image.sh python:3.13-slim caddy:2-alpine
#
# GitHub's runners share a small set of addresses with every other project, and public
# registries limit anonymous downloads per address. So a pull now and then fails with
# "toomanyrequests: Rate exceeded" through no fault of this repository, and a red run on
# main means no deploy.
#
# The official images are published in several places. This tries each place in turn,
# several times with a growing pause, and then names what it got the way the Dockerfile
# and the workflow name it (the first registry below). Every later step finds the image
# on the machine and does not go to a registry at all.

set -euo pipefail

# Amazon's and Google's mirrors of the official images, then Docker Hub itself.
REGISTRIES=(public.ecr.aws/docker/library mirror.gcr.io/library docker.io/library)
ROUNDS=4

fetch() {
	local image="$1" wanted="${REGISTRIES[0]}/$1" round registry
	for round in $(seq 1 "$ROUNDS"); do
		for registry in "${REGISTRIES[@]}"; do
			if docker pull --quiet "$registry/$image" >/dev/null; then
				if [[ "$registry/$image" != "$wanted" ]]; then
					docker tag "$registry/$image" "$wanted"
				fi
				echo "$image: from $registry"
				return 0
			fi
		done
		if ((round < ROUNDS)); then
			echo "$image: every registry refused, waiting $((round * 10)) s (round $round of $ROUNDS)"
			sleep "$((round * 10))"
		fi
	done
	echo "$image: could not be fetched from any registry" >&2
	return 1
}

(($# > 0)) || {
	echo "usage: $0 <image:tag> [<image:tag> ...]" >&2
	exit 2
}
for image in "$@"; do
	fetch "$image"
done
