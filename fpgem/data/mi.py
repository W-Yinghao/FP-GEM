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


EXPECTED = {  # trials per subject per session per class (protocol cue schedule); fail loud otherwise
    "B14": 72,
    "Lee": 100,   # 50 offline + 50 online per class and session
}


def _run_events(ds, subject: int) -> tuple[dict, list[str]]:
    """Cue onsets (s from run start) and class names for every (session, run), read from the raw stim
    channel, plus the EEG channel names in MOABB order."""
    import mne
    raws = ds.get_data(subjects=[subject])[subject]
    inv = {v: k for k, v in ds.event_id.items()}
    out, ch_names = {}, None
    for sess, runs in raws.items():
        for run, raw in runs.items():
            ev = mne.find_events(raw, shortest_event=0, verbose=False)
            ev = ev[np.isin(ev[:, 2], list(ds.event_id.values()))]
            onset = (ev[:, 0] - raw.first_samp) / raw.info["sfreq"] + ds.interval[0]
            out[(str(sess), str(run))] = (onset, [inv[c] for c in ev[:, 2]])
            if ch_names is None:
                picks = mne.pick_types(raw.info, eeg=True, stim=False, eog=False, emg=False)
                ch_names = [raw.ch_names[i] for i in picks]
    return out, ch_names


def build_subject(key: str, subject: int, out: Path | None = None) -> Path:
    """Build and write the cache npz for one subject. Returns the path."""
    import mne
    import moabb
    import scipy
    from moabb.paradigms import MotorImagery

    from ..provenance import git_sha

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
    session = meta["session"].astype(str).to_numpy().astype("U")   # fixed-width unicode: loadable without pickle
    run = meta["run"].astype(str).to_numpy().astype("U")
    if not (meta["subject"].to_numpy() == subject).all():
        raise RuntimeError("MOABB returned another subject")
    # expected protocol counts (no silent epoch drops)
    for s in np.unique(session):
        cnt = np.bincount(yi[session == s], minlength=len(spec["classes"]))
        if not np.all(cnt == EXPECTED[key]):
            raise RuntimeError(f"{key} s{subject} session {s}: class counts {cnt.tolist()} != {EXPECTED[key]}")
    if len(np.unique(session)) != 2:
        raise RuntimeError(f"{key} s{subject}: sessions {np.unique(session)}")
    # chronological indices + cue onsets; MOABB orders session -> run (insertion order) -> events in time
    events, raw_ch = _run_events(ds, subject)
    order_in_session = np.zeros(len(yi), dtype=np.int32)
    order_in_run = np.zeros(len(yi), dtype=np.int32)
    onset = np.zeros(len(yi), dtype=np.float64)
    for s in np.unique(session):
        m = np.flatnonzero(session == s)
        order_in_session[m] = np.arange(len(m))
        for r in np.unique(run[m]):
            mr = m[run[m] == r]
            order_in_run[mr] = np.arange(len(mr))
            ons, names = events[(str(s), str(r))]
            names_cached = [spec["classes"][v] for v in yi[mr]]
            if names != names_cached:                                    # alignment check: same labels, same order
                raise RuntimeError(f"{key} s{subject} {s}/{r}: raw event sequence does not match the epochs")
            onset[mr] = ons
    phase = np.array(["online" if "test" in r else "offline" for r in run]) if key == "Lee" else np.array(["offline"] * len(run))
    ch_names = spec["channels"] or raw_ch
    if X.shape[1] != len(ch_names):
        raise RuntimeError(f"channel count {X.shape[1]} != {len(ch_names)}")

    out = out or cache_dir(key) / f"sub{subject:02d}.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(f"{out.stem}.{os.getpid()}.tmp.npz")          # unique per writer
    for k, v in dict(session=session, run=run, phase=phase).items():
        if v.dtype.kind != "U":
            raise RuntimeError(f"{k} has dtype {v.dtype}; must be unicode")
    build = json.dumps(dict(git_sha=git_sha(), moabb=moabb.__version__, mne=mne.__version__, numpy=np.__version__,
                            scipy=scipy.__version__, band_hz=[4.0, 36.0], window_s=[CACHE_T0, CACHE_T0 + CACHE_N / SFREQ],
                            resample=spec["resample"]), sort_keys=True)
    np.savez(tmp, X=X, y=yi, session=session, run=run, phase=phase, order_in_session=order_in_session,
             order_in_run=order_in_run, onset_s=onset, subject=np.full(len(yi), subject, dtype=np.int16),
             sfreq=np.float32(SFREQ), t0=np.float32(CACHE_T0), channels=np.array(ch_names),
             classes=np.array(spec["classes"]), build=np.array(build))
    tmp.replace(out)
    return out


def load_subject(key: str, subject: int, classes: list[str] | None = None, window_s=(0.5, 3.5)) -> dict:
    """Load one cached subject cropped to `window_s`. All trials are returned; `y` is the index in
    `classes` (or -1 for trials outside the label set), `y_orig` the dataset-level class index."""
    z = np.load(cache_dir(key) / f"sub{subject:02d}.npz", allow_pickle=False)
    all_classes = list(z["classes"])
    classes = classes or all_classes
    remap = {all_classes.index(c): i for i, c in enumerate(classes)}
    i0 = int(round((window_s[0] - float(z["t0"])) * float(z["sfreq"])))
    i1 = i0 + int(round((window_s[1] - window_s[0]) * float(z["sfreq"])))
    y = np.array([remap.get(int(v), -1) for v in z["y"]], dtype=np.int64)
    out = dict(
        X=np.ascontiguousarray(z["X"][..., i0:i1]),
        y=y,
        y_orig=z["y"].astype(np.int64),
        in_label_set=y >= 0,
        subject=z["subject"].astype(np.int64),
        session=z["session"],
        run=z["run"],
        phase=z["phase"],
        order_in_session=z["order_in_session"],
        order_in_run=z["order_in_run"],
        onset_s=z["onset_s"],
        channels=list(z["channels"]),
        classes=classes,
        sfreq=float(z["sfreq"]),
    )
    return out


def write_manifest(key: str) -> Path:
    """Hash every cache file; refuse unless the file set is exactly the expected subject set."""
    from ..provenance import sha256_file
    d = cache_dir(key)
    if list(d.glob("*.tmp.npz")):
        raise RuntimeError(f"{d}: temporary files present; a builder is still running")
    files = sorted(d.glob("sub*.npz"))
    expected = {f"sub{s:02d}.npz" for s in SPECS[key]["subjects"]}
    if {f.name for f in files} != expected:
        raise RuntimeError(f"{key} cache incomplete: missing {sorted(expected - {f.name for f in files})}")
    man = {f.name: sha256_file(f) for f in files}
    p = d / "MANIFEST.json"
    with open(p, "w") as f:
        json.dump(man, f, indent=1, sort_keys=True)
    return p
