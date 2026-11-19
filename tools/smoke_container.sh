#!/usr/bin/env bash
# Run manually only after Docker is installed and running.
set -euo pipefail
image=${1:-wisecow:concurrent-v2}
name="wisecow-smoke-$$"
cleanup() {
  docker logs "$name" 2>&1 || true
  docker rm -f "$name" || true
}
trap cleanup EXIT
# Docker selects an unused host port and binds only to localhost.
docker run -d --name "$name" -p 127.0.0.1::4499 "$image"
port=$(docker port "$name" 4499/tcp | awk -F: '{print $NF}')
for attempt in $(seq 1 20); do
  if response=$(curl --fail --silent --show-error --max-time 3 "http://127.0.0.1:${port}/"); then
    if grep -q '<pre>' <<< "$response"; then
      printf 'PASS: HTTP 200 with cow output on attempt %s\n' "$attempt"
      docker inspect --format 'container_user={{.Config.User}} image={{.Image}}' "$name"
      exit 0
    fi
  fi
  sleep 1
done
printf 'FAIL: Wisecow did not return a successful cow response\n' >&2
exit 1
