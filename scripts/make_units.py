"""Write the canonical W1 unit list (one unit id per line) to configs/units_W1.txt."""
from __future__ import annotations

import sys

from fpgem.paths import REPO
from fpgem.train.source import enumerate_units, load_cfg


def main():
    cfg = load_cfg()
    units = enumerate_units(cfg)
    ids = [u.uid for u in units]
    if len(ids) != len(set(ids)):
        raise RuntimeError("duplicate unit ids")
    # schedule long units first so the tail of the fleet is short
    order = {"Lee": 0, "Sleep": 1, "B14": 2}
    ids.sort(key=lambda s: (order[s.split("-")[0]], s))
    p = REPO / "configs" / "units_W1.txt"
    p.write_text("\n".join(ids) + "\n")
    from collections import Counter
    c = Counter("-".join(i.split("-")[:3]) for i in ids)
    print(len(ids), dict(c))
    return 0


if __name__ == "__main__":
    sys.exit(main())
