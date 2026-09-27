# H2-CMI branch audit for the FP-GEM revision (REVIEW_P0, responsibility-qxu, root `h2cmi`, P13)

This was a read-only audit. I did not modify or check out anything. Branches were read with `git show` and `git ls-tree` in `/home/infres/yinwang/CMI_AAAI`, and data on disk was read with `ls`, `sha256sum` and read-only Python.

## Main findings

1. **The Sleep column of Table 1 comes from the REVIEW_P0 W2 primary run.** That run is commit `278fc85`, `code_sig 763bf49d`, 75 subjects × 3 seeds. I recomputed it from the raw rows and it matches to 0.1 pt:

   | Paper row | REVIEW_P0 branch | Mean over 75 subjects |
   |---|---|---|
   | Source | `identity_uniform` | 65.72 |
   | EA | `source_recolored_ea` | 65.30 |
   | Diag-IM | `latent_im_diag_uniform` | 63.62 |
   | Joint-GEM | `joint_geometry_uniform` | 63.72 |
   | FP-GEM | `fixed_iterative_geometry_uniform` | 65.57 |

   - The paper's "+1.9" is FP-GEM − Joint-GEM = **+1.85 [1.27, 2.45]**.
   - Two branches from the same run are not in the paper: `fixed_reference_oneshot` = **69.54** and `pooled` = 66.00.
2. **The code behind that Sleep column does not match the paper's §5.2 / supplement H description** (details in §4):
   - The fixed fitting prior is **uniform (1/5)**, not the empirical source proportions.
   - The density head is a Student-t, not a diagonal Gaussian.
   - The geometry fit is a fixed 20 EM rounds × 3 Adam steps, not L-BFGS with a stopping rule.
   - Source training is a fixed 30 epochs with no validation split or early stopping.
   - There is no 0.3–35 Hz band-pass filter.
   - I found no L-BFGS GEM implementation on any branch or clone on this server.
3. **The Gaussian simulations are not on the server.** Supplement F.1 says they ran on a Windows i7-9750H machine. Table S1–S4, Fig. 2, `convergence_sim`, `mechanism_sim`, `multiclass_sim` and `optimal_sim` appear on no git ref and in no directory I searched (see §8).

---

## 1. Branch relationships and what each adds

The branches form one straight line: `origin/main c8fce202` → `exp/h2cmi-responsibility-qxu 09e92499` (+49 commits) → `exp/h2cmi-review-p0-corrections 5bc9bf07` (+12) → `origin/exp/h2cmi-wave0-mechanism df47753e` (+74). The local and origin tips are identical for both audited branches, and all three branch from main at `c8fce202`. `review-p0-corrections` is also an ancestor of `origin/agent/fp-gem-stage2`.

### `exp/h2cmi-responsibility-qxu` @ `09e92499` (`git log origin/main..` = 49 commits, 2026-06-20 → 06-23)

- **Stages A–B2b (`624272ae` … `9ebad0d2`):** simulator infrastructure, the responsibility × family grid (B1a), routers, and the canonical CC freeze (`gen_oneshot_diag`, `6d762354`).
- **`27601945` H2CMI_METHOD_FREEZE.** V1 fresh seeds (`bffc08f6` … `82aa6aae`), V2 real-EEG (`96146b6f`, `78841b56`, `bf6375a2`), V2P (`8772ba63`, `edfd3214`, `9c42fd68`).
- **W1/W2:**
  - `71197880`: pre-registration, Sleep-EDF loader, SPDIM-style comparator, MI-LOSO and sleep-LOSO runners.
  - `d6c694d5`: analyzers.
  - `e9301c76`: fix.
  - `82ec85a6`: results.
  - `d4b08522`: framing.
  - `e941bb5b` + `09e92499`: W1-B BTTA-DG reproduction.
- **Files:** `h2cmi/data/sleep_eeg.py`, `run_w2_sleep.py`, `run_w1_mi.py`, `eval/spdim.py`, `eval/ea.py`, `results/W1_W2_{FROZEN,RESULTS}.md`, `W1B_REPRODUCTION.md`, `W1B_portability.patch`, `w1.report.json`, `w2.report.json`, `w1b.report.json`.
- **Old W2 result (before the P0 correction):**
  - Setup: only 20 subjects (`benchmark_subjects → two[:20]`) and only seed 0.
  - Result: `current_joint` Δ −0.043 [−0.071, −0.017].
  - Why it is superseded: the decision prior was the fitted π_J instead of uniform (the "P0-1" confound).
