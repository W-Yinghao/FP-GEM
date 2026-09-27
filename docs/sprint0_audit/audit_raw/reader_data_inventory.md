# Sprint-0 T3/T4 read-only scout: FP-GEM data, artifacts and operator rerun feasibility

I did not modify, move or check out anything, did not submit jobs and did not train. I only read files, plus a few small Python reads. I wrote draft tables to the scratchpad only (paths at the end).

## 0. Verdict

- **T4 is feasible for Sleep-EDF, B14 2-class, Cho2017 and Lee2019.**
  - Raw signal for all four datasets is on the datalake.
  - The frozen source models exist on disk: 345 TSMNet checkpoints for the MI datasets and 225 EEGNet bundles for Sleep.
  - Source training excludes the whole target subject, so any new adaptation/evaluation split can reuse these models without retraining.
  - **B14 4-class is not feasible from what exists.** There are no 4-class checkpoints or loaders in any h2cmi branch, so it needs retraining (27 units).
- **No saved output contains the learned features (embeddings).** Every latent, SPD or signal-level operator needs the model re-run on the data. That re-run is cheap and already proven to reproduce: P13 matched P12 hash-for-hash on Lee, and my recomputation from the Stage-2 logit dumps gives exactly the P12 numbers (B14 FP 0.7124, Joint 0.7094, Recenter base 0.7274; Lee FP 0.6656).
- **T3, MI datasets:** in every P12 unit ρ_A = ρ_E = (0.5, 0.5) exactly. This is by construction: the adaptation/evaluation split is built from target labels (class-stratified halves of session 0), and the pipeline rejects no trials. So the current MI artifacts show no gap between protocol and observed proportions. The only real sources of a gap are rejection flags the pipeline ignores (B14 expert artifact flags, Cho `bad_trial_indices`).
- **T3, Sleep:** the prior shift is natural and large. The median distance between ρ_A and ρ_E is 0.139 (total variation). 9 of 75 subjects have zero N3 epochs in the adaptation night.

## 1. Paper vs on-disk artifacts (hand-off to T1; please verify, do not assume)

**Code involved:**
- `origin/exp/h2cmi-wave0-mechanism` @ df47753e
- `origin/agent/fp-gem-stage2` @ 04a40e4e, cloned at `/home/infres/yinwang/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8`
- P12 launch commit e6c49156
- REVIEW_P0 on `exp/h2cmi-review-p0-corrections` @ 5bc9bf07
- The data loaders are identical across these branches.

| Table 1 cell | On-disk source | Match? |
|---|---|---|
| **Sleep** row (Source 65.7, EA 65.3, Diag-IM 63.6, Joint 63.7, FP 65.6) | `/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/results/h2cmi/p0_w2_primary_all.jsonl` (EEGNet, 75 subjects × 3 seeds) | Exact. The same file also has `fixed_reference_oneshot_uniform` 69.5 and `pooled_uniform` 66.0, which are not in the paper. |
| **MI** Source, EA, Recenter, SPDIM | P12 `fp_gem_results.csv` (sha f3e4ca69…), `~/.cache/h2cmi_training_caches/fp_gem_{ea,cho}` | Match |
| **MI** Joint-GEM | Artifacts: B14 70.9, Cho 59.2, Lee 66.3 | B14 does **not** match (paper 71.9) |
| **MI** FP-GEM | Artifacts: B14 71.2, Cho 59.0, Lee 66.6 (P12, and confirmed by the regime re-run) | **None match** (paper 73.2 / 60.0 / 67.6). I did not find these values in any artifact I searched. |

**Where the paper's description and the code disagree, on points that matter for T3/T4:**
- **MI split.** The paper says an earlier session adapts and a later session evaluates. The code uses session 0 only, split into class-stratified halves using target labels (`h2cmi/w1_repaired_split.py` L80-96).
- **MI preprocessing.** The paper says 4-38 Hz and 0.5-3.5 s. The code uses 8-30 Hz and 0-2 s after cue, with a per-trial, per-channel z-score (`h2cmi/data/real_eeg.py` L33-36, L92-96).
- **Sleep preprocessing.** The paper says a 0.3-35 Hz band-pass. The code applies no filter, z-scores each epoch per channel, and crops each night using the hypnogram, i.e. the target labels (`h2cmi/data/sleep_eeg.py` L73-79, L90-91).
- **B14 label set.** The paper says 4 classes. Every artifact is left/right only.
- **GEM implementation (P12).**
  - Density: the paper says diagonal Gaussian; P12 uses a Student-t with low-rank (4) plus diagonal.
  - Readout: the paper says the density head with uniform weights; P12 uses the frozen TSMNet linear classifier.
  - Optimizer: the paper says L-BFGS for 100 iterations; P12 uses Adam, 20×3 steps.
  - Source training: the paper says up to 100 epochs with patience 15; P12 uses 20 epochs and the Sleep bundles use 30.

