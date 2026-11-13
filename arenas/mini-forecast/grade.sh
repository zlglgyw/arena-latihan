#!/bin/bash
# grade.sh — nilai satu entry mini-forecast di 3 dataset (A/B/C).
# Cepat (hitungan detik), deterministik.
#
# Pemakaian:
#   ./grade.sh <direktori-entry> [label]
#   ./grade.sh entries/baseline-mean
#   ./grade.sh entries/ar1-v1 ar1-v1
set -u
ARENA_DIR="$(cd "$(dirname "$0")" && pwd)"
ENGINE_DIR="${1:-}"
LABEL="${2:-}"
if [ -z "$ENGINE_DIR" ]; then
  echo "Pemakaian: $0 <direktori-entry> [label]"
  exit 2
fi
case "$ENGINE_DIR" in /*) ;; *) ENGINE_DIR="$ARENA_DIR/$ENGINE_DIR" ;; esac
if [ -z "$LABEL" ]; then LABEL="$(basename "$ENGINE_DIR")"; fi
if [ ! -f "$ENGINE_DIR/forecast.py" ]; then
  echo "ERROR: tidak ada forecast.py di $ENGINE_DIR"
  exit 2
fi
for t in A B C; do
  if [ ! -f "$ARENA_DIR/data/series-$t.json" ]; then
    echo "ERROR: data/series-$t.json tidak ada — jalankan: python3 gen_data.py"
    exit 2
  fi
done

STAMP=$(date +%Y%m%d-%H%M%S)
RUN="$ARENA_DIR/runs/${LABEL}-${STAMP}"
mkdir -p "$RUN"
echo "=== GRADE $LABEL (mini-forecast) ==="
echo "entry  : $ENGINE_DIR/forecast.py"
echo "run dir: $RUN"
if ! python3 "$ARENA_DIR/grade.py" "$ENGINE_DIR" "$RUN" > "$RUN/grade.log" 2>&1; then
  echo "GRADE GAGAL — lihat $RUN/grade.log"
  cat "$RUN/grade.log"
  exit 1
fi
cat "$RUN/grade.log"
DATE_WIB=$(TZ=Asia/Jakarta date '+%Y-%m-%d %H:%M WIB')
python3 - "$RUN/result.json" <<EOF
import json, sys
r = json.load(open(sys.argv[1]))
row = {
    "date": "$DATE_WIB",
    "version": "$LABEL",
    "mean_logscore": r["mean_logscore"],
    "A": r["per_dataset"]["A"],
    "B": r["per_dataset"]["B"],
    "C": r["per_dataset"]["C"],
    "run_dir": "runs/$(basename "$RUN")",
}
with open("$ARENA_DIR/scoreboard.jsonl", "a") as f:
    f.write(json.dumps(row) + "\n")
print("dicatat:", row)
EOF
python3 "$ARENA_DIR/update-scoreboard.py"
echo "=== SELESAI: $LABEL ==="
