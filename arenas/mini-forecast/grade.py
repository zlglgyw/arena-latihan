"""Scorer deterministik arena mini-forecast.

Entry adalah program `forecast.py` yang dipanggil:
  python3 forecast.py --input <history.json> --output <forecast.json>

history.json : {"assets": {nama: [return harian, ...200 nilai...]}}
forecast.json: {"assets": {nama: {"mean": [5 nilai], "std": [5 nilai]}}}
  mean/std = prediksi return 5 hari ke depan, satu pasang per hari.

Skor = rata-rata Gaussian log-score atas 5 aset x 5 hari x 3 dataset (A/B/C):
  log N(x; mean, std) = -0.5*log(2*pi) - log(std) - (x-mean)^2 / (2*std^2)
Makin tinggi makin baik. Entry tidak pernah melihat masa depan: grade.py hanya
memberikan histori; masa depan (held-out) hanya dibaca scorer.

Deterministik: entry yang sama -> skor yang sama (entry dilarang memakai
random tanpa seed tetap dan dilarang membaca apa pun selain file input).

Pemakaian: python3 grade.py <direktori-entry> <direktori-kerja>
  Menulis result.json di direktori kerja dan mencetak ringkasan JSON.
  Keluar 1 kalau entry tidak valid / crash / timeout (120 detik per dataset).
"""
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATASETS = ["A", "B", "C"]
TIMEOUT = 120


def logscore(x, mean, std):
    return -0.5 * math.log(2 * math.pi) - math.log(std) - (x - mean) ** 2 / (2 * std ** 2)


def validate(forecast, assets):
    if not isinstance(forecast, dict) or "assets" not in forecast:
        return "forecast.json harus punya kunci 'assets'"
    fa = forecast["assets"]
    for name in assets:
        if name not in fa:
            return f"aset {name} tidak ada di forecast"
        e = fa[name]
        for k in ("mean", "std"):
            if k not in e or not isinstance(e[k], list) or len(e[k]) != 5:
                return f"aset {name}: '{k}' harus list 5 angka"
            for v in e[k]:
                if not isinstance(v, (int, float)) or not math.isfinite(v):
                    return f"aset {name}: '{k}' berisi nilai tidak hingga/bukan angka"
        if any(v <= 0 for v in e["std"]):
            return f"aset {name}: 'std' harus > 0"
    return None


def main():
    if len(sys.argv) != 3:
        print("Pemakaian: python3 grade.py <direktori-entry> <direktori-kerja>")
        sys.exit(2)
    entry_dir, work = sys.argv[1], sys.argv[2]
    prog = os.path.join(entry_dir, "forecast.py")
    if not os.path.isfile(prog):
        print(f"ERROR: tidak ada forecast.py di {entry_dir}")
        sys.exit(2)
    os.makedirs(work, exist_ok=True)

    per_ds = {}
    for tag in DATASETS:
        ds = json.load(open(os.path.join(HERE, "data", f"series-{tag}.json")))
        hist = {"assets": {n: a["history"] for n, a in ds["assets"].items()}}
        inp = os.path.join(work, f"input-{tag}.json")
        outp = os.path.join(work, f"forecast-{tag}.json")
        json.dump(hist, open(inp, "w"))
        try:
            r = subprocess.run(
                [sys.executable, prog, "--input", inp, "--output", outp],
                cwd=work, capture_output=True, text=True, timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired:
            print(f"ERROR: entry timeout (> {TIMEOUT} detik) di dataset {tag}")
            sys.exit(1)
        if r.returncode != 0:
            print(f"ERROR: entry exit {r.returncode} di dataset {tag}:\n{r.stderr[-2000:]}")
            sys.exit(1)
        if not os.path.isfile(outp):
            print(f"ERROR: entry tidak menulis {outp} di dataset {tag}")
            sys.exit(1)
        fc = json.load(open(outp))
        err = validate(fc, ds["assets"].keys())
        if err:
            print(f"ERROR: forecast dataset {tag} tidak valid: {err}")
            sys.exit(1)
        scores = []
        for name, a in ds["assets"].items():
            for i, x in enumerate(a["future"]):
                scores.append(logscore(x, fc["assets"][name]["mean"][i],
                                       fc["assets"][name]["std"][i]))
        per_ds[tag] = sum(scores) / len(scores)

    mean_score = sum(per_ds.values()) / len(per_ds)
    result = {"mean_logscore": round(mean_score, 4), "per_dataset": {k: round(v, 4) for k, v in per_ds.items()}}
    json.dump(result, open(os.path.join(work, "result.json"), "w"), indent=1)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
