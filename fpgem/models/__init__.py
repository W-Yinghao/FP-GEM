"""Backbone builders and feature access for the three W1 backbones."""
from __future__ import annotations

import numpy as np
import torch

from ..vendor.spdnets.models import TSMNet


# ---------------------------------------------------------------- TSMNet (Kobler et al. 2022)
def build_tsmnet(n_classes: int, n_chans: int, n_times: int, domains, device, cfg: dict) -> TSMNet:
    return TSMNet(temporal_filters=cfg["temporal_filters"], spatial_filters=cfg["spatial_filters"],
                  subspacedims=cfg["subspacedims"], temp_cnn_kernel=cfg["temp_cnn_kernel"],
                  bnorm=cfg["bnorm"], bnorm_dispersion="SCALAR", nclasses=n_classes, nchannels=n_chans,
                  nsamples=n_times, domains=torch.as_tensor(sorted(domains), dtype=torch.long),
                  device=torch.device(device))


def group_chunks(n: int, groups, bs: int):
    """Row slices of at most `bs` rows that never cross a group boundary and restart at each group's
    first row, so a subject's features do not depend on which other rows are processed with it."""
    if groups is None:
        starts = [0]
    else:
        g = np.asarray(groups)
        starts = [0] + [int(i) for i in np.flatnonzero(g[1:] != g[:-1]) + 1]
    bounds = starts + [n]
    for a, b in zip(bounds[:-1], bounds[1:]):
        for i in range(a, b, bs):
            yield slice(i, min(i + bs, b))


@torch.no_grad()
def tsmnet_prebn(model: TSMNet, X: np.ndarray, device, bs: int = 256, groups=None) -> torch.Tensor:
    """Pre-BN SPD matrices S (N, d, d) float64 on CPU — identical to the first half of TSMNet.forward.
    Pass `groups` (e.g. subject ids of contiguous rows) to batch every group from its own first row."""
    out = []
    for sl in group_chunks(len(X), groups, bs):
        x = torch.as_tensor(X[sl], dtype=torch.float32, device=device)
        h = model.cnn(x[:, None, ...])
        C = model.cov_pooling(h).to(device=model.spd_device_, dtype=torch.double)
        out.append(model.spdnet(C))
    return torch.cat(out)


@torch.no_grad()
def tsmnet_head(model: TSMNet, S: torch.Tensor, d: torch.Tensor):
    """Domain BN (current test statistics) -> LogEig -> classifier on cached S. Returns (latent, logits)."""
    l = model.spddsbnorm(S, d.to(model.spd_device_))
    z = model.logeig(l)
    return z, model.classifier(z)


@torch.no_grad()
def tsmnet_refit_domain(model: TSMNet, S: torch.Tensor, domain: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Re-centre one domain on its own data (REFIT: Karcher mean + dispersion), like TSMNet's
    domainadapt_finetune, but from cached S. Returns the new (mean, var) test statistics."""
    bnd = model.spddsbnorm.get_domain_obj(torch.tensor(domain))
    bnd.initrunningstats(S)
    return bnd.running_mean_test.detach().clone(), bnd.running_var_test.detach().clone()


# ---------------------------------------------------------------- braindecode backbones
def build_eegnet(n_classes: int, n_chans: int, n_times: int, cfg: dict):
    from braindecode.models import EEGNetv4
    return EEGNetv4(n_chans=n_chans, n_outputs=n_classes, n_times=n_times, F1=cfg["F1"], D=cfg["D"],
                    F2=cfg["F2"], kernel_length=cfg["kernel_length"], drop_prob=cfg["drop_prob"])


def build_chambon(n_classes: int, n_chans: int, sfreq: float, n_times: int, cfg: dict):
    from braindecode.models import SleepStagerChambon2018
    return SleepStagerChambon2018(n_chans=n_chans, sfreq=sfreq, n_outputs=n_classes, n_times=n_times,
                                  n_conv_chs=cfg["n_conv_chs"], dropout=cfg["dropout"])


class FeatureTap:
    """Captures the input of `model.final_layer` (the pre-classifier feature) on every forward."""

    def __init__(self, model):
        self.z = None
        self.h = model.final_layer.register_forward_pre_hook(self._hook)

    def _hook(self, module, inputs):
        self.z = inputs[0]

    def close(self):
        self.h.remove()


@torch.no_grad()
def braindecode_forward(model, X: np.ndarray, device, bs: int = 512, groups=None) -> tuple[np.ndarray, np.ndarray]:
    """Eval-mode (feature, logits) for every row of X. Features are flattened pre-classifier inputs.
    Pass `groups` to batch every group (subject) from its own first row."""
    model.eval()
    tap = FeatureTap(model)
    zs, ls = [], []
    try:
        for sl in group_chunks(len(X), groups, bs):
            x = torch.as_tensor(X[sl], dtype=torch.float32, device=device)
            logits = model(x)
            zs.append(tap.z.flatten(1).float().cpu().numpy())
            ls.append(logits.float().cpu().numpy())
    finally:
        tap.close()
    return np.concatenate(zs), np.concatenate(ls)


@torch.no_grad()
def replay_head(model, z: np.ndarray, backbone: str, device) -> np.ndarray:
    """Re-apply the classifier to dumped features (dump consistency check)."""
    model.eval()
    zt = torch.as_tensor(z, device=device)
    if backbone == "eegnet":
        # final_layer expects [B, F2, 1, T']; reshape from the flattened feature
        w = model.final_layer.conv_classifier.weight
        zt = zt.reshape(len(z), w.shape[1], w.shape[2], w.shape[3])
        return model.final_layer(zt).float().cpu().numpy()
    if backbone == "chambon":
        return model.final_layer(zt).float().cpu().numpy()
    raise ValueError(backbone)


def stabilize_renorm(model, n_chans: int, n_times: int, device, max_iter: int = 5) -> int:
    """EEGNetv4's max-norm conv renormalises weights inside forward(); run eval forwards until the
    state stops changing so that saved weights equal the weights actually used for inference."""
    model.eval()
    x = torch.zeros(2, n_chans, n_times, device=device)
    prev = None
    for it in range(max_iter):
        with torch.no_grad():
            model(x)
        cur = torch.cat([p.detach().flatten().cpu() for p in model.parameters()])
        if prev is not None and torch.equal(prev, cur):
            return it
        prev = cur
    raise RuntimeError("EEGNet renorm did not stabilise")
