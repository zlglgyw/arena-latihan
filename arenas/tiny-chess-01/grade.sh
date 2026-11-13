#!/bin/bash
# grade.sh — nilai SATU practice trial tiny-chess untuk satu engine.
# Pola yang sama dengan ~/workspace/makefun/run-trials-v8.sh (12 Nov 2026):
# env server Node per trial + engine python3 lewat MAKEFUN_ENV_URL + scorer.
# Bedanya: satu trial saja, port 8090+, state di runs/ arena ini, dan hasil
# langsung dicatat ke scoreboard. Kit hanya DIBACA, tidak pernah ditulis.
#
# Pemakaian:
#   ./grade.sh <trial> <direktori-engine> [label]
#   ./grade.sh 0 entries/v8-baseline
#   ./grade.sh 1 entries/v8-baseline v8-baseline
#   ./grade.sh 0 entries/v9-killer v9-killer
#
#   trial            : 0, 1, atau 2 (practice trial dari kit)
#   direktori-engine : path ke direktori berisi main.py (relatif thd arena ini
#                      atau absolut)
#   label            : nama versi untuk scoreboard (default: nama direktori
#                      engine)
#
# Satu trial ~15-20 menit (8 game gauntlet). Jangan jalankan dua trial
# bersamaan di port yang sama; tiap trial memakai portnya sendiri.
# Port = PORT_BASE + nomor trial (default PORT_BASE=8090). Untuk clone
# arena lokal (beberapa arena jalan bersamaan), set PORT_BASE berbeda,
# mis. PORT_BASE=8190 ./grade.sh 0 entries/v8-baseline
set -u
ARENA_DIR="$(cd "$(dirname "$0")" && pwd)"
KIT="$HOME/workspace/makefun/tiny-chess-01-kit"   # HANYA BACA

TRIAL="${1:-}"
ENGINE_DIR="${2:-}"
LABEL="${3:-}"

if [ -z "$TRIAL" ] || [ -z "$ENGINE_DIR" ]; then
  echo "Pemakaian: $0 <trial 0|1|2> <direktori-engine> [label]"
  exit 2
