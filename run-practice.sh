#!/bin/bash
# run-practice.sh — helper root arena latihan.
#
#   ./run-practice.sh list                        daftar arena
#   ./run-practice.sh grade <arena> [args...]     grading (diteruskan ke grade.sh arena)
#   ./run-practice.sh smoke <arena> [args...]     smoke test (kalau arena punya smoke.sh)
#   ./run-practice.sh scoreboard [arena]          tampilkan scoreboard
#
# Contoh:
#   ./run-practice.sh grade tiny-chess-01 0 entries/v8-baseline
#   ./run-practice.sh grade mini-forecast entries/baseline-mean
#   ./run-practice.sh scoreboard tiny-chess-01
set -u
ROOT="$(cd "$(dirname "$0")" && pwd)"
ARENAS="$ROOT/arenas"

usage() {
  sed -n '2,10p' "$0"
  echo ""
  echo "Arena yang tersedia:"
  for d in "$ARENAS"/*/; do
    name="$(basename "$d")"
    [ "$name" = "_template" ] && continue
    desc="$(sed -n '3p' "$d/README.md" 2>/dev/null)"
    printf '  %-16s %s\n' "$name" "$desc"
  done
}

cmd="${1:-}"
case "$cmd" in
  list)
    for d in "$ARENAS"/*/; do
      name="$(basename "$d")"
      [ "$name" = "_template" ] && continue
      desc="$(sed -n '3p' "$d/README.md" 2>/dev/null)"
      printf '%-16s %s\n' "$name" "$desc"
    done
    ;;
  grade)
    arena="${2:-}"
    [ -z "$arena" ] && { echo "Pemakaian: $0 grade <arena> [args...]"; exit 2; }
    shift 2
    [ -x "$ARENAS/$arena/grade.sh" ] || { echo "ERROR: tidak ada arena '$arena' (atau tidak punya grade.sh)"; exit 2; }
    cd "$ARENAS/$arena" && exec ./grade.sh "$@"
    ;;
  smoke)
    arena="${2:-}"
    [ -z "$arena" ] && { echo "Pemakaian: $0 smoke <arena> [args...]"; exit 2; }
    shift 2
    [ -x "$ARENAS/$arena/smoke.sh" ] || { echo "ERROR: arena '$arena' tidak punya smoke.sh"; exit 2; }
    cd "$ARENAS/$arena" && exec ./smoke.sh "$@"
    ;;
  scoreboard)
    arena="${2:-}"
    if [ -n "$arena" ]; then
      [ -f "$ARENAS/$arena/scoreboard.md" ] || { echo "ERROR: tidak ada scoreboard untuk arena '$arena'"; exit 2; }
      cat "$ARENAS/$arena/scoreboard.md"
    else
      for d in "$ARENAS"/*/; do
        name="$(basename "$d")"
        [ "$name" = "_template" ] && continue
        [ -f "$d/scoreboard.md" ] || continue
        echo "########## $name ##########"
        cat "$d/scoreboard.md"
        echo ""
      done
    fi
    ;;
  help|--help|-h|"")
    usage
    ;;
  *)
    echo "Perintah tidak dikenal: $cmd"
    usage
    exit 2
    ;;
esac
