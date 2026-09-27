"""Motor-imagery caches (BNCI2014_001, Lee2019_MI) built from the offline datalake with MOABB.

One npz per subject with the wide epoch window (cue −2 s … +4 s, 1500 samples at 250 Hz), all classes of
the dataset, every session/run, in chronological order within each session. Label-set restriction and the
model window are applied at load time, so every backbone and label set reads the same cached signal.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np

from ..paths import RAW, cache_dir

CACHE_T0 = -2.0          # seconds relative to cue of cached sample 0
CACHE_N = 1500           # cached samples (6.0 s at 250 Hz)
SFREQ = 250

LEE20 = ["FC5", "FC3", "FC1", "FC2", "FC4", "FC6", "C5", "C3", "C1", "Cz", "C2", "C4", "C6",
         "CP5", "CP3", "CP1", "CPz", "CP2", "CP4", "CP6"]

SPECS = {
    "B14": dict(moabb="BNCI2014_001", classes=["left_hand", "right_hand", "feet", "tongue"],
                channels=None, subjects=list(range(1, 10)), resample=None, kwargs={}),
    "Lee": dict(moabb="Lee2019_MI", classes=["left_hand", "right_hand"],
                channels=LEE20, subjects=list(range(1, 55)), resample=SFREQ,
                kwargs=dict(train_run=True, test_run=True)),
}


def configure_offline() -> None:
    """Point MNE/MOABB at the read-only datalake. Must run before importing moabb datasets.

    The per-job fake home (set by the sbatch script) keeps MOABB from writing into the shared
    ~/.mne/mne-python.json. Nothing from the MNE config is ever recorded in provenance files.
    """
    dl = str(RAW)
    for k in ("MNE_DATA", "MNE_DATASETS_BNCI_PATH", "MNE_DATASETS_GIGADB_PATH", "MNE_DATASETS_LEE2019-MI_PATH"):
        os.environ[k] = dl


def _dataset(key: str):
    configure_offline()
    import moabb.datasets as mds
    spec = SPECS[key]
    return getattr(mds, spec["moabb"])(**spec["kwargs"])


def _check_files(key: str, subject: int) -> None:
    if key == "B14":
        for s in "TE":
            p = RAW / f"MNE-bnci-data/database/data-sets/001-2014/A{subject:02d}{s}.mat"
            if not p.exists():
                raise FileNotFoundError(p)
    elif key == "Lee":
        for k in (1, 2):
            p = (RAW / "MNE-lee2019-mi-data/gigadb-datasets/live/pub/10.5524/100001_101000/100542"
                 / f"session{k}/s{subject}/sess{k:02d}_subj{subject:02d}_EEG_MI.mat")
            if not p.exists():
                raise FileNotFoundError(p)


def build_subject(key: str, subject: int, out: Path | None = None) -> Path:
    """Build and write the cache npz for one subject. Returns the path."""
    from moabb.paradigms import MotorImagery

    spec = SPECS[key]
    _check_files(key, subject)
    ds = _dataset(key)
    paradigm = MotorImagery(n_classes=len(spec["classes"]), events=spec["classes"], fmin=4.0, fmax=36.0,
                            tmin=CACHE_T0, tmax=CACHE_T0 + CACHE_N / SFREQ, channels=spec["channels"],
                            resample=spec["resample"])
    X, y, meta = paradigm.get_data(ds, subjects=[subject], return_epochs=False)
    if X.shape[-1] < CACHE_N:
        raise RuntimeError(f"{key} s{subject}: only {X.shape[-1]} samples, need {CACHE_N}")
    X = np.ascontiguousarray(X[..., :CACHE_N], dtype=np.float32)          # µV (MOABB unit_factor 1e6)
    if not np.isfinite(X).all():
        raise RuntimeError(f"{key} s{subject}: non-finite samples")
    cls = {c: i for i, c in enumerate(spec["classes"])}
    yi = np.array([cls[v] for v in y], dtype=np.int16)
    session = meta["session"].astype(str).to_numpy()
    run = meta["run"].astype(str).to_numpy()
    if not (meta["subject"].to_numpy() == subject).all():
        raise RuntimeError("MOABB returned another subject")
    # chronological indices: MOABB orders session -> run (insertion order) -> events in time
    order_in_session = np.zeros(len(yi), dtype=np.int32)
    order_in_run = np.zeros(len(yi), dtype=np.int32)
    for s in np.unique(session):
        m = np.flatnonzero(session == s)
        order_in_session[m] = np.arange(len(m))
        for r in np.unique(run[m]):
            mr = m[run[m] == r]
            order_in_run[mr] = np.arange(len(mr))
    phase = np.array(["online" if "test" in r else "offline" for r in run]) if key == "Lee" else np.array(["offline"] * len(run))
    ch_names = spec["channels"] or list(ds_channel_names(ds, subject))
    if X.shape[1] != len(ch_names):
        raise RuntimeError(f"channel count {X.shape[1]} != {len(ch_names)}")

    out = out or cache_dir(key) / f"sub{subject:02d}.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".tmp.npz")
    np.savez(tmp, X=X, y=yi, session=session, run=run, phase=phase, order_in_session=order_in_session,
             order_in_run=order_in_run, subject=np.full(len(yi), subject, dtype=np.int16),
             sfreq=np.float32(SFREQ), t0=np.float32(CACHE_T0), channels=np.array(ch_names),
             classes=np.array(spec["classes"]))
    tmp.replace(out)
    return out


def ds_channel_names(ds, subject: int) -> list[str]:
    """EEG channel names in MOABB paradigm order (used only when `channels=None`)."""
    raws = ds.get_data(subjects=[subject])[subject]
    raw = next(iter(next(iter(raws.values())).values()))
    import mne
    picks = mne.pick_types(raw.info, eeg=True, stim=False, eog=False, emg=False)
    return [raw.ch_names[i] for i in picks]


def load_subject(key: str, subject: int, classes: list[str] | None = None, window_s=(0.5, 3.5)) -> dict:
    """Load one cached subject restricted to `classes` (re-indexed 0..K-1) and cropped to `window_s`."""
    z = np.load(cache_dir(key) / f"sub{subject:02d}.npz", allow_pickle=False)
    all_classes = list(z["classes"])
    classes = classes or all_classes
    keep = np.isin(z["y"], [all_classes.index(c) for c in classes])
    remap = {all_classes.index(c): i for i, c in enumerate(classes)}
    i0 = int(round((window_s[0] - float(z["t0"])) * float(z["sfreq"])))
    i1 = i0 + int(round((window_s[1] - window_s[0]) * float(z["sfreq"])))
    out = dict(
        X=np.ascontiguousarray(z["X"][keep][..., i0:i1]),
        y=np.array([remap[v] for v in z["y"][keep]], dtype=np.int64),
        subject=z["subject"][keep].astype(np.int64),
        session=z["session"][keep],
        run=z["run"][keep],
        phase=z["phase"][keep],
        order_in_session=z["order_in_session"][keep],
        order_in_run=z["order_in_run"][keep],
        channels=list(z["channels"]),
        classes=classes,
        sfreq=float(z["sfreq"]),
    )
    return out


def write_manifest(key: str) -> Path:
    from ..provenance import sha256_file
    d = cache_dir(key)
    files = sorted(d.glob("sub*.npz"))
    man = {f.name: sha256_file(f) for f in files if not f.name.endswith(".tmp.npz")}
    p = d / "MANIFEST.json"
    with open(p, "w") as f:
        json.dump(man, f, indent=1, sort_keys=True)
    return p
