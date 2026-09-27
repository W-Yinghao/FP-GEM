"""Provenance helpers: git state, code signature, content hashes. Fail loud."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from .paths import REPO


class ProvenanceError(RuntimeError):
    pass


def git_sha(repo: Path = REPO) -> str:
    return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()


def require_clean_git(repo: Path = REPO) -> str:
    """Return HEAD sha; raise if tracked files are modified or untracked files exist under fpgem/."""
    out = subprocess.check_output(
        ["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=all", "--", "fpgem", "scripts", "configs"],
        text=True,
    ).strip()
    if out:
        raise ProvenanceError(f"refusing to run: dirty tree at {git_sha(repo)[:12]}:\n{out}")
    return git_sha(repo)


def code_sig(repo: Path = REPO) -> str:
    """sha256 over the tracked content of fpgem/ + scripts/ + configs/ at HEAD (blob ids, sorted)."""
    ls = subprocess.check_output(
        ["git", "-C", str(repo), "ls-tree", "-r", "HEAD", "--", "fpgem", "scripts", "configs"], text=True
    )
    return hashlib.sha256(ls.encode()).hexdigest()[:16]


def sha256_file(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def sha256_array(*arrays) -> str:
    h = hashlib.sha256()
    for a in arrays:
        h.update(str(a.dtype).encode())
        h.update(str(a.shape).encode())
        h.update(a.tobytes(order="C"))
    return h.hexdigest()


def write_json(path: Path, obj) -> None:
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=str)
    tmp.replace(path)