## 2. Per-dataset inventory

**Raw data (all offline, via MOABB 1.2.0 / MNE 1.8.0 in the `icml` env):**
- B14: `/projects/EEG-foundation-model/datalake/raw/MNE-bnci-data/database/data-sets/001-2014/A0[1-9][TE].mat` (18 files; byte-identical copy reachable through `~/mne_data`)
- Cho: `…/raw/MNE-gigadb-data/…/100295/mat_data/s01-s52.mat` (52 files, 10 GB)
- Lee: `…/raw/MNE-lee2019-mi-data/…/100542/session{1,2}/sNN/*.mat` (108 files, 61 GB)
- Sleep: `…/raw/sleep-edf/sleep-cassette` (153 PSG + 153 hypnogram files; 78 subjects, 75 with two nights; subjects 13, 36 and 52 excluded)

| | Sleep-EDF (EEGNet) | B14 2-class (TSMNet) | Cho2017 (TSMNet) | Lee2019 (TSMNet) |
|---|---|---|---|---|
| **Frozen source models** | 225/225 `/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/results/h2cmi/p0_w2_bundles/*.pt`; density stored inside; EA reference in `moments.npz` (2×2). Also 196/225 different sources in `fp_gem_stage2_sleep/sources`. | 27/27 `~/.cache/h2cmi_training_caches/fp_gem_p12/source_checkpoints/*.pt` (TSMNet state dict, per-subject SPD batch norm; density **not** stored, refit deterministically) | 156/156 in the same directory | 162/162 in the same directory |
| **Saved outputs** | Epoch cache `…/p0_sleep_cache/subjNN.npz` (X [n,2,3000], y, night); W2 result rows with transform `a`,`b` and ρ; Stage-2 night-2 probabilities (196 units) | P12 unit JSON (a, b, fitting prior, hashes only); Stage-2 npz (2-d logits for adapt and eval, trial IDs); EA JSONs | `fp_gem_cho/*.json` (accuracy only, 7 methods); regime summary CSV | Same as B14, plus P13 units |
| **Trial order preserved** | Yes: cache is in time order, night 1 then night 2 | Yes. The P12 split equals runs 0-2 vs 3-5, i.e. chronological | **Only within each class.** MOABB stacks all left trials then all right trials (`gigadb.py` L99-107), and the `.mat` stores classes separately | Within the run yes, but adaptation and evaluation interleave: on average 18.7% of evaluation trials come before the last adaptation trial |
| **Pre-stimulus / calibration segments** | No stimulus. Pre-sleep wake is in the raw files. Lights-off times are in `SC-subjects.xls` per PhysioNet docs (not parsed here: `xlrd` is missing) | 2 s fixation before each cue. 3 EOG baseline runs per session in the `.mat` (A04T has only 1); MOABB drops them (`bnci.py` L621-625) | Each trial is a 7-s frame from −2 to +5 s around the cue. Also `rest` (66 s), `noise` recordings and 20 movement trials per class | About 3 s fixation before each cue. 60 s of rest before and after each phase; 4 EMG channels |
| **Pre-cue in any existing dump?** | Not applicable | **No.** Every MI epoch is 0-2 s after cue; new epoching from raw is needed | No | No |
| **Rejection rule in the loader** | Drops "Movement time" (128 epochs in total) and unscored epochs (24,765). Keeps only 30 min either side of the first and last non-wake epoch, using the labels (median 1,580 epochs trimmed per night). My recount matches the cache exactly, 150/150 nights | None. Expert artifact flags are ignored | None. `bad_trial_indices` ignored | None. MOABB also drops the labelled online phase (50/50 per session; checked in subj01 session 1) |
| **Class counts (protocol → kept → adaptation / evaluation)** | No quota. Adaptation night median 1,132 epochs (672-2,667), evaluation night 1,108. Mean ρ_A = [.30, .11, .38, .075, .135], mean ρ_E = [.30, .11, .37, .075, .146]. N3 count is zero in 9 subjects' adaptation night and 9 subjects' evaluation night | 72/72 per session → 72/72 kept → 36/36 and 36/36. Expert flags per class per session range 0-23; applying them would give left/right ρ from 0.457 (A09T) to 0.519 (A05E), and a 4-class deviation of at most 0.026 | 100/100 (120/120 for subjects 7, 9, 46) → all kept → 50/50 and 50/50. Sampled flags: s20 bad_mi 70 left / 47 right (ρ_left ≈ 0.36 if applied), s49 8/0, s46 1/0, s02 1/0 (voltage); s01 and s32 have none | 50/50 (offline phase, session 0) → all kept → 25/25 and 25/25 |

