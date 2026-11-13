# Arena tiny-chess-01

Latihan lokal untuk bounty make.fun tiny-chess-01: engine catur Python
maksimal 4.096 byte, dinilai melawan gauntlet 8 house engine lewat kit resmi.
Semua penilaian memakai kode kit (env + scorer) — tidak ada API make.fun,
tidak ada submit, tidak ada keypair.

## Cara kerja

Satu trial = 8 game melawan gauntlet (depth-2, depth-3, depth-4, nodes-100k,
nodes-250k, nodes-500k, nodes-1M, nodes-2M), masing-masing dari opening
berbeda, warna selang-seling. Scorer kit menghitung Elo dari hasil game
(anchor: depth-2 855 … nodes-2M 1712; cap 2112).

- Kit (hanya baca): `~/workspace/makefun/tiny-chess-01-kit/` — env server
  (`program/env/server.mjs`), scorer (`program/scorer/score.mjs`), dan 3
  practice trial (`practice/trial-0/1/2`). Kit tidak pernah ditulis arena.
- Satu trial ~15–20 menit. Engine jalan 1 CPU (`taskset -c 0`), batas
  10 detik/langkah dari env, wall time trial 1.800 detik.

## Perintah

```bash
# Smoke test cepat (~10 detik): perft + sanity search. WAJIB sebelum trial.
./smoke.sh entries/v8-baseline
./smoke.sh entries/v9-xxx --full        # perft sampai depth 4

# Nilai satu trial (otomatis smoke test dulu, lalu catat scoreboard).
./grade.sh 0 entries/v8-baseline                  # trial-0, label = nama dir
./grade.sh 1 entries/v9-xxx v9-xxx                # trial-1, label eksplisit
```

Port: PORT_BASE + nomor trial (default 8090/8091/8092) — tidak bentrok
dengan run lama 12 Nov (8080–8082). Untuk clone lokal, set PORT_BASE
berbeda (mis. `PORT_BASE=8190`). Tiap run punya direktori sendiri di
`runs/` berisi
`state/`, `env.log`, `engine.log`, `scorer.log`, `scores/scores.json`,
dan `smoke.log`.

## Baseline & lantai

| Acuan | Elo |
|---|---|
| Lantai practice (bounty) | 1154 |
| Baseline sunfish ~ | 1325 |
| v7 (60k node, uji lokal 12 Nov, trial-0b) | 1173 (1M / 3S / 4K) |
| v8-baseline (80k node + killer moves, trial-0, 13 Nov 19:50 WIB) | **871 (0M / 2S / 6K)** — DI BAWAH lantai 1154 dan di bawah v7 di trial yang sama. Penyebab: 2 game berbalik (vs depth-3: v7 menang mat, v8 kalah mat; vs depth-4: v7 seri, v8 kalah mat). Bukan timeout (think maks 4.237 ms dari batas 10.000 ms) dan bukan crash — kekalahan catur murni. Satu trial 8 game belum bisa membuktikan v8 lebih lemah dari v7 (noise besar), tapi juga belum membuktikan v8 lebih baik — butuh trial-1 dan trial-2. |
| Top 10 live make.fun (13 Nov 2026 19:30 WIB) | 1850 |
| Top 1–5 live make.fun (13 Nov 2026 19:30 WIB) | 2110 |

Catatan jujur: Elo lokal dihitung dari 8 game melawan gauntlet yang SAMA
dengan server (practice trial), jadi proksinya cukup dekat — tapi trial
scored di server memakai seed & opening berbeda, dan Elo dari 8 game punya
noise besar (±100 Elo lebih). Skor lokal yang naik belum tentu berarti
peringkat server naik sama besarnya.

## Menambah versi engine baru

1. Salin `entries/v8-baseline/` ke `entries/<nama-baru>/`, ubah `main.py`.
2. Jaga `main.py` ≤ 4096 byte dan snapshot repo ≤ 8192 byte (aturan bounty).
3. `./smoke.sh entries/<nama-baru>/` lalu `./grade.sh <trial> entries/<nama-baru>/`.
4. Jangan pernah ubah `entries/v8-baseline/` — itu baseline beku.
