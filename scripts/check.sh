#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
NODE_BIN="/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin"
PNPM_BIN="/Users/alexandrubogdan/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin"

cd "$ROOT_DIR/backend"
venv/bin/python -m pytest tests -q

cd "$ROOT_DIR/frontend"
if [ -x "$PNPM_BIN/pnpm" ]; then
  PATH="$NODE_BIN:$PNPM_BIN:$PATH" "$PNPM_BIN/pnpm" build
elif command -v pnpm >/dev/null 2>&1; then
  PATH="$NODE_BIN:$PATH" pnpm build
else
  echo "pnpm is required to build the frontend." >&2
  exit 1
fi
