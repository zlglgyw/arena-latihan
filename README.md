# Arena Latihan (lokal, mirip make.fun)

Sistem latihan lokal supaya saya bisa berlatih dan mengiterasi entry
dengan skor terukur — tanpa submit apa pun ke make.fun.

## Apa ini

Tiap "arena" adalah satu skill yang bisa dilatih: ada tugasnya, ada
scorer lokal deterministik, ada baseline yang sudah dinilai, dan ada
scoreboard yang mencatat setiap percobaan. Saya latih entry di sini,
ukur skornya, perbaiki yang kurang — baru kalau Pak memerintahkan,
entry dibawa ke bounty sungguhan.

Arena yang sudah ada:

| Arena | Skill | Metrik | Baseline |
|---|---|---|---|
| `tiny-chess-01` | Engine catur 4 KB Python | Elo vs gauntlet 8 house engine | v8-baseline (salinan engine v8, 12 Nov) |
| `mini-forecast` | Forecasting deret waktu | Gaussian log-score, 3 dataset | baseline-mean (climatology) |

## Loop latihan

```
bangun → nilai lokal (grade.sh) → catat skor (scoreboard) → perbaiki
   ↑                                                        |
   └────────────────── ulangi, tanpa batas iterasi ─────────┘
```

1. **Bangun** — buat/salin entry baru di `arenas/<arena>/entries/<versi>/`.
   Baseline tidak pernah diubah; versi baru selalu salinan baru.
2. **Nilai lokal** — `./run-practice.sh grade <arena> ...` (atau
   `grade.sh` langsung di dalam arena). Scorer lokal deterministik.
3. **Catat skor** — otomatis ke `scoreboard.jsonl` + `scoreboard.md`.
   Skor lama tidak pernah dihapus; perbandingan antar-versi harus dari
   scoreboard yang sama.
4. **Perbaiki** — satu perubahan terukur per iterasi, lalu nilai lagi.
   Kalau skor turun, versi lama tetap ada di scoreboard sebagai acuan.

## Perintah

```bash
./run-practice.sh list                        # daftar arena
./run-practice.sh grade tiny-chess-01 0 entries/v8-baseline
./run-practice.sh grade mini-forecast entries/baseline-mean
./run-practice.sh smoke tiny-chess-01 entries/v8-baseline
./run-practice.sh scoreboard                  # semua scoreboard
./run-practice.sh scoreboard tiny-chess-01    # satu arena
```

Detail tiap arena ada di `arenas/<arena>/README.md`.
Cara menambah arena baru: `arenas/_template/TEMPLATE.md`.

## Batas jujur (baca sebelum mengklaim apa pun)

- **Latihan meningkatkan kualitas entry + playbook saya, BUKAN mengubah
  model dasar.** Saya tidak menjadi "lebih pintar" secara umum karena
  latihan — yang meningkat adalah entry yang dibangun, catatan apa yang
  berhasil/gagal, dan cara kerja yang teruji. Itu tetap berharga, tapi
  jangan diklaim lebih dari itu.
- **Skor lokal adalah proksi, bukan jaminan.** Trial practice memakai
  seed/opening yang sama dengan kit, tapi penilaian server memakai seed
  berbeda; Elo dari 8 game punya noise besar; data sintetik bukan pasar
  nyata. Skor lokal naik ≠ peringkat server naik sama besarnya.
- **Grading lewat script itu murah; yang makan token adalah iterasi
  saya.** Sekali jalan `grade.sh` hampir tidak memakai token — yang mahal
  adalah saya membaca hasil, menganalisis, dan menulis ulang entry.
  **Tidak ada batas iterasi demi hemat token** (Pak, 13 Nov 19:39 WIB:
  "Gausah hemat token"; Pak mengalokasikan 2M token khusus untuk
  make.fun, 13 Nov 19:40 WIB — kalau bisa menang, Pak tambah token).
  Yang TETAP berlaku: **disiplin satu perubahan per iterasi** (satu
  perubahan entry → nilai → catat di scoreboard), karena itu soal
  kebenaran pengukuran, bukan soal token. Dua perubahan sekaligus
  membuat skor tidak bisa diatribusikan ke perubahan yang mana.

## Aturan keras

- Lokal saja: **jangan panggil API make.fun, jangan submit, jangan pakai
  keypair/API key make.fun** dari arena ini.
- Jangan ubah apa pun di `~/workspace/makefun/` — kit dan repo asli hanya
  dibaca (kit tiny-chess dipakai read-only oleh `grade.sh`).
- Baseline di `entries/` tidak pernah diubah; versi baru = direktori baru.
