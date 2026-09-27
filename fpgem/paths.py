"""Filesystem layout. All large outputs live OUTSIDE the git repo.

Override with environment variables:
  FPGEM_STORE   root for caches and runs      (default /home/infres/yinwang/fpgem_store)
  FPGEM_RAW     datalake raw root             (default /projects/EEG-foundation-model/datalake/raw)
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STORE = Path(os.environ.get("FPGEM_STORE", "/home/infres/yinwang/fpgem_store"))
RAW = Path(os.environ.get("FPGEM_RAW", "/projects/EEG-foundation-model/datalake/raw"))

CACHE = STORE / "cache"      # preprocessed epochs, one npz per (dataset, subject)
RUNS = STORE / "runs"        # one directory per training unit
LOGS = STORE / "logs"        # SLURM stdout/stderr
CONTROL = STORE / "control"  # STOP flag, driver state


def cache_dir(dataset: str) -> Path:
    return CACHE / dataset


def unit_dir(wave: str, unit_id: str) -> Path:
    return RUNS / wave / unit_id
