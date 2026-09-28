"""W2 analysis exactly as pre-registered (prereg/W2_ADAPTATION_FROZEN.md + appenda A1–A3).

  python -m scripts.analyze_w2 --out results/W2
Aggregation: mean over seeds within subject; paired cluster bootstrap over subjects (10,000, percentile 95%);
Holm over the primary contrasts within each study and cell.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from fpgem.paths import REPO, RUNS

B = 10_000


def load(study: str) -> list:
    out = []
    for f in sorted((RUNS / "W2" / study).glob("*.json")):
        d = json.load(open(f))
        if "rows" in d:
            out.append(d)
    return out


def cell_of(uid: str) -> tuple:
    ds, ls, bb, t, s = uid.split("-")
    return (ds, ls, bb), int(t[1:]), int(s[1:])


def boot_ci(diff: np.ndarray, rng) -> tuple:
    n = len(diff)
    idx = rng.integers(0, n, size=(B, n))
    means = diff[idx].mean(1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    p = 2 * min(np.mean(means <= 0), np.mean(means >= 0))
    return float(diff.mean()), float(lo), float(hi), float(min(p, 1.0))


def holm(ps: list) -> list:
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, (len(ps) - i) * ps[j])
        adj[j] = min(run, 1.0)
    return adj.tolist()


def subject_means(recs: dict) -> dict:
    """recs: {(cell, subject, seed): value} -> {cell: {subject: mean over seeds}}"""
    acc = defaultdict(lambda: defaultdict(list))
    for (cell, subj, seed), v in recs.items():
        acc[cell][subj].append(v)
    return {c: {s: float(np.mean(v)) for s, v in d.items()} for c, d in acc.items()}


def analyze_s1(rng, lines, table):
    runs = load("s1")
    vals = defaultdict(dict)       # (protocol, readout, method) -> {(cell, subj, seed): bacc}
    diag = defaultdict(list)
    for d in runs:
        cell, subj, seed = cell_of(d["unit"])
        for r in d["rows"]:
            for ro in ("bacc_head", "bacc_density"):
                if r[ro] == r[ro]:
                    vals[(r["protocol"], ro, r["method"])][(cell, subj, seed)] = r[ro]
            if r["protocol"] == "inductive":
                diag[(cell, r["method"])].append((r["prior_move_l1"], r["converged"], r["iters"]))
    primary = [("FP", "Joint"), ("Kstar", "FP"), ("Kstar", "Joint")]
    secondary = [("FP", "Identity"), ("Pooled", "Identity"), ("Recenter", "FP"), ("K6", "FP")]
    lines += ["## S1 — estimator family under natural shift", ""]
    for protocol in ("inductive", "transductive"):
        for ro in ("bacc_head", "bacc_density"):
            tag = "PRIMARY" if (protocol, ro) == ("inductive", "bacc_head") else "secondary"
            lines += [f"### {protocol}, {ro} ({tag})", "",
                      "| cell | method means (bAcc %) | contrast | Δ (pts) | 95% CI | Holm p | n subj |",
                      "|---|---|---|---|---|---|---|"]
            sm = {m: subject_means(vals[(protocol, ro, m)]) for m in
                  ("Identity", "Pooled", "FP", "Joint", "K6", "Kstar", "Recenter")}
            cells = sorted({c for m in sm.values() for c in m})
            for cell in cells:
                means = {m: 100 * np.mean(list(sm[m][cell].values())) for m in sm if cell in sm[m]}
                mtxt = ", ".join(f"{m} {v:.1f}" for m, v in means.items())
                res = []
                for (x, yv) in primary + secondary:
                    if cell not in sm[x] or cell not in sm[yv]:
                        continue
                    subs = sorted(set(sm[x][cell]) & set(sm[yv][cell]))
                    diff = np.array([sm[x][cell][s] - sm[yv][cell][s] for s in subs]) * 100
                    res.append(((x, yv), boot_ci(diff, rng), len(subs)))
                pp = [r[1][3] for r in res if r[0] in primary]
                adj = holm(pp) if pp else []
                k = 0
                for (x, yv), (m, lo, hi, p), n in res:
                    hp = f"{adj[k]:.3g}" if (x, yv) in primary else "—"
                    if (x, yv) in primary:
                        k += 1
                    lines.append(f"| {'/'.join(cell)} | {mtxt} | {x} − {yv} | {m:+.2f} | [{lo:+.2f}, {hi:+.2f}] | {hp} | {n} |")
                    table.append(dict(study="S1", protocol=protocol, readout=ro, cell="/".join(cell), contrast=f"{x}-{yv}",
                                      delta=m, lo=lo, hi=hi, holm_p=(adj[k - 1] if (x, yv) in primary else None), n=n))
                    mtxt = ""
            lines.append("")
    lines += ["### S1 diagnostics (inductive): mean prior movement ‖π̂−π_src‖₁, convergence", "",
              "| cell | method | mean prior move | converged | median iters |", "|---|---|---|---|---|"]
    for (cell, m), v in sorted(diag.items()):
        a = np.array(v, dtype=float)
        lines.append(f"| {'/'.join(cell)} | {m} | {a[:, 0].mean():.3f} | {a[:, 1].mean():.3f} | {np.median(a[:, 2]):.0f} |")
    lines.append("")


def analyze_s2(rng, lines, table):
    runs = load("s2")
    err = defaultdict(lambda: defaultdict(list))
    for d in runs:
        cell, subj, seed = cell_of(d["unit"])
        for r in d["rows"]:
            err[(cell, r["scale"], r["design"], r["estimator"])][subj].append((r["geom_err"], r["bacc_eval"]))
    lines += ["## S2 — multi-batch known proportions (geometry error E, lower is better)", "",
              "| cell | scale | design | FP-union E | MB-known E | MB-known − FP-union ΔE | 95% CI | MB-unknown E | MB-interval E | Pooled E |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    keys = sorted({(c, s, des) for (c, s, des, e) in err})
    for (c, s, des) in keys:
        def sm(e):
            d = err[(c, s, des, e)]
            return {k: np.mean([x[0] for x in v]) for k, v in d.items()}
        fp, mk = sm("FP-union"), sm("MB-known")
        subs = sorted(set(fp) & set(mk))
        diff = np.array([mk[k] - fp[k] for k in subs])
        m, lo, hi, p = boot_ci(diff, rng)
        others = {e: np.mean(list(sm(e).values())) for e in ("MB-unknown", "MB-interval", "Pooled-union")}
        lines.append(f"| {'/'.join(c)} | {s} | {des} | {np.mean(list(fp.values())):.3f} | {np.mean(list(mk.values())):.3f} | "
                     f"{m:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {others['MB-unknown']:.3f} | {others['MB-interval']:.3f} | {others['Pooled-union']:.3f} |")
        table.append(dict(study="S2", cell="/".join(c), scale=s, design=des, contrast="MBknown-FPunion", delta=m, lo=lo, hi=hi, n=len(subs)))
    lines.append("")


def wilson(k, n):
    if n == 0:
        return (float("nan"),) * 3
    z = 1.96
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return p, c - h, c + h


def analyze_s3(lines, table):
    runs = load("s3")
    agg = defaultdict(lambda: [0, 0, 0, 0])
    for d in runs:
        cell, subj, seed = cell_of(d["unit"])
        for r in d["rows"]:
            a = agg[(cell, r["cell"])]
            a[0] += r["lr"]["reject"]; a[1] += 1; a[2] += r["moment"]["reject"]; a[3] += 1
    lines += ["## S3 — fixed-prior mismatch detection (rejection rate, Wilson 95% CI)", "",
              "| cell | condition | LR test reject | moment test reject | n tests |", "|---|---|---|---|---|"]
    for (cell, cond), (k, n, km, nm) in sorted(agg.items()):
        p, lo, hi = wilson(k, n)
        pm, lom, him = wilson(km, nm)
        lines.append(f"| {'/'.join(cell)} | {cond} | {p:.3f} [{lo:.3f}, {hi:.3f}] | {pm:.3f} [{lom:.3f}, {him:.3f}] | {n} |")
        table.append(dict(study="S3", cell="/".join(cell), condition=cond, lr_reject=p, lr_lo=lo, lr_hi=hi,
                          moment_reject=pm, n=n))
    lines.append("")


def analyze_s4(rng, lines, table):
    runs = load("s4")
    dep = defaultdict(list)
    rec = defaultdict(lambda: defaultdict(list))
    for d in runs:
        cell, subj, seed = cell_of(d["unit"])
        clean = d["clean_identity_bacc"]
        by = defaultdict(dict)
        for r in d["rows"]:
            by[(r["injection"], r["draw"])][r["method"]] = r
        for (inj, draw), ms in by.items():
            r0 = next(iter(ms.values()))
            dep[(cell, inj)].append(r0["dep_p"] <= 0.05)
            ident = ms["Identity"]["bacc"]
            drop = clean - ident
            for m, r in ms.items():
                if abs(drop) > 1e-9:
                    rec[(cell, inj, m)][subj].append((r["bacc"] - ident) / drop)
    lines += ["## S4 — injections: class-dependence of the latent response and recovery", "",
              "| cell | injection | fraction with class-dependent Δz (perm p ≤ .05) | n |", "|---|---|---|---|"]
    for (cell, inj), v in sorted(dep.items()):
        p, lo, hi = wilson(int(np.sum(v)), len(v))
        lines.append(f"| {'/'.join(cell)} | {inj} | {p:.3f} [{lo:.3f}, {hi:.3f}] | {len(v)} |")
        table.append(dict(study="S4", cell="/".join(cell), injection=inj, class_dependent_frac=p, n=len(v)))
    lines += ["", "| cell | injection | method | recovery ratio (median over subjects) | IQR |", "|---|---|---|---|---|"]
    for (cell, inj, m), d in sorted(rec.items()):
        v = np.array([np.mean(x) for x in d.values()])
        lines.append(f"| {'/'.join(cell)} | {inj} | {m} | {np.median(v):.3f} | [{np.percentile(v, 25):.3f}, {np.percentile(v, 75):.3f}] |")
    lines.append("")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "results" / "W2"))
    a = ap.parse_args(argv)
    rng = np.random.default_rng(20260928)
    lines = ["# W2 results (neutral; pre-registered analysis)", ""]
    table = []
    analyze_s1(rng, lines, table)
    analyze_s2(rng, lines, table)
    analyze_s3(lines, table)
    analyze_s4(rng, lines, table)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "W2_RESULTS_TABLES.md").write_text("\n".join(lines) + "\n")
    with open(out / "w2_contrasts.json", "w") as f:
        json.dump(table, f, indent=1, default=float)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
