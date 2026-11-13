"""Generate 3 dataset sintetik (A/B/C) untuk arena mini-forecast.

Tiap dataset: 5 aset, 200 hari histori return + 5 hari masa depan (held-out).
Return dibuat proses AR(1): r_t = mu + phi*(r_{t-1} - mu) + eps, eps ~ N(0, sigma).
Seed tetap -> file selalu sama. Jalankan sekali; file disimpan di data/.

Pemakaian: python3 gen_data.py
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data")

ASSETS = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO"]
# (mu harian, phi AR(1), sigma harian) per aset — tetap di semua dataset;
# seed hanya mengubah undian noise.
PARAMS = {
    "ALPHA": (0.0008, 0.35, 0.012),
    "BRAVO": (0.0004, 0.10, 0.018),
    "CHARLIE": (-0.0002, 0.55, 0.010),
    "DELTA": (0.0012, 0.25, 0.022),
    "ECHO": (0.0000, 0.45, 0.015),
}
HIST = 200
FUT = 5
BURN = 50


def gen(seed):
    rng = random.Random(seed)
    out = {}
    for name in ASSETS:
        mu, phi, sigma = PARAMS[name]
        r = mu
        series = []
        for _ in range(HIST + FUT + BURN):
            r = mu + phi * (r - mu) + rng.gauss(0, sigma)
            series.append(round(r, 6))
        series = series[BURN:]
        out[name] = {"history": series[:HIST], "future": series[HIST:]}
    return {"seed": seed, "history_days": HIST, "future_days": FUT, "assets": out}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for tag, seed in [("A", 20261113), ("B", 20261114), ("C", 20261115)]:
        path = os.path.join(OUT, f"series-{tag}.json")
        with open(path, "w") as f:
            json.dump(gen(seed), f, indent=1)
        print(f"wrote {path}")
