# Template arena baru

Cara menambah arena latihan baru ke `~/workspace/arena-latihan/arenas/`.
Satu arena = satu skill yang bisa dilatih dengan skor terukur, lokal,
tanpa API luar.

## Syarat arena yang bagus

1. **Tugas jelas** — input dan output entry didefinisikan persis
   (format file, batas waktu, batas ukuran).
2. **Scorer lokal deterministik** — entry yang sama selalu dapat skor
   yang sama. Tanpa API luar, tanpa model luar, tanpa random tanpa seed.
   Kalau tugasnya butuh "juri" (mis. nilai gambar), arena ini BUKAN
   tempatnya — pakai penilaian manual terpisah.
3. **Baseline yang sudah dinilai** — satu entry paling sederhana yang
   jalan dan punya skor tercatat. Baseline adalah lantai: perbaikan
   harus mengalahkannya.
4. **Lantai skor tertulis** — angka baseline + (kalau ada) acuan luar
   (mis. skor top 10 live) di README arena, dengan tanggalnya.
5. **Held-out / anti-curang** — entry tidak boleh melihat jawaban
   (data masa depan, hidden tests) saat jalan. Scorer yang memegang
   jawaban, bukan entry.

## Struktur wajib

```
arenas/<nama-arena>/
├── README.md            # tugas, metrik, perintah, baseline & lantai, batas jujur
├── grade.sh             # ./grade.sh <entry-dir> [label] [opsi arena]
├── scoreboard.jsonl     # satu baris JSON per run (dibuat grade.sh)
├── scoreboard.md        # tabel dari jsonl (dibuat update-scoreboard.py)
├── update-scoreboard.py # regenerasi scoreboard.md dari scoreboard.jsonl
├── entries/
│   └── <baseline>/      # baseline entry (sudah dinilai, JANGAN diubah)
└── runs/                # satu direktori per run: input, output, log, result
```

Aturan `grade.sh` (kontrak antar-arena, dipakai `run-practice.sh`):
- Argumen pertama selalu direktori entry; argumen kedua (opsional) label.
- Keluar 0 kalau skor berhasil dicatat, bukan 0 kalau gagal (entry tidak
  valid, crash, timeout).
- Selalu menulis `runs/<label>-<timestamp>/` berisi semua artefak run
  (log + hasil mentah) dan meng-append satu baris ke `scoreboard.jsonl`.
- Port/state dir sendiri, tidak bentrok dengan arena lain.

Aturan `scoreboard.jsonl` (satu baris JSON per run, field wajib):
- `date` (string, `YYYY-MM-DD HH:MM WIB`), `version` (label),
  `run_dir` (relatif, mis. `runs/<label>-<timestamp>`),
- plus kolom skor arena itu (mis. `elo`, `wins`, `draws`, `losses`,
  `bytes` untuk catur; `mean_logscore`, `A`, `B`, `C` untuk forecast).

## Checklist sebelum arena dianggap jadi

- [ ] README arena lengkap (tugas, metrik, perintah, baseline, batas jujur)
- [ ] Baseline entry jalan dan sudah dinilai lewat `grade.sh`
- [ ] Skor baseline tercatat di `scoreboard.jsonl` + `scoreboard.md`
- [ ] Determinisme dicek: grade baseline 2×, skor harus identik
- [ ] `run-practice.sh list` menampilkan arena baru (otomatis dari nama dir)
- [ ] Tidak ada panggilan API luar / keypair / submit di arena mana pun
