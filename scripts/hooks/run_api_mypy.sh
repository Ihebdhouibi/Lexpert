#!/usr/bin/env bash
# Run mypy over apps/api, skipping cleanly when the app is not set up yet.
#
# CLAUDE.md rule 5 promises that pre-commit runs mypy for the API. This wrapper is what
# makes that true without breaking every commit before FND-01 exists, and without the
# confusing failure you get when mypy is simply not installed.
#
# mypy runs over the whole package rather than over the staged files: a type error is
# rarely confined to the file that caused it, and per-file mypy invocations miss exactly
# the cross-module breakage that matters most in a modular monolith.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
API="$ROOT/apps/api"

if [[ ! -f "$API/pyproject.toml" ]]; then
  echo "skip: apps/api does not exist yet (created in FND-01), skipping mypy"
  exit 0
fi

if [[ ! -d "$API/src" ]]; then
  echo "skip: apps/api/src does not exist yet, skipping mypy"
  exit 0
fi

if ! command -v mypy >/dev/null 2>&1; then
  echo "mypy is not installed, so the API type check cannot run." >&2
  echo "Run:  pip install -e 'apps/api[dev]'" >&2
  exit 1
fi

cd "$API"
exec mypy src
