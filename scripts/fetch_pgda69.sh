#!/usr/bin/env bash
# PGDA product 69 — average solar illumination (south poles) for S12 compare (D-9ab3).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${ROOT}/data/pgda69"
mkdir -p "$DEST"
UA="moonpark/0.1 (+https://github.com/Pedrojonfg/moonpark)"
BASE="https://pgda.gsfc.nasa.gov/data/MoonIllumination"

fetch() {
  local url="$1" name="$2"
  echo "==> ${name}"
  curl -L --fail --retry 5 --retry-all-errors -A "$UA" -C - -o "${DEST}/${name}" "${url}"
}

# 85–90°S 60 m/px — matches PGDA-78 validation sites (D-9ab3).
fetch "${BASE}/AVGVISIB_85S_060M_201608.TIF" "AVGVISIB_85S_060M_201608.TIF"

echo "done → ${DEST}"