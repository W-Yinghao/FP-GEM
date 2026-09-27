# W1 — Source retraining and per-trial dumps (FROZEN)

Status: FROZEN at the commit that adds this file. Config: `configs/w1.yaml` (same commit).
Date: 2026-09-27. Owner decision (2026-09-27): the project restarts from scratch; numbers from the
AAAI submission and from earlier runs are not reused, compared against, or targeted.

## 1. Purpose

W1 produces the frozen source models and complete per-trial feature dumps that every later wave
(adaptation operators, prior–geometry identification studies, protocol-design studies) consumes.
W1 tests **no scientific hypothesis**. It must not be tuned on target data.

## 2. Datasets and label-free roles

| Dataset | Classes | Subjects | Adaptation batch (unlabeled) | Evaluation data |
|---|---|---|---|---|
| BNCI2014_001 (B14), 4-class | L, R, feet, tongue | 9 | session `0train` (all 6 runs) | session `1test` |
| BNCI2014_001 (B14), 2-class | L, R | 9 | session `0train` | session `1test` |
| Lee2019_MI | L, R | 54 | session 1 (offline + online phase) | session 2 |
| Sleep-EDF SC | W, N1, N2, N3, REM | 78 (75 paired targets) | night 1, window [lights-off, +9 h), all epochs | night 2, same window, scored epochs only |

- The adaptation/evaluation assignment uses only session/night identity and acquisition metadata
  (lights-off time). No target label is used to build any batch, crop, or split.
- Sleep subjects with one night (13, 36, 52) are used only as source subjects.
- Cho2017 is excluded from W1: MOABB returns its trials class-stacked (chronology lost) and it has a
  single session, so no label-free chronological adaptation/evaluation split exists.

## 3. Preprocessing (identical for every unit)

- MI: MOABB 1.2 `MotorImagery`, IIR band-pass 4–36 Hz on the continuous signal, epochs −2.0 to 4.0 s
  around the cue (cached, 1500 samples at 250 Hz; Lee resampled from 1000 Hz), models see 0.5–3.5 s
  (750 samples). µV units. No per-trial normalization.
- Lee channels: the 20 sensorimotor channels of Lee et al. (2019). B14: all 22 EEG channels.
- Sleep: EEG Fpz-Cz, EEG Pz-Oz (+ EOG horizontal cached for later waves), 100 Hz, FIR band-pass
  0.3–35 Hz on the continuous signal, 30-s epochs on the EDF record grid, stages 3+4 → N3,
  `Sleep stage ?`/`Movement time` → label −1 (kept in the adaptation night, excluded from training
  and from scoring). No per-epoch normalization.
- EEGNet/Chambon inputs: per-channel standardization with mean/std computed on the unit's
  source-train subjects only, stored with the checkpoint. TSMNet: µV input, no standardization.

## 4. Backbones and training

- TSMNet (Kobler et al. 2022; BSD-3, vendored) with domain-specific SPD batch norm (SCALAR
  dispersion), domains = subject × session; RiemannianAdam lr 1e-3, wd 1e-4; batches of 5 domains ×
  10 trials; momentum BN scheduler (τ0 = 0.85).
- EEGNetv4 (braindecode 0.8), AdamW lr 1e-3, wd 1e-4, batch 64.
- SleepStagerChambon2018 (braindecode 0.8), AdamW lr 1e-3, wd 1e-4, batch 128, class-weighted CE.
- Leave-one-subject-out. Validation = 20% of the source subjects (participant-level, drawn with
  `rng([seed, target])`). TSMNet validation domains are re-centred on their own unlabeled data before
  the validation loss is computed (these are source subjects).
- Max 100 epochs, min 30, early stopping patience 20 on validation loss; the best-validation-loss
  weights are restored. Seeds 0, 1, 2. Deterministic CUDA settings; GPU model recorded per unit.

Units: B14-c4 and B14-c2 × {TSMNet, EEGNet} × 9 targets × 3 seeds = 108; Lee × {TSMNet, EEGNet} ×
54 × 3 = 324; Sleep × Chambon × 75 × 3 = 225. **Total 657.**

## 5. Dumps (per unit)

- `ckpt.pt` (state dict), `model_spec.json` (constructor arguments, domain map), `norm.npz`.
- `split.json`: target, source-train subjects, validation subjects, session/night roles.
- `dump_target.npz` and `dump_source.npz`: every trial of the target (both sessions/nights) and of
  every source subject, with metadata (subject, session/night, run/phase, chronological index,
  label, onset) and:
  - EEGNet/Chambon: pre-classifier features and logits under the source (eval-mode) network.
  - TSMNet: pre-BN SPD matrices (float64), so every SPD normalization / re-centering / SPDIM
    variant can be recomputed exactly on CPU; plus per-domain Karcher means/dispersions of the
    source domains, and features/logits of source trials under their own domain statistics.
- `metrics.json`: training curve, best epoch, validation loss/bAcc, and descriptive sanity metrics
  on the target evaluation data (Section 7). `DONE.json` is written last, atomically.

## 6. QC gates

Probe (before the fleet; one unit each of B14-c4 TSMNet, B14-c4 EEGNet, Lee TSMNet, Sleep Chambon):
1. Runs end-to-end on GPU under deterministic settings without errors.
2. Leakage invariants hold: the target subject is absent from source-train and validation sets; the
   split manifest matches the data actually loaded; no target signal or label enters training or
   model selection (target labels are only copied into the dump metadata for later scoring).
3. Dump completeness: row counts equal the cached trial counts; the classifier replayed on dumped
   features reproduces dumped logits (max abs diff ≤ 1e-5).
4. Self-replay: re-running inference from `ckpt.pt` reproduces `dump_target.npz` features bit-exactly
   on the same GPU type.
5. Sanity: validation bAcc above chance (B14-c4 > 0.25, 2-class > 0.5, Sleep > 0.2).

Fleet: every unit must pass gates 2–3 in-process (it fails loud otherwise). Units that fail are
reason-coded, retried at most 3 times, then reported; they are never silently dropped.

## 7. What W1 reports (descriptive only)

Per dataset × backbone: source-only balanced accuracy on the evaluation data (EEGNet/Chambon: plain
eval-mode network; TSMNet: target session re-centred on its own unlabeled data, i.e. the standard
TSMNet inference, labeled as such), validation metrics, best epochs, runtime, GPU type. These are
sanity numbers for the source models, **not** endpoints and not method comparisons.

## 8. Forbidden

- Any use of target labels before evaluation; any target-driven hyperparameter change.
- Changing preprocessing, splits, or training settings after seeing any target evaluation number
  (engineering fixes discovered in the probe are allowed, documented in an appendum before the fleet).
- Reusing, targeting, or comparing to numbers from the AAAI submission or earlier project runs.
