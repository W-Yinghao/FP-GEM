"""Load a finished W1 unit and expose features + the unit's own classifier head on CPU (W2 pre-reg §0)."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch

from ..paths import RUNS
from ..train.source import Unit, rebuild
from ..vendor.spdnets import functionals as spdf


class UnitView:
    def __init__(self, uid: str, wave: str = "W1"):
        self.u = Unit.parse(uid)
        self.d = RUNS / wave / uid
        self.spec = json.load(open(self.d / "model_spec.json"))
        self.kind = self.spec["kind"]
        self.K = self.spec["n_classes"]
        self.model = rebuild(self.spec, torch.device("cpu"))
        self.model.load_state_dict(torch.load(self.d / "ckpt.pt", map_location="cpu", weights_only=True))
        self.model.eval()
        self.src = dict(np.load(self.d / "dump_source.npz", allow_pickle=False))
        self.tgt = dict(np.load(self.d / "dump_target.npz", allow_pickle=False))
        if self.kind == "tsmnet":
            self._ref_dom = int(self.tgt["domain"][0])          # any domain slot; its stats are overwritten per call
            tr = self.src["role"] == "train"
            M, v = self.karcher(self.src["S"][tr])
            self.src_ref = (M, v)

    # ---------------------------------------------------------------- TSMNet helpers
    @staticmethod
    def karcher(S: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        St = torch.as_tensor(S, dtype=torch.float64)
        M, dist = spdf.spd_mean_kracher_flow(St, dim=0, return_dist=True)
        v = dist.square().mean(dim=0, keepdim=True).clamp(min=spdf.EPS[St.dtype])
        return M.numpy(), v.reshape(-1).numpy()

    @torch.no_grad()
    def tsm_features(self, S: np.ndarray, ref: tuple) -> np.ndarray:
        """LogEig of S re-centred (and dispersion-rescaled, TSMNet convention) at reference (M, v)."""
        bn = self.model.spddsbnorm
        bnd = bn.get_domain_obj(torch.tensor(self._ref_dom))
        bnd.running_mean_test.data = torch.as_tensor(ref[0]).reshape(1, *ref[0].shape[-2:]).clone()
        bnd.running_var_test = torch.as_tensor(ref[1]).reshape(1, 1).clone()
        St = torch.as_tensor(S, dtype=torch.float64)
        d = torch.full((len(St),), self._ref_dom, dtype=torch.long)
        return self.model.logeig(bn(St, d)).numpy()

    # ---------------------------------------------------------------- generic
    def features(self, part: str, rows=None, ref=None) -> np.ndarray:
        D = self.src if part == "src" else self.tgt
        idx = slice(None) if rows is None else rows
        if self.kind == "tsmnet":
            return self.tsm_features(D["S"][idx], self.src_ref if ref is None else ref)
        return D["z"][idx].astype(np.float64)

    @torch.no_grad()
    def head(self, z: np.ndarray) -> np.ndarray:
        zt = torch.as_tensor(z)
        if self.kind == "tsmnet":
            return self.model.classifier(zt.double()).numpy()
        if self.kind == "eegnet":
            w = self.model.final_layer.conv_classifier.weight
            return self.model.final_layer(zt.float().reshape(len(z), w.shape[1], w.shape[2], w.shape[3])).double().numpy()
        return self.model.final_layer(zt.float()).double().numpy()


def balanced_accuracy(y: np.ndarray, pred: np.ndarray, K: int) -> float:
    rec = [np.mean(pred[y == k] == k) for k in range(K) if np.any(y == k)]
    return float(np.mean(rec))
