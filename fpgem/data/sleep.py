"""Sleep-EDF (sleep-cassette) caches with a label-free crop.

Every recording is cropped to [LightsOff, LightsOff + 9 h) using only the lights-off clock time from
PhysioNet's SC-subjects.xls (copied to `sc_subjects.csv`) and the EDF start time. The hypnogram is read
only to attach labels to the already-chosen epochs. The same rule is applied to source nights, the
adaptation night and the evaluation night.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np

from ..paths import RAW, cache_dir

SC_DIR = RAW / "sleep-edf" / "sleep-cassette"
LIGHTS_OFF_CSV = Path(__file__).with_name("sc_subjects.csv")
CHANNELS = ["EEG Fpz-Cz", "EEG Pz-Oz", "EOG horizontal"]
MODEL_CHANNELS = [0, 1]           # indices into CHANNELS used by the models
SFREQ = 100
EPOCH_S = 30
EPOCH_N = SFREQ * EPOCH_S
WINDOW_EPOCHS = 9 * 120           # 9 h of 30-s epochs
CLASSES = ["W", "N1", "N2", "N3", "REM"]
DESC2Y = {"Sleep stage W": 0, "Sleep stage 1": 1, "Sleep stage 2": 2, "Sleep stage 3": 3,
          "Sleep stage 4": 3, "Sleep stage R": 4, "Sleep stage ?": -1, "Movement time": -1}


def recordings() -> dict[tuple[int, int], tuple[Path, Path]]:
    """{(subject, night): (psg, hypnogram)} for every sleep-cassette recording."""
    out = {}
    for psg in sorted(SC_DIR.glob("SC4*-PSG.edf")):
        m = re.fullmatch(r"SC4(\d\d)(\d)[A-Z]0-PSG\.edf", psg.name)
        if m is None:
            raise RuntimeError(f"unexpected PSG file name {psg.name}")
        subj, night = int(m.group(1)), int(m.group(2))
        hyps = sorted(SC_DIR.glob(f"SC4{m.group(1)}{m.group(2)}??-Hypnogram.edf"))
        if len(hyps) != 1:
            raise RuntimeError(f"{psg.name}: {len(hyps)} hypnograms")
        out[(subj, night)] = (psg, hyps[0])
    return out


def subjects_by_nights() -> tuple[list[int], list[int]]:
    """(paired subjects with nights 1 and 2, all subjects)."""
    recs = recordings()
    subs = sorted({s for s, _ in recs})
    paired = [s for s in subs if (s, 1) in recs and (s, 2) in recs]
    return paired, subs


def _lights_off() -> dict[tuple[int, int], int]:
    out = {}
    with open(LIGHTS_OFF_CSV) as f:
        for row in csv.DictReader(f):
            h, m, s = (int(v) for v in row["LightsOff"].split(":"))
            out[(int(row["subject"]), int(row["night"]))] = h * 3600 + m * 60 + s
    return out


def _edf_start_clock(psg: Path) -> int:
    with open(psg, "rb") as f:
        hdr = f.read(256)
    hh, mm, ss = (int(v) for v in hdr[176:184].decode("ascii").split("."))
    return hh * 3600 + mm * 60 + ss


def build_recording(subject: int, night: int, out: Path | None = None) -> Path:
    import mne

    psg, hyp = recordings()[(subject, night)]
    raw = mne.io.read_raw_edf(psg, include=CHANNELS, preload=True, verbose="ERROR")
    if raw.ch_names != CHANNELS:
        raw.reorder_channels(CHANNELS)
    if abs(raw.info["sfreq"] - SFREQ) > 1e-6:
        raise RuntimeError(f"{psg.name}: sfreq {raw.info['sfreq']}")
    raw.filter(0.3, 35.0, picks="all", verbose="ERROR")          # FIR (firwin), zero-phase, continuous signal
    data = raw.get_data() * 1e6                                   # µV
    n_records = data.shape[1] // EPOCH_N

    lo_s = (_lights_off()[(subject, night)] - _edf_start_clock(psg)) % 86400
    if lo_s % EPOCH_S:
        raise RuntimeError(f"{psg.name}: lights-off not on the 30-s grid ({lo_s} s)")
    i0 = lo_s // EPOCH_S
    i1 = min(n_records, i0 + WINDOW_EPOCHS)
    if i1 <= i0:
        raise RuntimeError(f"{psg.name}: empty window")

    # labels for every record from the hypnogram (onsets relative to PSG start, multiples of 30 s)
    lab = np.full(n_records, -1, dtype=np.int16)
    ann = mne.read_annotations(hyp)
    for onset, dur, desc in zip(ann.onset, ann.duration, ann.description):
        if desc not in DESC2Y:
            raise RuntimeError(f"{hyp.name}: unknown annotation {desc!r}")
        a, b = int(round(onset / EPOCH_S)), int(round((onset + dur) / EPOCH_S))
        lab[max(a, 0):min(b, n_records)] = DESC2Y[desc]

    idx = np.arange(i0, i1)
    X = np.stack([data[:, i * EPOCH_N:(i + 1) * EPOCH_N] for i in idx]).astype(np.float32)
    if not np.isfinite(X).all():
        raise RuntimeError(f"{psg.name}: non-finite samples")
    out = out or cache_dir("Sleep") / f"sub{subject:02d}_n{night}.npz"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.stem + ".tmp.npz")
    np.savez(tmp, X=X, y=lab[idx], record_index=idx.astype(np.int32),
             order_in_session=np.arange(len(idx), dtype=np.int32),
             subject=np.full(len(idx), subject, dtype=np.int16), night=np.full(len(idx), night, dtype=np.int8),
             lights_off_record=np.int32(i0), n_records=np.int32(n_records), truncated=np.bool_(i1 - i0 < WINDOW_EPOCHS),
             sfreq=np.float32(SFREQ), channels=np.array(CHANNELS), classes=np.array(CLASSES),
             psg=np.array(psg.name), hypnogram=np.array(hyp.name))
    tmp.replace(out)
    return out


def load_subject(subject: int, nights=(1, 2), channels=MODEL_CHANNELS) -> dict:
    parts = []
    for n in nights:
        p = cache_dir("Sleep") / f"sub{subject:02d}_n{n}.npz"
        if p.exists():
            parts.append(np.load(p, allow_pickle=False))
    if not parts:
        raise FileNotFoundError(f"Sleep subject {subject}: no cached nights")
    cat = lambda k: np.concatenate([z[k] for z in parts])
    return dict(
        X=np.ascontiguousarray(np.concatenate([z["X"][:, channels] for z in parts])),
        y=cat("y").astype(np.int64),
        subject=cat("subject").astype(np.int64),
        session=np.array([str(int(v)) for v in cat("night")]),
        run=np.array([str(int(v)) for v in cat("night")]),
        phase=np.array(["night"] * sum(len(z["y"]) for z in parts)),
        order_in_session=cat("order_in_session"),
        order_in_run=cat("order_in_session"),
        record_index=cat("record_index"),
        channels=[CHANNELS[c] for c in channels],
        classes=CLASSES,
        sfreq=float(SFREQ),
    )


def write_manifest() -> Path:
    from ..provenance import sha256_file
    d = cache_dir("Sleep")
    man = {f.name: sha256_file(f) for f in sorted(d.glob("sub*_n*.npz")) if not f.name.endswith(".tmp.npz")}
    p = d / "MANIFEST.json"
    with open(p, "w") as f:
        json.dump(man, f, indent=1, sort_keys=True)
    return p
