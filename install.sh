#!/bin/bash
# EvolveAgent installer — zero-config, one command.
set -e

DEST="${HERMES_HOME:-$HOME/.hermes}/skills"
SRC="$(cd "$(dirname "$0")" && pwd)"

echo "Installing evolve-agent → $DEST/evolve-agent"
mkdir -p "$DEST"
cp -r "$SRC" "$DEST/evolve-agent"
rm -rf "$DEST/evolve-agent/.git"
echo "Done. Restart your gateway, then verify:"
echo "  python3 $DEST/evolve-agent/scripts/planner.py \"test\"   # expect exit 2"
