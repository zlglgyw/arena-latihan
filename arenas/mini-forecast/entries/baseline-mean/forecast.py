"""Baseline climatology untuk arena mini-forecast.

Prediksi: mean & std historis tiap aset, dipakai untuk kelima hari ke depan.
Tidak memakai sinyal apa pun (tidak ada AR, tidak ada momentum) — ini lantai
skor arena. Entry yang lebih baik harus mengalahkannya, misalnya dengan
forecast AR(1): mean hari ke depan = mu + phi*(return terakhir - mu).

Deterministik: tanpa random.
"""
import argparse
import json
import statistics

ap = argparse.ArgumentParser()
ap.add_argument("--input", required=True, help="history.json dari scorer")
ap.add_argument("--output", required=True, help="forecast.json untuk ditulis")
a = ap.parse_args()

hist = json.load(open(a.input))["assets"]
out = {"assets": {}}
for name, rets in hist.items():
    mu = statistics.fmean(rets)
    sd = statistics.pstdev(rets)
    sd = max(sd, 0.005)  # lantai: jangan pernah klaim terlalu yakin
    out["assets"][name] = {"mean": [round(mu, 6)] * 5, "std": [round(sd, 6)] * 5}

json.dump(out, open(a.output, "w"), indent=1)
