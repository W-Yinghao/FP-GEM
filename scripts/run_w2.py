"""Run one W2 study on one W1 unit and write <store>/runs/W2/<study>/<unit>.json (atomic).

  python -m scripts.run_w2 --study s1 --unit Lee-c2-tsmnet-t01-s0
"""
from __future__ import annotations

import argparse
import importlib
import sys

from fpgem.paths import RUNS
from fpgem.provenance import git_sha, write_json


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--study", required=True, choices=["s1", "s2", "s3", "s4"])
    ap.add_argument("--unit", nargs="+", required=True)
    ap.add_argument("--wave", default="W2")
    a = ap.parse_args(argv)
    mod = importlib.import_module(f"fpgem.adapt.{a.study}")
    out_dir = RUNS / a.wave / a.study
    out_dir.mkdir(parents=True, exist_ok=True)
    sha = git_sha()
    for uid in a.unit:
        p = out_dir / f"{uid}.json"
        if p.exists():
            continue
        res = mod.run(uid)
        res["git_sha"] = sha
        write_json(p, res)
        print(f"done {uid} {res.get('seconds')}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
