#!/usr/bin/env bash
# Run an npm script in apps/web, skipping cleanly when the app is not set up yet.
#
# Two reasons this wrapper exists rather than calling npm from .pre-commit-config.yaml:
#
#   1. `apps/web` does not exist until FND-01. Without the guard, every commit in the
#      meantime fails on a missing directory, and the usual response to a hook that always
#      fails is `--no-verify`, which then becomes the habit.
#   2. When the app exists but `node_modules` does not, the raw npm error is confusing.
#      A contributor needs to be told to run `npm ci`, not to read an npm stack trace.
#
# Usage: scripts/hooks/run_web_check.sh <npm-script-name>
set -euo pipefail

SCRIPT="${1:?usage: run_web_check.sh <npm-script-name>}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
WEB="$ROOT/apps/web"

if [[ ! -f "$WEB/package.json" ]]; then
  echo "skip: apps/web does not exist yet (created in FND-01), skipping '$SCRIPT'"
  exit 0
fi

if [[ ! -d "$WEB/node_modules" ]]; then
  echo "apps/web dependencies are not installed, so '$SCRIPT' cannot run." >&2
  echo "Run:  npm --prefix apps/web ci" >&2
  exit 1
fi

if ! node -e "process.exit(require('$WEB/package.json').scripts?.['$SCRIPT']?0:1)" 2>/dev/null; then
  echo "apps/web/package.json has no '$SCRIPT' script." >&2
  echo "FND-01 requires: dev, build, typecheck, lint, format:check, format:fix, test" >&2
  exit 1
fi

exec npm --prefix "$WEB" run --silent "$SCRIPT"
