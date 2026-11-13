"""Regenerasi scoreboard.md dari scoreboard.jsonl (arena mini-forecast).

Pemakaian: python3 update-scoreboard.py
Tabel diurutkan mean log-score tertinggi dulu.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JL = os.path.join(HERE, "scoreboard.jsonl")
MD = os.path.join(HERE, "scoreboard.md")

rows = []
if os.path.exists(JL):
    with open(JL) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

rows.sort(key=lambda r: (r.get("mean_logscore") if r.get("mean_logscore") is not None else -1e9), reverse=True)

out = []
out.append("# Scoreboard — mini-forecast (arena lokal)")
out.append("")
out.append("Diurutkan mean log-score tertinggi dulu (makin tinggi makin baik).")
out.append("Lantai = baseline-mean (climatology). Skor adalah rata-rata Gaussian")
out.append("log-score atas 5 aset x 5 hari x 3 dataset sintetik (A/B/C).")
out.append("")
out.append("| Versi | Mean log-score | A | B | C | Tanggal | Run |")
out.append("|---|---|---|---|---|---|---|")
for r in rows:
    out.append(
        "| {version} | {mean} | {A} | {B} | {C} | {date} | {run_dir} |".format(
            version=r.get("version", "?"),
            mean=r.get("mean_logscore", "?"),
            A=r.get("A", "?"),
            B=r.get("B", "?"),
            C=r.get("C", "?"),
            date=r.get("date", "?"),
            run_dir=r.get("run_dir", "?"),
        )
    )
if not rows:
    out.append("| _(belum ada run)_ | | | | | | |")
out.append("")
out.append("Sumber data: `scoreboard.jsonl` (satu baris JSON per run).")
out.append("")
open(MD, "w").write("\n".join(out))
print(f"scoreboard.md ditulis ({len(rows)} run)")