- **BTTA-DG reproduction (W1-B):**
  - Upstream `luo-huan-123/BTTA-DG` @ `5932d026`, MIT licence, LOSO on BNCI2014001/002/2015001, n = 35.
  - As published, BTTA-DG equals its own source-only ensemble exactly (Δ = +0.0000). The only buffer-filling call, `add_sample()`, is never called, so the GMM step does nothing.
  - With that call restored, the GMM is active on about 2.3% of trials and flips 1 prediction in total.
  - On disk: `/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/w1b_external/BTTA-DG` (HEAD `5932d026…`, plus the `.tar` and the patch) and `…/results/h2cmi/w1b_out/` (35 `.npy` files).

### `exp/h2cmi-review-p0-corrections` @ `5bc9bf07` (12 commits on top of qxu, 2026-06-23 → 06-29)

- **Commits:**
  - `4713dd6a`: pre-registration `REVIEW_P0_FROZEN.md`.
  - `cf3f3f6c`: `eval/p0_eval.py` and `tta/weighted_tta.py`.
  - `46ac2912`: `run_w1_p0.py` and `p0_source.py`.
  - `83ec64b4`: `run_w2_p0.py`, `run_v2p_weighted.py`, analyzer.
  - `278fc85e`: gitignore; this is the commit that produced the raw results.
  - `7788e52a`: `PROJECT_OVERVIEW.md`.
  - `dbb43e07` / `8ea5f994` / `cf8352a6` / `829d27db` / `9a35cc97` / `5bc9bf07`: finalizers (manifest, corrected analyzer `analyze_p0_final.py`, provenance audit, confusion replay, `REVIEW_P0_RESULTS.md`).
- **The two corrections:**
  - **P0-1:** separate the fitting prior from the decision prior.
  - **P0-2:** V2P reweights the same trials instead of drawing different subsets.
- **Other changes vs the old run:** W2 now uses all 75 paired-night subjects and seeds {0, 1, 2}.

### Root package `/home/infres/yinwang/CMI_AAAI/h2cmi`

- **On `origin/main`:** 37 files, a single commit `0e6ebfd3` ("ICLR-direction redesign"). This is the simulator-only precursor. It has no Sleep, P0 or FP-GEM code, and its `TTAConfig` still uses the old name `prior_kl`.
- **On the current checkout (`agent/cedar-eeg-p0` @ `1ab08225`):** main plus Project A (`h2cmi/observability/*`, `run_real_audited*.py`, 25 tests, a modified `eval/harness.py`; Steps 5–20, `eb7dd1dc` … `183f27fc`). It also has no FP-GEM, Sleep or REVIEW_P0 code.
- `h2cmi/results/review_completion/` exists but is an empty, untracked directory.

## 2. REVIEW_P0 headline numbers

Source: `origin/exp/h2cmi-review-p0-corrections:h2cmi/results/REVIEW_P0_RESULTS.md` and `review_p0.report.json`. The runner commit is `278fc85`; the report names `9a35cc9` as analyzer commit, while the analyzer code itself (`analyze_p0_final.py`) is from `8ea5f994`.

**W2 Sleep-Cassette, 75 subjects, subject bootstrap with 10,000 resamples:**

| Contrast | Primary protocol (night 1 → night 2) | Secondary protocol (within night 2) | Where |
|---|---|---|---|
| G = joint geometry − identity (pre-registered **primary** contrast) | −0.0200 [−0.0413, +0.0007], not significant | −0.0230 [−0.0436, −0.0029] | RESULTS.md:73 |
| **P = identity@π_J − identity@uniform** (the "14-point decision-prior effect") | **−0.1438 [−0.1591, −0.1283]** | −0.1300 [−0.1496, −0.1103] | :74 |
| joint geometry: decode with π_J − decode with uniform | −0.0846 [−0.0968, −0.0727] | −0.1061 | :75 |
| **FP − Joint** (pre-registered as **secondary** in W2) | **+0.0185 [+0.0127, +0.0245]** | +0.0234 [+0.0112, +0.0377] | :76, :92, :209 |

- **Share of subjects worse than Source-only:** identity@π_J 98.7%, Joint 61.3%, FP 46.7%, one-shot 30.7% (lines 82–84).
- **Values I recomputed from the raw rows:**
  - FP beats Joint on **63 of 75** subjects and loses on 12.
  - FP beats Source on 40 subjects and loses on 35.
  - Subject-level standard deviations: Source 9.77, FP 10.85, Joint 10.97. These can fill the missing Sleep s.d. in Table 1.

