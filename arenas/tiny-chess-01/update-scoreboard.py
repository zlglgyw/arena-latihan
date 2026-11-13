"""Regenerasi scoreboard.md dari scoreboard.jsonl (arena tiny-chess-01).

Pemakaian: python3 update-scoreboard.py
Membaca scoreboard.jsonl di direktori yang sama, menulis scoreboard.md.
Tabel diurutkan Elo tertinggi dulu.
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

rows.sort(key=lambda r: (r.get("elo") or 0), reverse=True)

out = []
out.append("# Scoreboard — tiny-chess-01 (arena lokal)")
out.append("")
out.append("Diurutkan Elo tertinggi dulu. Skor lokal = proksi skor server make.fun,")
out.append("bukan jaminan. Lantai practice: 1154 Elo. Baseline sunfish ~1325 Elo.")
out.append("Top 10 live make.fun per 13 Nov 2026 19:30 WIB: 1850 Elo.")
out.append("")
out.append("| Versi | Trial | Elo | Menang | Seri | Kalah | Byte | Tanggal | Run |")
out.append("|---|---|---|---|---|---|---|---|---|")
for r in rows:
    out.append(
        "| {version} | {trial} | {elo} | {wins} | {draws} | {losses} | {nbytes} | {date} | {run_dir} |".format(
            version=r.get("version", "?"),
            trial=r.get("trial", "?"),
            elo=r.get("elo", "?"),
            wins=r.get("wins", "?"),
            draws=r.get("draws", "?"),
            losses=r.get("losses", "?"),
            nbytes=r.get("bytes", "?"),
            date=r.get("date", "?"),
            run_dir=r.get("run_dir", "?"),
        )
    )
if not rows:
    out.append("| _(belum ada run)_ | | | | | | | | |")
out.append("")
out.append("Sumber data: `scoreboard.jsonl` (satu baris JSON per run).")
out.append("")
open(MD, "w").write("\n".join(out))
print(f"scoreboard.md ditulis ({len(rows)} run)")
