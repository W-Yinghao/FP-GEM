"""Build preprocessed caches.

  python -m scripts.build_cache --dataset B14 --subjects 1 2 3
  python -m scripts.build_cache --dataset Lee --subjects 1-18
  python -m scripts.build_cache --dataset Sleep --subjects 0-40      (all nights of these subjects)
  python -m scripts.build_cache --dataset B14 --manifest             (hash all cached files)
"""
from __future__ import annotations

import argparse
import sys
import time


def parse_subjects(tokens):
    out = []
    for t in tokens:
        if "-" in t:
            a, b = t.split("-")
            out.extend(range(int(a), int(b) + 1))
        else:
            out.append(int(t))
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["B14", "Lee", "Sleep"])
    ap.add_argument("--subjects", nargs="*", default=[])
    ap.add_argument("--manifest", action="store_true")
    ap.add_argument("--skip-existing", action="store_true")
    a = ap.parse_args(argv)
    from fpgem.data import mi, sleep
    from fpgem.paths import cache_dir

    if a.manifest:
        p = sleep.write_manifest() if a.dataset == "Sleep" else mi.write_manifest(a.dataset)
        print("manifest", p)
        return 0
    subs = parse_subjects(a.subjects)
    failures = []
    if a.dataset == "Sleep":
        recs = sleep.recordings()
        jobs = [(s, n) for (s, n) in sorted(recs) if s in subs]
        for s, n in jobs:
            out = cache_dir("Sleep") / f"sub{s:02d}_n{n}.npz"
            if a.skip_existing and out.exists():
                continue
            t0 = time.time()
            try:
                sleep.build_recording(s, n)
                print(f"ok Sleep s{s} n{n} ({time.time() - t0:.1f}s)", flush=True)
            except Exception as e:  # reason-coded, never silent
                failures.append((s, n, repr(e)))
                print(f"FAIL Sleep s{s} n{n}: {e!r}", flush=True)
    else:
        for s in subs:
            out = cache_dir(a.dataset) / f"sub{s:02d}.npz"
            if a.skip_existing and out.exists():
                continue
            t0 = time.time()
            try:
                mi.build_subject(a.dataset, s)
                print(f"ok {a.dataset} s{s} ({time.time() - t0:.1f}s)", flush=True)
            except Exception as e:
                failures.append((s, repr(e)))
                print(f"FAIL {a.dataset} s{s}: {e!r}", flush=True)
    if failures:
        print(f"{len(failures)} FAILURES: {failures}", flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