**W1 (motor imagery, 115 subjects):** FP − Joint = +0.0022 [−0.0005, +0.0049], not significant; G = +0.060 (driven by Cho2017).
- W1 is **not** the source of the paper's MI columns. Its per-dataset Source values are 68.9 / 62.5 / 71.3, against 61.0 / 52.3 / 54.9 in the paper.
- W1 uses BNCI2014_001 as a two-class left/right task and the H2 encoder, not TSMNet.

**V2P_WEIGHTED (90 units in 72 clusters):** embedding displacement is pooled 0.049 < one-shot (FRSC) 0.314 < iterative ≈ joint 0.640 ≪ oracle 1.960.

**Reproducibility:** the Wave0 W0.1 deterministic rerun (`H2CMI/CMI_AAAI_qxu/results/h2cmi/wave0_w2.report.json`) gives FP − Joint = +0.01866 [0.01285, 0.02463] and G = −0.0201. The confusion replay in REVIEW_P0 §4 is excluded (114 of 2025 prediction hashes differed, GPU nondeterminism).

## 3. Sleep-EDF pipeline as implemented (review-p0 branch)

- **Runner:** `h2cmi/run_w2_p0.py`.
  - Adaptation / evaluation split at lines 105–110: night 1 adapts, night 2 evaluates; the secondary protocol splits night 2 in half.
  - Minimum set sizes 16 / 8 at line 111.
  - Default of 30 epochs at line 163.
- **Configuration:** `sleep_cfg` in `run_w2_sleep.py:49-55`. K = `NC` = 5 (line 45), 2 channels, 3000 samples, only the temporal branch, CMI switched off.
- **Loader:** `data/sleep_eeg.py`.
  - Data root `/projects/EEG-foundation-model/datalake/raw/sleep-edf/sleep-cassette` (line 17); Sleep-Cassette only.
  - Channels Fpz-Cz and Pz-Oz; 100 Hz; S3 and S4 merged into N3.
  - Recordings cropped to 30 minutes either side of the sleep period (lines 73–79).
  - **Each 30-s epoch is z-scored per channel (lines 90–91). There is no band-pass filter.**
- **Encoder:** `models/encoder.py`. The `TemporalBranch` is "EEGNet-ish" (lines 47–68): 32 temporal filters of length 187, a depthwise spatial convolution, and pooling to 8. It feeds a fusion MLP that produces a 16-dimensional task latent `z_c` (`core_config`, `config.py:181`).
- **Source training:** `train/trainer.py:86+`. AdamW with lr 1e-3 and weight decay 1e-4 (line 112), cosine schedule (line 114), batch 64, **a fixed 30 epochs, no validation split, no early stopping**. Every source bundle's JSON records `"epochs": 30`.
- **Density head:** `density/student_t_mixture.py`, `DensityConfig` in `config.py:34-44` and `core_config` lines 187–189.
  - Student-t with 8 degrees of freedom, low-rank (rank 2) plus diagonal covariance, eigenvalue floor 1e-2.
  - Trained jointly with the encoder using the loss CE + NLL + 0.5 × JS (`loss()` line 142, total at line 151).
- **Source prior:** `p0_source.py:75,82` uses `reference_prior(y, K, "uniform")`, which is `trainer.py:44-48`. **So π_fit is 0.2 for every class.**
  - The empirical source proportions from the raw rows are W 0.339, N1 0.111, N2 0.351, N3 0.067, REM 0.132.
  - Mean JS divergence between uniform and each subject's evaluation-night proportions is 0.0715.
- **GEM fit:** `tta/class_conditional.py::_fit_transform`.
  - 20 EM rounds (lines 229–255), each with 3 Adam steps at lr 0.05. There is no stopping rule.
  - Penalty on the transform: log-determinant weight 1, plus trust-region terms τ‖A−I‖²/d and τ_b‖b‖²/d with τ = τ_b = 1.
  - The Joint prior M-step (line 245) adds a Dirichlet anchor of (5 + 1) × π_S.
  - Variants: FP = `gen_iterative_diag` (fitting prior fixed, line 406); Joint = `joint_iterative_diag`; one-shot = `gen_oneshot_diag` (responsibilities computed once, line 396).
