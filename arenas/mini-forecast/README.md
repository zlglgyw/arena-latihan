# Arena mini-forecast

Latihan lokal kecil untuk skill forecasting (seperti bounty forecasting
make.fun: xstocks, roblox, polymarket). Tugas: prediksi return 5 hari ke
depan untuk 5 aset sintetik, dinilai dengan Gaussian log-score.
Cepat (hitungan detik), deterministik, tanpa API apa pun.

## Tugas

- Data: 3 dataset sintetik (A/B/C) di `data/`, masing-masing 5 aset
  (ALPHA–ECHO), 200 hari histori + 5 hari masa depan (held-out).
  Dibuat `gen_data.py` dari proses AR(1) dengan seed tetap — jangan
  regenerate (atau skor lama tidak lagi sebanding).
- Entry: program `forecast.py` yang dipanggil
  `python3 forecast.py --input <history.json> --output <forecast.json>`.
  Input hanya berisi histori; masa depan tidak pernah diberikan ke entry.
- Output: `{"assets": {nama: {"mean": [5 nilai], "std": [5 nilai]}}}` —
  prediksi return 5 hari ke depan, satu pasang mean/std per hari.
- Skor = rata-rata Gaussian log-score atas 5 aset × 5 hari × 3 dataset.
  Makin tinggi makin baik. Entry yang tidak valid (std ≤ 0, jumlah nilai
  salah, crash, timeout 120 detik/dataset) gagal grading.

## Perintah

```bash
# Nilai satu entry (otomatis catat scoreboard).
./grade.sh entries/baseline-mean
./grade.sh entries/ar1-v1 ar1-v1

# Regenerasi data (HANYA kalau data hilang — skor lama jadi tidak sebanding).
python3 gen_data.py
```

## Baseline & lantai

| Versi | Mean log-score | A | B | C |
|---|---|---|---|---|
| baseline-mean (climatology, lantai) | 2.6321 | 2.5166 | 2.6894 | 2.6903 |

Baseline memprediksi mean & std historis untuk semua 5 hari — tanpa sinyal
apa pun. Cara mengalahkannya: forecast AR(1) (mean hari ke depan =
mu + phi × (return terakhir − mu), dengan phi diestimasi dari histori),
atau std adaptif. Karena datanya AR(1) murni, entry AR(1) yang benar
SEHARUSNYA mengalahkan baseline — kalau tidak, ada bug di entry.

## Batas jujur

- Hanya 3 dataset × 5 hari masa depan = 75 observasi. Selisih skor kecil
  (< 0.05) bisa jadi noise, bukan perbaikan nyata.
- Data sintetik AR(1) bukan pasar nyata: menang di sini tidak menjamin
  menang di bounty forecasting sungguhan (data nyata punya regime,
  fat tail, dan korelasi antar-aset yang tidak ada di sini).
- Jangan tuning berulang-ulang terhadap 3 dataset yang sama lalu klaim
  menang — itu overfitting ke held-out. Kalau mau serius, tambah dataset
  baru dengan seed baru sebagai "test set" yang jarang dipakai.
