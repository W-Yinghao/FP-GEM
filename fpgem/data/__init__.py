"""Dataset access used by the training units (reads only the prepared, manifest-verified caches)."""
from __future__ import annotations

import json

import numpy as np

from ..paths import cache_dir
from ..provenance import ProvenanceError, sha256_file
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
META_KEYS = ["y", "y_orig", "in_label_set", "subject", "session", "run", "phase", "order_in_session",
             "order_in_run", "onset_s"]


def all_subjects(ds: str) -> list[int]:
    if ds in mi.SPECS:
        return list(mi.SPECS[ds]["subjects"])
    return sleep.subjects_by_nights()[1]


def target_subjects(ds: str) -> list[int]:
    if ds in mi.SPECS:
        return list(mi.SPECS[ds]["subjects"])
    return sleep.subjects_by_nights()[0]


def cache_files(ds: str, subject: int) -> list[str]:
    if ds == "Sleep":
        return [f"sub{subject:02d}_n{n}.npz" for (s, n) in sorted(sleep.recordings()) if s == subject]
    return [f"sub{subject:02d}.npz"]


def verify_cache(ds: str, subjects) -> dict:
    """sha256 of every cache file of `subjects` must equal the MANIFEST entry. Returns {file: sha}."""
    man_p = cache_dir(ds) / "MANIFEST.json"
    if not man_p.exists():
        raise ProvenanceError(f"missing cache manifest {man_p}")
    man = json.load(open(man_p))
    out = {}
    for s in subjects:
        for name in cache_files(ds, int(s)):
            h = sha256_file(cache_dir(ds) / name)
            if man.get(name) != h:
                raise ProvenanceError(f"{ds}/{name}: sha256 differs from MANIFEST.json")
            out[name] = h
    return out


def load(ds: str, label_set: str, subjects) -> dict:
    """Concatenate all cached trials of `subjects` (kept in the given order). `y` indexes the label set
    (-1 = outside the label set, or unscored sleep epoch); `y_orig` keeps the dataset-level class."""
    classes = LABEL_SETS[(ds, label_set)]
    parts = []
    for s in subjects:
        if ds == "Sleep":
            parts.append(sleep.load_subject(int(s)))
        else:
            parts.append(mi.load_subject(ds, int(s), classes=classes))
    out = {k: np.concatenate([p[k] for p in parts]) for k in ["X"] + META_KEYS}
    if ds == "Sleep":
        out["record_index"] = np.concatenate([p["record_index"] for p in parts])
        out["truncated_night"] = np.concatenate([p["truncated_night"] for p in parts])
    out["channels"] = parts[0]["channels"]
    out["classes"] = classes
    out["sfreq"] = parts[0]["sfreq"]
    return out


def session_index(ds: str, session: np.ndarray) -> np.ndarray:
    roles = SESSION_ROLES[ds]
    lut = {roles["adapt"]: 0, roles["eval"]: 1}
    return np.array([lut[str(s)] for s in session], dtype=np.int64)


def validate_config(cfg: dict) -> None:
    """The frozen config and the constants hard-coded in the data modules must agree (fail loud)."""
    d = cfg["datasets"]
    problems = []
    for key in ("B14", "Lee"):
        c, spec = d[key], mi.SPECS[key]
        if list(c["band_hz"]) != [4.0, 36.0]:
            problems.append(f"{key} band")
        if list(c["cache_window_s"]) != [mi.CACHE_T0, mi.CACHE_T0 + mi.CACHE_N / mi.SFREQ]:
            problems.append(f"{key} cache window")
        if list(c["model_window_s"]) != [0.5, 3.5]:
            problems.append(f"{key} model window")
        if c["moabb"] != spec["moabb"] or c.get("moabb_kwargs", {}) != spec["kwargs"]:
            problems.append(f"{key} moabb dataset/kwargs")
        if c["classes"] != spec["classes"] or c["sfreq"] != mi.SFREQ:
            problems.append(f"{key} classes/sfreq")
        if (c["channels"] or None) != spec["channels"]:
            problems.append(f"{key} channels")
        subs = c["subjects"]
        if subs != "all" and list(subs) != spec["subjects"]:
            problems.append(f"{key} subjects")
        for ls, names in c["label_sets"].items():
            if LABEL_SETS[(key, ls)] != names:
                problems.append(f"{key} label set {ls}")
        if c["sessions"] != SESSION_ROLES[key]:
            problems.append(f"{key} session roles")
    c = d["Sleep"]
    if list(c["band_hz"]) != [0.3, 35.0] or c["sfreq"] != sleep.SFREQ or c["epoch_s"] != sleep.EPOCH_S:
        problems.append("Sleep band/sfreq/epoch")
    if c["channels"] != sleep.CHANNELS or c["classes"] != sleep.CLASSES:
        problems.append("Sleep channels/classes")
    if [sleep.CHANNELS[i] for i in sleep.MODEL_CHANNELS] != c["model_channels"]:
        problems.append("Sleep model channels")
    if {k: str(v) for k, v in c["nights"].items()} != SESSION_ROLES["Sleep"]:
        problems.append("Sleep night roles")
    if problems:
        raise ProvenanceError(f"config/code mismatch: {problems}")