- **Evaluation and decoding:** `eval/p0_eval.py`.
  - The Joint fit happens once (line 82).
  - Uniform decoding is at lines 77 and 85–88.
  - Comparators are at lines 91–101: Diag-IM is `spdim_fit` (40 Adam steps, `eval/spdim.py:20`), and EA recolours to the source reference (`ea.py:31-38`).
  - The additive decomposition check is at lines 104–114.

## 4. Paper description vs the code that produced the Sleep numbers

| Item | Paper (§5.2 / supplement H) | Code (`278fc85`) |
|---|---|---|
| Fitting prior π_fit | Empirical source proportions | **Uniform 1/5** |
| Density | Diagonal Gaussian fitted after training, variance floor 1e-4 | Student-t (8 d.o.f.), rank 2 + diagonal, floor 1e-2, trained jointly |
| Geometry M-step | L-BFGS, ≤100 GEM iterations, stop after 5 changes < 1e-6, log-scales in [−2, 2], penalty 1e-3 | Adam, a fixed 20 × 3 steps, trust region 1.0 plus log-determinant term, no bounds |
| Joint prior update | Average of responsibilities, weights floored at 1e-4 | Dirichlet anchor of 6 × π_S |
| Source training | 80/20 train/validation split, ≤100 epochs, patience 15 | A fixed 30 epochs, no validation |
| Preprocessing | 0.3–35 Hz band-pass; normalisation statistics from source training | No filter; each epoch z-scored separately; ±30-min crop |
| Diag-IM | 50 epochs, tuned on source validation | 40 steps, fixed trust region |

- **P12 / P13 (motor imagery) use the same `ClassConditionalTTA` Adam settings.** See `origin/exp/h2cmi-wave0-mechanism:h2cmi/results/fp_gem_main/fp_gem_config.json`: Student-t rank 4, 20 × 3 Adam steps, and "decision through the TSMNet classifier". These also do not match §H.
- **The Stage-2 Sleep pre-registration repeats the prior mislabel.** `FP_GEM_STAGE2_SLEEP_FROZEN.md` on fp-gem-stage2 says "π_src", but the code path is the same uniform-prior one.
- **Per-stage recall explains the Sleep result.** Data: `origin/agent/fp-gem-stage2:h2cmi/results/review_completion/sleep_per_stage_recall.csv`, commit `29a21959`, from the W0.1 deterministic rerun.
  - FP and Joint both move about 38 points of N2 recall into N3: N2 0.885 → 0.51 / 0.50, N3 0.53 → 0.96.
  - FP's edge over Joint comes from N1 and REM.
  - The mean fitted Joint prior is [0.369, 0.008, 0.301, 0.220, 0.102]; its N3 value of 0.22 compares with a true share of about 0.075.
  - This fits a misspecified uniform prior pushing the geometry, which is the opposite of how the paper frames Sleep.

## 5. Raw data and dumps on disk

**REVIEW_P0 raw rows**, in `/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/results/h2cmi/`. That worktree is on local `exp/h2cmi-wave0-mechanism` @ `a8b93682`. The SHA-256 of all four files below matches `REVIEW_P0_MANIFEST.json`.
- `p0_w2_primary_all.jsonl`: `bc605da7…`, 2250 rows.
- `p0_w2_secondary_all.jsonl`: `a4d200c8…`.
- `p0_w1_all.jsonl`: `c1ef4a6f…`.
- `p0_v2pw_all.jsonl`: `6b0edcca…`.
- Each row records the source proportions, both nights' proportions, π_J, four JS divergences, per-stage recall and the confusion matrix. This answers the reviewer's question about empirical target proportions.
- The per-target shards are `p0w2_{primary,secondary,replay}_*.jsonl`.

**Other Sleep artifacts:**
- Sleep epoch cache: `…/results/h2cmi/p0_sleep_cache/` (3.1 GB; 75 `subjNN.npz` files plus `p0_benchmark.json`).
- Source bundles: `…/p0_w2_bundles/` (675 files = 225 bundles × 3).
- `p0_w2_det_bundles/` is empty.
- The Wave0 deterministic rerun is in `wave0_w2det/`.
- **Stage-2 Sleep dump ("EEGNet, K=5, natural shift"):** `/home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_stage2_sleep/`.
  - Runner `run_w2_sleep_stage2_dump.py`, commits `687003ff` / `e23825b6`; analyzer `722e33cd`.
  - **It is incomplete: 196 of 225 units.** SLURM job 910097 was cancelled on its time limit at 2026-07-28 02:10.
  - The results were never committed.
  - The runner's default `--cache` path `/home/infres/yinwang/CMI_AAAI_qxu/…` no longer exists since the reorganisation; the cache is now under `H2CMI/CMI_AAAI_qxu`.

