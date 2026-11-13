#!/bin/bash
# smoke.sh — smoke test cepat (perft + sanity search) untuk satu engine.
# Jalankan ini SEBELUM trial penuh: trial butuh 15-20 menit, smoke ~1 menit.
#
# Pemakaian:
#   ./smoke.sh <direktori-engine> [--full]
#   ./smoke.sh entries/v8-baseline          (quick: perft sampai depth 3)
#   ./smoke.sh entries/v8-baseline --full   (full: perft sampai depth 4)
set -u
ARENA_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="${1:-}"
MODE="${2:---quick}"
if [ -z "$ENGINE_DIR" ]; then
  echo "Pemakaian: $0 <direktori-engine> [--full]"
  exit 2
fi
case "$ENGINE_DIR" in /*) ;; *) ENGINE_DIR="$ARENA_DIR/$ENGINE_DIR" ;; esac
if [ ! -f "$ENGINE_DIR/main.py" ]; then
  echo "ERROR: tidak ada main.py di $ENGINE_DIR"
  exit 2
fi
BYTES=$(wc -c < "$ENGINE_DIR/main.py")
echo "engine: $ENGINE_DIR/main.py ($BYTES byte, batas 4096)"
if [ "$BYTES" -gt 4096 ]; then
  echo "ERROR: engine melebihi cap 4096 byte — entry seperti ini ditolak."
  exit 1
fi
cd "$ARENA_DIR"
exec taskset -c 0 timeout 600 python3 test_engine.py "$ENGINE_DIR" "$MODE"
