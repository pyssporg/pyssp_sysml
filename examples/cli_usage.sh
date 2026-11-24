#!/usr/bin/env bash
set -euo pipefail

# Generate the aircraft example's SSD, parameter sets, bootstrap SysML, and
# SSD-synced SysML through the pyssp CLI. Run from the pyssp_dev workspace root:
#
#   bash repos/pyssp_sysml/examples/cli_usage.sh [--out DIR]

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ARCH="$SCRIPT_DIR/aircraft_subset"
COMP="AircraftComposition"

OUT_DIR="build/examples/cli_usage"
if [[ $# -gt 0 ]]; then
  if [[ "$1" != "--out" || $# -ne 2 ]]; then
    echo "usage: $0 [--out DIR]" >&2
    exit 2
  fi
  OUT_DIR="${2%/}"
fi
BOOTSTRAP_DIR="$OUT_DIR/new_architecture"

pyssp generate ssd \
  --architecture "$ARCH" \
  --composition "$COMP" \
  --core-definitions \
  --output "$OUT_DIR/SystemStructure.ssd" >/dev/null

pyssp generate ssv \
  --architecture "$ARCH" \
  --composition "$COMP" \
  --core-definitions \
  --output-dir "$OUT_DIR/parameter_sets" >/dev/null

mkdir -p "$BOOTSTRAP_DIR"
pyssp generate sysml \
  --ssd "$OUT_DIR/SystemStructure.ssd" \
  --composition "$COMP" \
  --output "$BOOTSTRAP_DIR/architecture.sysml" >/dev/null

pyssp sync ssd \
  --architecture "$ARCH" \
  --composition "$COMP" \
  --core-definitions \
  --ssd "$OUT_DIR/SystemStructure.ssd" \
  --output-architecture-dir "$OUT_DIR/synced_sysml" >/dev/null

printf '%s\n' \
  "$OUT_DIR/SystemStructure.ssd" \
  "$OUT_DIR/parameter_sets" \
  "$BOOTSTRAP_DIR/architecture.sysml" \
  "$OUT_DIR/synced_sysml"
