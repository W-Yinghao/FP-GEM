"""Run one W1 training unit:  python -m scripts.run_unit --unit B14-c4-tsmnet-t01-s0

Any exception writes a reason-coded FAILED_<n>.json into the unit directory before re-raising, so
attempt-capped units can be reported mechanically (pre-reg §6).
"""
from __future__ import annotations

import argparse
import os
import socket
import sys
import traceback


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit", required=True)
    ap.add_argument("--wave", default="W1")
    a = ap.parse_args(argv)
    from fpgem.paths import unit_dir
    from fpgem.provenance import write_json
    from fpgem.train.source import run_unit
    try:
        res = run_unit(a.unit, wave=a.wave)
    except BaseException as e:
        d = unit_dir(a.wave, a.unit)
        d.mkdir(parents=True, exist_ok=True)
        n = len(list(d.glob("FAILED_*.json"))) + 1
        try:
            import torch
            gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        except Exception:
            gpu = None
        write_json(d / f"FAILED_{n}.json", dict(
            unit=a.unit, wave=a.wave, reason=type(e).__name__, message=str(e)[:2000],
            traceback=traceback.format_exc()[-4000:], host=socket.gethostname(), gpu=gpu,
            slurm_job=os.environ.get("SLURM_JOB_ID"), launch_sha=os.environ.get("FPGEM_LAUNCH_SHA")))
        raise
    print(res, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
