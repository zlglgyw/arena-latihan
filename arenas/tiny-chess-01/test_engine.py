"""Tes lokal engine tiny-chess (BUKAN bagian dari entry).

Menguji main.py engine apa pun di arena ini: perft (kebenaran move generator),
sanity eval/search, dan kecepatan. Diadaptasi dari
~/workspace/makefun/test_engine.py (12 Nov 2026) — bedanya, path engine
diterima sebagai argumen, bukan hardcode ke repo asli.

Pemakaian:
  python3 test_engine.py <path-ke-direktori-engine> [--quick|--full]
  --quick : perft sampai depth 3 saja (smoke test sebelum trial, ~1 menit)
  --full  : perft sampai depth 4 (default kalau tidak disebut? tidak — default
            adalah --quick; pakai --full untuk pemeriksaan menyeluruh)

Keluar 0 kalau semua perft PASS, 1 kalau ada yang FAIL.
"""
import argparse
import os
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("engine_dir", help="direktori engine (berisi main.py)")
ap.add_argument("--quick", action="store_true", help="perft sampai depth 3")
ap.add_argument("--full", action="store_true", help="perft sampai depth 4")
args = ap.parse_args()

ENGINE = os.path.join(args.engine_dir, "main.py")
if not os.path.isfile(ENGINE):
    print(f"ERROR: tidak ada main.py di {args.engine_dir}")
    sys.exit(2)
print(f"engine: {ENGINE} ({os.path.getsize(ENGINE)} byte, batas 4096)")

os.environ["MAKEFUN_ENV_URL"] = "http://127.0.0.1:9"  # dummy; driver tidak jalan
SRC = open(ENGINE).read()
if "b85decode(" in SRC:  # entry ter-pack (pack.py): unpack dulu
    import base64
    import lzma
    import re

    m = re.search(r'b85decode\("([^"]+)"\)', SRC)
    assert m, "payload pack tidak ditemukan di main.py"
    SRC = lzma.decompress(base64.b85decode(m.group(1))).decode()
    print(f"entry ter-pack, src ter-unpack {len(SRC)} byte")
NS = {}
# Potong sebelum driver HTTP: yang diuji hanya bagian library engine.
exec(SRC.split('g=post("/game",{})')[0], NS)
parse, gen, make, ev, sr, best, uci = NS["parse"], NS["gen"], NS["make"], NS["ev"], NS["sr"], NS["best"], NS["uci"]
TT, nd = NS["TT"], NS["nd"]


def perft(b, w, c, e, d):
    if d == 0:
        return 1
    n = 0
    for m in gen(b, w, c, e, 0):
        nb, nw, nc, ne = make(b, c, e, m, w)
        n += perft(nb, nw, nc, ne, d - 1)
    return n


CASES_FULL = [
    ("startpos", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     {1: 20, 2: 400, 3: 8902, 4: 197281}),
    ("kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
     {1: 48, 2: 2039, 3: 97862}),
    ("ep", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1",
     {1: 14, 2: 191, 3: 2812, 4: 43238}),
    ("castling", "r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1",
     {1: 6, 2: 264, 3: 9467}),
    ("talking5", "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8",
     {1: 44, 2: 1486, 3: 62379}),
    ("talking6", "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10",
     {1: 46, 2: 2079, 3: 89890}),
]

full = args.full or not args.quick
cases = CASES_FULL if full else [
    (name, fen, {d: v for d, v in want.items() if d <= 3})
    for name, fen, want in CASES_FULL
]
print(f"mode: {'full' if full else 'quick'}")

ok = True
for name, fen, want in cases:
    b, w, c, e = parse(fen)
    for d, exp in want.items():
        got = perft(b, w, c, e, d)
        s = "OK " if got == exp else "FAIL"
        if got != exp:
            ok = False
        print(f"perft {name} d{d}: {got} (want {exp}) {s}")
print("PERFT", "ALL PASS" if ok else "FAILED")

# eval sanity: startpos simetris ~0; putih unggul menteri ~ +900
b, w, c, e = parse("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
print("eval startpos:", ev(b, w))
b, w, c, e = parse("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
print("eval white up queen:", ev(b, w))


def search_move(fen, legal):
    b, w, c, e = parse(fen)
    nd[0] = 0
    TT.clear()
    t0 = time.time()
    m, s = best(b, w, c, e, legal)
    return (uci(m) if m else None), s, nd[0], time.time() - t0


# mate in 1: Qxf7#
fen = "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1"
b, w, c, e = parse(fen)
legal = [uci(m) for m in gen(b, w, c, e, 0)]
mv, s, n, dt = search_move(fen, legal)
print(f"mate-in-1: {mv} score={s} nodes={n} time={dt:.2f}s (want h5f7, mate score)")

# hanging queen: menteri hitam di d5, pion e4 menyerang tanpa penjaga
fen2 = "rnb1kbnr/ppp1pppp/8/3q4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 1"
b, w, c, e = parse(fen2)
legal = [uci(m) for m in gen(b, w, c, e, 0)]
mv, s, n, dt = search_move(fen2, legal)
print(f"hanging queen: {mv} score={s} nodes={n} time={dt:.2f}s (want e4d5, score ~900)")

# kecepatan: posisi middlegame, satu langkah penuh (budget node engine), 1 CPU
fen3 = "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
b, w, c, e = parse(fen3)
legal = [uci(m) for m in gen(b, w, c, e, 0)]
mv, s, n, dt = search_move(fen3, legal)
print(f"middlegame: {mv} score={s} nodes={n} time={dt:.2f}s nps={n/max(dt,0.01):.0f}")

sys.exit(0 if ok else 1)
