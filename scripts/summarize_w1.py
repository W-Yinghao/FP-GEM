"""Collect W1 unit outputs into a coverage report and the descriptive sanity table (pre-reg §7).

  python -m scripts.summarize_w1 [--wave W1] [--out results/W1]
Nothing here is an endpoint: it reports source-model sanity numbers, coverage and provenance only.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from fpgem.paths import REPO, RUNS


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", default="W1")
    ap.add_argument("--units", default=str(REPO / "configs" / "units_W1.txt"))
    ap.add_argument("--out", default=str(REPO / "results" / "W1"))
    a = ap.parse_args(argv)
    units = [l.strip() for l in open(a.units) if l.strip() and not l.startswith("#")]
    rows, missing = [], []
    for u in units:
        d = RUNS / a.wave / u
        done = d / "DONE.json"
        if not done.exists():
            missing.append(u)
            continue
        dj = json.load(open(done))
        mj = json.load(open(d / "metrics.json"))
        sj = json.load(open(d / "sanity_target.json"))       # target-side values: read only here, after the fleet
        ds, ls, bb, t, s = u.split("-")
        rows.append(dict(unit=u, dataset=ds, label_set=ls, backbone=bb, target=int(t[1:]), seed=int(s[1:]),
                         sanity_eval_bacc=sj["sanity_eval_bacc"], best_val_bacc=mj["best_val_bacc"],
                         best_epoch=mj["best_epoch"], epochs_run=mj["epochs_run"], seconds=dj["seconds"],
                         gpu=dj["gpu"], git_sha=dj["git_sha"][:12], replay=dj["replay_bit_exact"]))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    import csv
    with open(out / "w1_units.csv", "w", newline="") as f:
        if rows:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    groups = defaultdict(list)
    for r in rows:
        groups[(r["dataset"], r["label_set"], r["backbone"])].append(r)
    lines = ["# W1 coverage and source-model sanity (descriptive; not endpoints)", "",
             f"units done: {len(rows)}/{len(units)}; missing: {len(missing)}", "",
             "| dataset | labels | backbone | units | subjects | eval bAcc mean (subject-level SD) | val bAcc mean | best epoch median | best epoch >= 95 | minutes median | GPUs |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for (ds, ls, bb), rs in sorted(groups.items()):
        by_subj = defaultdict(list)
        for r in rs:
            by_subj[r["target"]].append(r["sanity_eval_bacc"])
        subj_means = np.array([np.mean(v) for v in by_subj.values()])
        gpus = sorted({r["gpu"] for r in rs})
        lines.append(f"| {ds} | {ls} | {bb} | {len(rs)} | {len(by_subj)} | {100 * subj_means.mean():.1f} ({100 * subj_means.std(ddof=1) if len(subj_means) > 1 else 0:.1f}) | "
                     f"{100 * np.mean([r['best_val_bacc'] for r in rs]):.1f} | {np.median([r['best_epoch'] for r in rs]):.0f} | "
                     f"{sum(r['best_epoch'] >= 95 for r in rs)}/{len(rs)} | "
                     f"{np.median([r['seconds'] for r in rs]) / 60:.1f} | {', '.join(gpus)} |")
    lines += ["", "`best epoch >= 95`: units whose selected epoch is at the 100-epoch cap (validation bAcc still rising; "
              "possible under-training, reported as a QC diagnostic, not acted on).",
              "", "Sanity eval bAcc: EEGNet/Chambon = eval-mode network with source normalisation; TSMNet = each target "
              "session re-centred on its own label-set trials (standard TSMNet inference).", ""]
    if missing:
        lines += ["## Missing units", ""] + [f"- {m}" for m in missing]
    (out / "W1_COVERAGE.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[:4 + len(groups) + 2]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
