"""Run one W1 training unit:  python -m scripts.run_unit --unit B14-c4-tsmnet-t01-s0"""
from __future__ import annotations

import argparse
import sys


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", required=True)
    ap.add_argument("--wave", default="W1")
    a = ap.parse_args(argv)
    from fpgem.train.source import run_unit
    res = run_unit(a.unit, wave=a.wave)
    print(res, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
