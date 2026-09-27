"""Dataset access used by the training units (reads only the prepared caches)."""
from __future__ import annotations

import numpy as np

from . import mi, sleep

LABEL_SETS = {
    ("B14", "c4"): ["left_hand", "right_hand", "feet", "tongue"],
    ("B14", "c2"): ["left_hand", "right_hand"],
    ("Lee", "c2"): ["left_hand", "right_hand"],
    ("Sleep", "c5"): sleep.CLASSES,
}
SESSION_ROLES = {  # label-free adaptation / evaluation roles of the target's sessions (nights)
    "B14": {"adapt": "0train", "eval": "1test"},
    "Lee": {"adapt": "0", "eval": "1"},
    "Sleep": {"adapt": "1", "eval": "2"},
}


def all_subjects(ds: str) -> list[int]:
    if ds in mi.SPECS:
        return list(mi.SPECS[ds]["subjects"])
    return sleep.subjects_by_nights()[1]


def target_subjects(ds: str) -> list[int]:
    if ds in mi.SPECS:
        return list(mi.SPECS[ds]["subjects"])
    return sleep.subjects_by_nights()[0]


def load(ds: str, label_set: str, subjects) -> dict:
    """Concatenate the cached trials of `subjects` (kept in the given order)."""
    classes = LABEL_SETS[(ds, label_set)]
    parts = []
    for s in subjects:
        if ds == "Sleep":
            parts.append(sleep.load_subject(int(s)))
        else:
            parts.append(mi.load_subject(ds, int(s), classes=classes))
    out = {}
    for k in ("X", "y", "subject", "session", "run", "phase", "order_in_session", "order_in_run"):
        out[k] = np.concatenate([p[k] for p in parts])
    if ds == "Sleep":
        out["record_index"] = np.concatenate([p["record_index"] for p in parts])
    out["channels"] = parts[0]["channels"]
    out["classes"] = classes
    out["sfreq"] = parts[0]["sfreq"]
    return out


def session_index(ds: str, session: np.ndarray) -> np.ndarray:
    roles = SESSION_ROLES[ds]
    lut = {roles["adapt"]: 0, roles["eval"]: 1}
    return np.array([lut[str(s)] for s in session], dtype=np.int64)