fi
case "$TRIAL" in 0|1|2) ;; *) echo "ERROR: trial harus 0, 1, atau 2"; exit 2 ;; esac
case "$ENGINE_DIR" in /*) ;; *) ENGINE_DIR="$ARENA_DIR/$ENGINE_DIR" ;; esac
if [ -z "$LABEL" ]; then LABEL="$(basename "$ENGINE_DIR")"; fi
if [ ! -f "$ENGINE_DIR/main.py" ]; then
  echo "ERROR: tidak ada main.py di $ENGINE_DIR"
  exit 2
fi
if [ ! -d "$KIT/practice/trial-$TRIAL" ]; then
  echo "ERROR: kit tidak ditemukan di $KIT"
  exit 2
fi

BYTES=$(wc -c < "$ENGINE_DIR/main.py")
if [ "$BYTES" -gt 4096 ]; then
  echo "ERROR: engine $BYTES byte, melebihi cap 4096 — entry seperti ini ditolak."
  exit 1
fi

PORT_BASE="${PORT_BASE:-8090}"
PORT=$((PORT_BASE + TRIAL))
STAMP=$(date +%Y%m%d-%H%M%S)
RUN="$ARENA_DIR/runs/${LABEL}-trial${TRIAL}-${STAMP}"
mkdir -p "$RUN/scores"
echo "=== GRADE $LABEL trial-$TRIAL (port $PORT) ==="
echo "engine : $ENGINE_DIR/main.py ($BYTES byte)"
echo "run dir: $RUN"
echo "mulai  : $(date '+%Y-%m-%d %H:%M:%S %Z')"

# 0) Smoke test dulu — jangan buang 20 menit untuk engine yang move generatornya salah.
echo "--- smoke test (perft) ---"
if ! taskset -c 0 timeout 600 python3 "$ARENA_DIR/test_engine.py" "$ENGINE_DIR" --quick > "$RUN/smoke.log" 2>&1; then
  echo "SMOKE GAGAL — lihat $RUN/smoke.log. Trial dibatalkan."
  tail -5 "$RUN/smoke.log"
  exit 1
fi
grep -E "^PERFT|middlegame" "$RUN/smoke.log"
echo "smoke OK"

# Cek port bebas.
if (exec 3<>/dev/tcp/127.0.0.1/$PORT) 2>/dev/null; then
  echo "ERROR: port $PORT sudah dipakai — ada trial lain yang jalan?"
  exit 1
fi

# 1) Env server (PID dicatat, dibunuh di akhir — jangan pkill pola global).
MAKEFUN_STATE_DIR="$RUN/state" \
MAKEFUN_ENV_DATA_DIR="$KIT/practice/trial-$TRIAL/input/env" \
MAKEFUN_ENV_PORT=$PORT \
  nohup node "$KIT/program/env/server.mjs" > "$RUN/env.log" 2>&1 < /dev/null &
ENV_PID=$!
cleanup() {
  if kill -0 $ENV_PID 2>/dev/null; then
    kill $ENV_PID 2>/dev/null
    sleep 2
    kill -9 $ENV_PID 2>/dev/null || true
  fi
}
trap cleanup EXIT

# Tunggu server siap (respons HTTP apa pun = sudah naik).
READY=0
for _ in $(seq 1 30); do
  if curl -s -o /dev/null --max-time 1 "http://127.0.0.1:$PORT/" 2>/dev/null; then READY=1; break; fi
  sleep 1
done
if [ "$READY" -ne 1 ]; then
  echo "ERROR: env server tidak naik di port $PORT — lihat $RUN/env.log"
  exit 1
fi
echo "env server naik (pid $ENV_PID)"

# 2) Engine: 1 CPU (taskset), batas waktu 1750 detik (wall trial 1800 detik).
T0=$(date +%s)
cd "$ENGINE_DIR"
MAKEFUN_ENV_URL="http://127.0.0.1:$PORT" \
  timeout 1750 taskset -c 0 python3 main.py > "$RUN/engine.log" 2>&1
ENGINE_EXIT=$?
T1=$(date +%s)
DUR=$((T1 - T0))
echo "engine selesai (exit $ENGINE_EXIT, ${DUR} detik)"
cd "$ARENA_DIR"

# 3) Matikan env server, lalu scorer.
cleanup
trap - EXIT
sleep 2
MAKEFUN_OUTPUT_DIR="$RUN/state/export" \
MAKEFUN_REFERENCE_DIR="$KIT/practice/trial-$TRIAL/reference" \
MAKEFUN_SCORES_DIR="$RUN/scores" \
  node "$KIT/program/scorer/score.mjs" > "$RUN/scorer.log" 2>&1
if [ ! -f "$RUN/scores/scores.json" ]; then
  echo "ERROR: scorer tidak menghasilkan scores.json — lihat $RUN/scorer.log"
  exit 1
fi
SCORES=$(cat "$RUN/scores/scores.json")
echo "SKOR: $SCORES"

# 4) Catat ke scoreboard (jsonl + md).
DATE_WIB=$(TZ=Asia/Jakarta date '+%Y-%m-%d %H:%M WIB')
python3 - "$RUN/scores/scores.json" <<EOF
import json, sys
s = json.load(open(sys.argv[1]))
row = {
    "date": "$DATE_WIB",
    "version": "$LABEL",
    "trial": $TRIAL,
    "elo": s.get("elo"),
    "wins": s.get("wins"),
    "draws": s.get("draws"),
    "losses": s.get("losses"),
    "bytes": $BYTES,
    "working": s.get("working"),
    "spare_plies": s.get("spare_plies"),
    "duration_sec": $DUR,
    "engine_exit": $ENGINE_EXIT,
    "run_dir": "runs/$(basename "$RUN")",
}
with open("$ARENA_DIR/scoreboard.jsonl", "a") as f:
    f.write(json.dumps(row) + "\n")
print("dicatat:", row)
EOF
python3 "$ARENA_DIR/update-scoreboard.py"
echo "=== SELESAI: $LABEL trial-$TRIAL ==="