## 6. P13 (Joint prior 0.46 → 0.50, geometry displacement 1.4)

- **Where it lives:** `origin/exp/h2cmi-wave0-mechanism`.
  - Commits: `7b48813e` (protocol freeze) → `afa21f2e` (launch) → `a7036197` → `245dc579` → `6cb8e35c` → **`b5fb5158`** (results).
  - Runner `h2cmi/run_fp_gem_prevalence.py`.
  - Outputs in `h2cmi/results/fp_gem_prevalence/`: completion report, summary JSON, `*_geometry_diagnostic.csv` (972 rows), per-subject CSV.
  - Raw data: `/home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_p13`.
- **Setup:** Lee2019_MI, 54 subjects × 3 seeds, the P12 TSMNet checkpoints, a 50-trial adaptation reservoir. q is the class-0 share: [5, 45] → q = 0.1, [25, 25] → 0.5, [45, 5] → 0.9.
- **Joint fitted class-0 prior:** 0.4636 / 0.4850 / 0.5007 at q = 0.1 / 0.5 / 0.9. FP stays at 0.5.
- **Geometry displacement from q = 0.5** (√(‖Δb‖² + ‖Δa‖²) over 210 dimensions):

  | Method | q = 0.1 | q = 0.9 | Log-scale part | Translation part |
  |---|---|---|---|---|
  | Joint | 1.436 | 1.424 | ≈1.40 | 0.25 |
  | FP | 1.414 | 1.404 | ≈1.39 | 0.21 |

  **The 1.4 is almost the same for FP; it is not specific to Joint.**
- **Primary result:** FP − Joint sensitivity = −0.00074 [−0.0036, +0.0021]. The interval crosses zero, so the claim that FP is less prevalence-sensitive is **not supported**.

## 7. What S9, S12, Table S3/S4 and `convergence_sim` correspond to

- **S9 = Lemma S9** (uniform decision weights maximise balanced accuracy; supplement line 449).
  - No code carries that name. Uniform decoding is at `p0_eval.py:77,85-88`.
  - Its real-data counterpart is P = −14.4 points (RESULTS.md:74, :87–91).
- **S12 = Theorem S12** (the oracle class-conditional optimum does not depend on class weights).
  - The closest code is the V2P oracle `fit_weighted_em(kind="oracle")` in `tta/weighted_tta.py:63-108` (one-hot at lines 87–89), called from `run_v2p_weighted.py:30-39`. It also appears as the `oracle_oneshot_diag` variant.
  - The oracle's displacement of 1.96 contradicts S12's conclusion. But the code breaks S12's premises: no convergence (20 × 3 Adam steps), a trust-region penalty, and a jointly trained Student-t density. So the displacement cannot be attributed to class-dependent geometry alone.
- **Table S3** (paired FP − Joint at n_A = 500), **Table S4** (strict EM from the identity, seed 930000) and **Table S1/S2 / Fig. 2** (finite-difference seed 913731) have **no code or outputs on the server.**
  - Supplement F.1 says they ran on a Windows i7-9750H host.
  - `convergence_sim`, `mechanism_sim`, `multiclass_sim`, `optimal_sim`, `version_b_optimal` and `precheck_theory.py` appear on no git ref and in no directory I searched (`/home/infres/yinwang` to depth 5; `CMI_AAAI` and `AAAI_2026` to depth 4). I found no `fpgem` package in those directories or in the `icml` conda environment.
  - `REVISION_PLAN_TSP_TPAMI.md` §11 lists them as local-only.

## 8. `notes/` and top-level `results/`

- I found nothing related to FP-GEM or H2-CMI in `notes/`.
  - `preprocessing_decision.md` only matched "Gemein".
  - The `route_A_gls_vae.md:196` match ("fixed prior variance") and the `project_A_observability` matches (step13) are unrelated.
  - `project_A_observability/04_prior_decoupled_theory.md` is about CMI prior decoupling, not FP-GEM.
- The top-level `results/` directory holds 393 AAAI-CMI files and none relate to FP-GEM. `H2CMI/paper_data` belongs to a different "P12", the CMI nullspace paper.

Scratch file: `/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/review_p0.report.json` (a copy extracted from the branch).