## 3. Draft artifact_capability_matrix (dataset × operator)

Legend:
- **R** = can be re-run from the checkpoint plus raw data by re-inference (no retraining).
- **R\*** = possible from the checkpoint, but the operator is not implemented in h2cmi.
- **T** = needs retraining.
- **X** = not defined for this model.

| | EA (signal level) | Recenter / RCT | SPDIM (geodesic, bias) | Latent FP-GEM | Latent Joint-GEM | BN refit | Diag-IM |
|---|---|---|---|---|---|---|---|
| Sleep | R (EA reference in bundle) | X (no SPD layer) | X | R (density in bundle) | R | R\* (EEGNet has bn1/bn2) | R |
| B14 2-class | R (`run_ea_b14_lee.py`) | R | R (external repo present at `~/.cache/h2cmi_external/SPDIM_1b0de0cc…`) | R (density refit; verified) | R | same as RCT (TSMNet has only SPD batch norm) | R\* |
| B14 4-class | T | T | T | T | T | T | T |
| Cho | R (Cho runner's EA arm) | R | R | R | R | same as RCT | R\* |
| Lee | R | R | R | R (P13 hash gate) | R | same as RCT | R\* |

- **What works from saved outputs alone:** only prior re-weighting, MLLS and calibration, on the Stage-2 posteriors (B14 and Lee: 189 units; Sleep: 196 units, from a different source set than the paper).
- **Rerun hazards:**
  - The scripts hard-code paths that moved in the reorganisation:
    - `/home/infres/yinwang/CMI_AAAI/.codex_p12_launch_5b71ee8` is now `…/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8`
    - `/home/infres/yinwang/CMI_AAAI_qxu` is now `…/H2CMI/CMI_AAAI_qxu`
    - `/home/infres/yinwang/CMI_AAAI_spdim_clean_a8b9368` is now `…/H2CMI/_frozen_shards/CMI_AAAI_spdim_clean_a8b9368`
  - The runners require a clean git tree before they start.

## 4. Implications for T7, T8 and T9

- **T7 (C1 physical-injection experiment):** feasible without retraining.
  - On B14 2-class, Cho and Lee: EA, Recenter and latent GEM on the same frozen TSMNet.
  - On Sleep: EA and latent GEM only.
  - **Hazard: both loaders z-score every trial per channel** (`real_eeg.py` L93-96, `sleep_eeg.py` L90-91). That exactly cancels any per-channel gain or offset injected upstream, which would make the experiment trivially null. Inject after the z-score (at the model input), or use non-diagonal transforms such as re-referencing or channel mixing. The z-score is also a plausible, untested reason why EA ≈ Source-only everywhere.
- **A2 (sequential / temporal):** possible on B14, Lee and Sleep. Not possible on Cho, because the order across classes is lost.
- **A4 (calibration anchors):** the raw data has rest, EOG and pre-cue segments for all four datasets, but no existing cache contains them; they need new epoching from raw.
- **T8 (multi-batch with known proportions):** the P12 adaptation pools are small (50-100 trials). Better to rebuild from full sessions: B14 144 left/right trials per session, Lee 200 labelled trials per session including the online phase, Cho 200-240.
- **T9 (fixed-prior mismatch test):** needs per-trial features, so re-inference.

## 5. Remaining T3 work (CPU-only; run through SLURM, which I did not submit)

- Tally Cho `bad_trial_indices` for all 52 subjects (about 10 GB of `.mat` reads, roughly 3 minutes).
- Count Lee online-phase labels, only if that phase will be used (about 61 GB of reads).
- Build a Sleep crop from lights-off times that does not use labels (needs `xlrd` or a CSV export of `SC-subjects.xls`).

## Files written (scratchpad only)

Directory: `/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/`
- `t3_rho_audit_draft.csv` (217 rows: per subject/session, protocol vs kept vs adaptation/evaluation counts, ρ, rejection rules)
- `artifact_capability_matrix_draft.csv` (v3 column schema, one row per dataset and label set)
- `t3_b14_artifacts.json`
- `t3_mi_manifest_counts.json`
- `t3_sleep_counts.json`
- `t3_sleep_rejection.json`