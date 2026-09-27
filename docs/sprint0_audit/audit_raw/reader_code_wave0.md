# FP-GEM on `origin/exp/h2cmi-wave0-mechanism` (tip `df47753e`): implementation map, results, and how they line up with the paper

All paths and line numbers below refer to the tree at `df47753e`, read with `git show`. I made no checkouts, SLURM calls or edits.

## 0. Main findings

1. **FP-GEM and Joint-GEM are not separate code.** Both are variants of the H2CMI class-conditional TTA, `h2cmi/tta/class_conditional.py`:
   - FP-GEM is the variant named `gen_iterative_diag`.
   - Joint-GEM is the variant named `joint_iterative_diag`.
   - The only difference is at `_variant_core` L406: `fixed_prior = pi_S_t if spec.update == "prior_fixed" else None`. When `fixed_prior` is set, `_fit_transform` skips the prior M-step at L243-245.
2. **The code on this branch does not match the method the paper describes.** Differences are in the density head, the regularizer, the optimizer, the stopping rule, the Joint prior update (a Dirichlet pseudo-count κ = 5 + 1 = 6), the MI readout, the number of B14 classes, the MI split and the MI preprocessing. For the Sleep result, the "πsrc" held fixed by FP-GEM is actually **uniform**, not the empirical source proportions (§7).
3. **The controlled Gaussian study in the paper is not in this branch.** That study gives R²=0.998, 2,038 fits, the variance–bias crossover, and uses master seed 20270728. I searched all 121 branch tips for the seed `20270728` in `.py`/`.md` files and found nothing. The supplement §F.1 says it ran on a Windows i7-9750H laptop. What this branch does have is a different "controlled" result, from the H2CMI synthetic EEG simulator (§5).
4. **Paper Table 1, cell by cell:**
   - The Sleep column is REVIEW_P0 W2 on this branch, and it matches exactly.
   - The MI Source/Recenter/SPDIM cells match P12, plus P9 or the Cho cache for Cho2017.
   - **The MI FP-GEM and Joint-GEM cells do not match any artifact I found.** The standard deviations are identical to the P12/Cho-cache values, but three FP-GEM means are exactly +1.0 or +2.0 points higher, and one Joint-GEM mean is +1.0 higher (§8). This needs author verification.
5. **The frozen claim gate at `df47753e` forbids the paper's headline MI claim.** It says FP-GEM vs Joint-GEM on natural transfer is *not supported*: P12 gives +0.0029 [−0.0003, +0.0062].

## 1. FP-GEM-related commits (`git log origin/main..origin/exp/h2cmi-wave0-mechanism`, 135 in total)

**Core FP-GEM line (P12 → P13 → P14):**

| SHA | date | subject |
|---|---|---|
| `f34cc8b2` | 07-11 | Freeze Fixed-Prior Geometry EM same-backbone protocol (adds `run_fp_gem.py`, `analyze_fp_gem.py`, `prepare_fp_gem_freeze.py`, `finalize_fp_gem_smoke.py`, `tests/test_fp_gem.py`, `fp_gem_config.json`, `fp_gem_units.csv`, slurm) |
| `5b71ee84` | 07-11 | Amend FP-GEM source checkpoint provenance gate (P9 weights were never saved, so each unit retrains with the exact P9 config) |
| `1c39525c` | 07-11 | Record FP-GEM no-performance smoke gate (job 893433) |
| `e6c49156` | 07-11 | Shard FP-GEM fleet under scheduler submit limit |
| `3bba1d0b` | 07-13 | **P12 results**: Evaluate FP-GEM against official SPDIM |
| `7b48813e` | 07-13 | **P13 protocol freeze** (prevalence stress; adds `run/prepare/analyze_fp_gem_prevalence.py`, manifest, slurm) |
| `afa21f2e` | 07-13 | P13 checkpoint-reuse gate PASS (job 894726); this is the P13 launch commit |
| `a7036197` | 07-13 | Harden P13 scheduler handoff validation (analyzer only) |
| `245dc579` | 07-14 | Preserve P13 execution provenance (analyzer only) |
| `6cb8e35c` | 07-14 | Bind P13 raw rows to frozen stress manifest (analyzer only) |
| `b5fb5158` | 07-14 | **P13 results**: "Canonical FP-GEM result head" |
| `df47753e` | 07-14 | **P14**: Freeze final FP-GEM method story and evidence hierarchy |

**Prerequisite evidence cited in the FP-GEM spine:**
- `31297db0`, `cbf6b50e`, `2b4c4f12` (06-21): B1a variant grid and `C_prior_coupling`.
- `bffc08f6` (06-22): V1 fresh seeds.
- `4713dd6a` → `5bc9bf07` (06-23 to 06-29): REVIEW_P0, which includes the Sleep FP − Joint +0.0185. Raw compute ran at `278fc85e`.
- `ab93820d`, `bc61ee11`: repaired W1 split and H2CMI results.
- `8972de87`: P9 official SPDIM, three seeds.
- `cfb43d42`, `f2808796`: repaired-W1 freeze.

**Adapter source history:**
- `h2cmi/tta/class_conditional.py` was last changed at `15838783` (06-21).
- The Dirichlet anchor was renamed at `4fc4d4dc`.
- The GEM math was frozen before P12.

## 2. GEM adapter: `h2cmi/tta/class_conditional.py`

| element | location | implementation |
|---|---|---|
| Transform family | `Transform` L38-79; `diag_affine` L44-46, `apply` L67-70 | `T(z)=z*exp(a)+b` (coordinatewise gain and offset); `logdet=a.sum()` L72-75; `trust=‖diag(e^a)−I‖_F²` L77-79 |
| Variant registry | `VariantSpec` L97-117; `B1A_VARIANTS` L123-131 | **FP-GEM = `gen_iterative_diag`** (L127: responsibility `gen_iterative`, update `prior_fixed`). **Joint-GEM = `joint_iterative_diag`** (L130: update `joint`). |
| **FP/Joint switch** | `_variant_core` L387-408, **L406** | `fixed_prior = pi_S_t if spec.update=="prior_fixed" else None` |
| Initialization | L226-228 | `a=0`, `b=0`; `pi_T = pi_S` (or `fixed_prior`) |
| Optimizer | L229 | `Adam(T.params, lr=cfg.em_lr)`, created once, so Adam moment state carries across outer iterations |
| κ pseudo-count | L232-233 | `anchor = (cfg.dirichlet + cfg.prior_anchor_strength) * pi_S` = **(5+1)·πS, so κ=6** (`config.py` L110-111) |
| E-step (responsibility) | L240-242 | `r = softmax(log p_y(T(u_i)) + log pi_T)`. The Jacobian is class-constant, so it cancels. |
| **Prior M-step (skipped by FP-GEM)** | **L243-245** | `if fixed_prior is None: pi_T = (Σ_i r_iy + 6πS_y)/(n + 6)` |
| Geometry M-step | L249-256 | 3 Adam steps per outer iteration on `mean_i Σ_y r_iy[log p_y(Tu_i)+log π_y] + 1.0·Σa − 1.0·‖e^a−1‖²/d − 1.0·‖b‖²/d` |
| Stopping rule | L235 | fixed `cfg.em_iters` outer iterations (20 in P12/P13, so 60 Adam steps). No convergence test. |
| Restart/objective | `fit_variant` L410-446 | 1 restart for diag variants; objective from `_fit_objective` L262-270; `r_final` posterior L438-439 |
| Unused variants | L396-398 (`gen_oneshot`), L399-403 (`oracle`) | "FRSC" one-shot, the best Sleep operator, is `gen_oneshot_diag` L126 |

Default configuration is `h2cmi/config.py` `TTAConfig`, L97-119: `trust_region=1`, `trust_region_b=1`, `logdet_weight=1`, `prior_anchor_strength=1`, `dirichlet=5`, `em_iters=20`, `em_lr=0.05`.

The unit test is `tests/test_fp_gem.py::test_fp_gem_and_joint_gem_differ_only_in_prior_update`, L40-63.

## 3. Density head: `h2cmi/density/student_t_mixture.py`

- `_student_t_logpdf` L30-58: multivariate Student-t with a Woodbury low-rank-plus-diagonal scale `Σ=LLᵀ+diag(softplus(s)+floor)`.
- `ClassConditionalDensity` L61-101: `log_prob_all` L83-90, `class_posterior` L95-101.
- **In P12/P13**, the density is fit afterwards on frozen TSMNet features (`run_fp_gem.py::fit_source_density` L466-542):
  - 1 component per class, rank 4, df 8, floor 0.01, `init_scale` 1;
  - AdamW, lr 1e-3, weight decay 1e-4, batch 64, cosine schedule over a fixed 40 epochs, gradient clip 5;
  - loss `−log p(z|y)/d`;
  - fit on P9 source-train features only.
  - πsrc is the empirical class frequency (L526-527).
- **In REVIEW_P0 and W1-repaired**, the density is trained jointly with the H2CMI encoder through the `HybridHead` loss (CE + β·NLL + γ·JS, L112-153). It uses `core_config` settings: rank 2, df 8 (`config.py` L167-197).

## 4. Prediction and decision rule

There are two different readouts on this branch.

**P12/P13 (TSMNet):**
- The frozen TSMNet classifier is applied to T(z): `rct_model.classifier(fixed.transform.apply(eval_features))`, at `run_fp_gem.py` L927-929 and `run_fp_gem_prevalence.py` L408-409.
- The feature hook is `capture_preclassifier` L274-313: a forward pre-hook on `TSMNet.classifier`, dimension 210, replay error ≤ 1e-7.
- The fit prior is **not** injected into the logits (config `decision_rule`).
- Evaluation labels are read only after both fits (L959-960).

**REVIEW_P0 and W1-repaired (H2CMI encoder):**
- The readout is the density Bayes posterior with a uniform decision prior: `eval/harness.py::_predict_transform` L33-36, called from `eval/p0_eval.py::eval_unit_p0` L73-115.
  - Joint: L82 and L87.
  - FP: L91-96, `fixed_iterative_geometry_uniform`.
  - Diag-IM: `latent_im_diag_uniform` L97-98, from `eval/spdim.py`.
  - EA: L99-101.
- The fitting prior here is `pi_star = reference_prior(y,K,"uniform")` (`p0_source.py` L75/L82; `train/trainer.py` L44-48). So FP-GEM pins π_fit to **uniform**, and κ=6 anchors Joint toward uniform.

## 5. Simulation code on this branch

**Not present anywhere in git:** the paper's 4-D Gaussian study (§5.1: R²=0.998, 2,038/4,000 fits, crossover at ρ=0.92, t=0.75, L-BFGS-B, seed 20270728).

**What is present is a different controlled experiment:**
- Simulator: `h2cmi/data/eeg_simulator.py`, a synthetic multichannel EEG model with site→subject→session structure. `ShiftSpec` L38-47 has the knobs `cov`, `prior`, `concept`, `montage`, `noise`.
- Runner: `run_b1a_grid.py`.
- Contrast: `analyze_b1a_grid.py` L17, L49, L57 define `C_prior_coupling = bacc[gen_iterative_diag] − bacc[joint_iterative_diag]` (FP − Joint).
- Result file: `h2cmi/results/b1a_confirm.report.json` (20 seeds). This is the source of the "+0.012 to +0.032" in `fp_gem_theory_to_evidence.csv`.

| mechanism | FP − Joint [CI] |
|---|---|
| `cov` | +0.0125 [+0.0024, +0.0254] |
| `cov_prior` | +0.0118 [+0.0023, +0.0239] |
| `cov_conditional_rotation` | +0.0315 [+0.0156, +0.0494] |
| `conditional_rotation` | +0.0076 [+0.0017, +0.0179] |
| `prior` | +0.0012 [−0.0009, +0.0038] (not significant) |
| `population_null` | +0.0011 |
| `matched_domain_null` | 0 |

- **Other displacement and prevalence evidence:** V2P_WEIGHTED in `REVIEW_P0_RESULTS.md` §3. Embedding displacement is fixed_iterative 0.640 vs joint 0.640 (identical), FRSC 0.314, pooled 0.049.
- **Real-EEG prevalence displacement:** P13 geometry diagnostic (§6).

## 6. Prevalence-stress protocol (P13)

**Protocol (`7b48813e`), `h2cmi/results/fp_gem_prevalence/FP_GEM_PREVALENCE_PROTOCOL.md`:**
- Lee2019_MI, all 54 subjects × 3 seeds, the exact P12 checkpoints, and the unchanged 50-trial evaluation block [25,25].
- The adaptation reservoir is the P12 50-trial block, with q ∈ {0.1, 0.5, 0.9} → counts [5,45], [25,25], [45,5].
- The primary endpoint is `0.5(|bAcc(.1)−bAcc(.5)|+|bAcc(.9)−bAcc(.5)|)`. The primary claim requires the FP − Joint CI to lie entirely below 0.
- Bootstrap: 10,000 replicates, seed 20260710, clustered by subject.

**Code:**
- Intervention builder: `prepare_fp_gem_prevalence.py::batch_ids` L79-91, with `repeat_or_crop` L73-76.
- Runner (`run_fp_gem_prevalence.py`):
  - `adapt_methods` L252-448 receives no labels and no q; its `TTAConfig` is at L373-383.
  - `load_p12_checkpoint` L189 and `break_spd_running_buffer_aliases` L178 load the saved checkpoints.
  - `verify_p12_center` L462 is the q=0.5 hash gate.
  - `geometry_with_displacement` L502-517 computes ‖Δa‖, ‖Δb‖ and √ of their squared sum.
  - `run_checkpoint_gate` L636 and `run_unit` L710 run the gate job and the fleet units.
- Analyzer: the sensitivity endpoint is `analyze_fp_gem_prevalence.py` L578; `bootstrap_endpoints` is L609.

**Gate (`afa21f2e`):** job 894726 on a V100 passed. The checkpoint, prediction, logits, density and geometry hashes all reproduced, and 216 aliased SPD buffers were separated before loading.

**Results (`b5fb5158`, CSV SHA `cf9e403e…`):**

| | value [95% CI] |
|---|---|
| Sensitivity, FP-GEM | 0.0296 [0.0233, 0.0367] |
| Sensitivity, Joint-GEM | 0.0303 |
| Sensitivity, RCT | 0.0357 |
| Sensitivity, SPDIM geodesic | 0.0295 |
| Sensitivity, SPDIM bias | 0.0281 |
| **FP − Joint (primary)** | **−0.00074 [−0.00364, +0.00210], not supported** |
| FP − RCT | −0.0061 [−0.0114, −0.0010] |
| FP − SPDIM geodesic | +0.0001 (not significant) |
| FP − SPDIM bias | +0.0015 (not significant) |
| Endpoint-mean bAcc, FP | 0.6488 |
| Endpoint-mean bAcc, Joint | 0.6470 |
| Endpoint-mean bAcc, RCT | 0.6589 |
| Endpoint-mean bAcc, SPDIM geodesic | 0.6641 |
| Endpoint-mean bAcc, SPDIM bias | 0.6638 |
| Endpoint-mean bAcc, FP − Joint | +0.0019 [−0.0006, +0.0044] |

- **Geometry displacement from q=.5:** Joint 1.436 at q=.1 and 1.424 at q=.9; FP 1.414 and 1.404.
- **Joint fitted class-0 prior** at q=.1/.5/.9: 0.4636 / 0.4850 / 0.5007. FP stays at 0.5000.
- So Joint's prior barely moves, which is consistent with κ=6 and n=50.

## 7. Paper vs. code

**P12/P13 code compared with the paper:**

| item | paper (main §4-5, supp. §H) | wave0 P12/P13 |
|---|---|---|
| density | diagonal Gaussian, variance floor 1e-4 | Student-t, rank-4 plus diagonal, df 8, floor 1e-2 |
| Joint prior M-step | mean responsibility, floor 1e-4 | `(Σr+6πS)/(n+6)` (κ=6) |
| penalty | identity-centered, 1e-3; log-scale in [−2,2] | logdet 1, trust 1/1, no bounds |
| optimizer / stop | L-BFGS, ≤100 iterations, 5 consecutive relative changes <1e-6 | Adam lr 0.05, 20×3 steps, fixed |
| MI readout | density argmax with uniform π_dec | frozen `TSMNet.classifier` |
| B14 classes | 4 | 2 (`LeftRightImagery`, `real_eeg.py` L72-76; density K=2 at `run_fp_gem.py` L488) |
| MI split | earlier session adapts, later session evaluates | `class_stratified_half`, first session only (`w1_repaired_split.py` L80-95) |
| MI preprocessing | 4–38 Hz, 0.5–3.5 s | 8–30 Hz, 2.0 s window (`real_eeg.py` L33-35) |
| source training | ≤100 epochs, patience 15, split by participant | P9: fixed 20 epochs; val = last 20% of each subject × class (`run_spdim_probe.py` L132-145) |

**Sleep (REVIEW_P0 W2, `run_w2_p0.py`):**
- The encoder is the H2CMI EEGNet-style temporal branch (`run_w2_sleep.py::sleep_cfg` L49-56).
- It uses a Student-t rank-2 density, Adam with κ=6, and **a uniform π_fit** (`p0_source.py` L75/82).

## 8. Paper Table 1 provenance

| cell | source | match |
|---|---|---|
| Sleep: Source 65.7, EA 65.3, Diag-IM 63.6, Joint 63.7, FP 65.6 | `h2cmi/results/review_p0.report.json` `W2_primary.branch_mean_bacc`: 0.6572, 0.653, 0.6362, 0.6372, 0.6557. FP − Joint = +0.0185 [+0.0127, +0.0245] | exact. Note FRSC one-shot = 0.6954 (best, not in the paper), and FP is 0.1 below Source. |
| B14 and Lee: Source, Recenter, SPDIM | P12 `fp_gem_per_subject.csv`: B14 60.96 (10.80), 72.74 (12.82), 72.74 (12.91); Lee 54.85 (4.90), 68.16 (10.00), 67.65 (9.84) | exact |
| Cho: Source, Recenter, SPDIM, EA | P9 `spdim_w1_repaired_three_seed_results.csv` (`8972de87`) and the cache `~/.cache/h2cmi_training_caches/fp_gem_cho` (commit `04a40e4`, agent/fp-gem-stage2): 52.35, 59.76, 59.66, 52.19 | exact |
| **GEM rows, MI** | P12: B14 FP 71.24 (11.48), Joint 70.94 (11.34); Lee FP 66.56 (9.35), Joint 66.27 (9.24). Cho cache: FP 58.98 (7.14), Joint 59.19 (7.13) | **paper: 73.2 (11.5) / 71.9 (11.3); 67.6 (9.3) / 66.3 (9.2); 60.0 (7.1) / 59.2 (7.1)** |

For the MI GEM rows:
- All six standard deviations are identical to the artifacts.
- The FP-GEM means are +2.0, +1.0 and +1.0 higher (B14, Lee, Cho), and Joint B14 is +1.0 higher.
- As a result, the paper's FP − Joint gaps (1.3, 1.3, 0.8) differ from the artifacts (0.3, 0.3, −0.2).
- `~/.cache/h2cmi_training_caches/FP_GEM_RESULTS_SO_FAR.md` (2026-07-28) lists the artifact values.
- `FP-GEM/REVISION_PLAN_TSP_TPAMI.md` L60 says a "later round" exists but has no local artifacts. I found none.

## 9. `df47753e`: the story freeze, read in full

`FINAL_FP_GEM_STORY_FREEZE.md/json` has status `FROZEN` and names FP-GEM as the main method. Its frozen inputs are the P12 result SHA `f3e4ca69…` (`3bba1d0b`) and the P13 result SHA `cf9e403e…` (`b5fb5158`). It makes three kinds of claim.

**Theory:**
- Joint prior fitting creates a prior-to-geometry feedback path.
- FP-GEM removes the prior M-step while keeping iterative geometry fitting.
- Fixing the prior removes the feedback, but not soft-assignment or prior-misspecification bias.

**Method:**
- FP-GEM is a simple, theory-derived, decoupled geometry estimator.
- It is not claimed to be prevalence-invariant, and not claimed to be SOTA.

**Empirical:**
- Controlled FP − Joint effects are positive.
- The Sleep FP − Joint contrast is positive.
- P12 FP-GEM beats source-only, but does not beat RCT, SPDIM geodesic or SPDIM bias.
- P13's primary claim is unsupported. The only supported P13 contrast is lower sensitivity than RCT, with lower endpoint performance.

**Claim gate:**

| flag | value |
|---|---|
| `fp_gem_is_main_method` | true |
| `theory_prior_feedback_claim_supported` | true |
| `controlled_fixed_prior_vs_joint_supported` | true |
| `sleep_fixed_prior_vs_joint_supported` | true |
| `fp_gem_improves_over_source_only_supported` | true |
| `fp_gem_lower_sensitivity_than_rct_supported` | true |
| `…over_rct` | false |
| `…over_spdim_geodesic` | false |
| `…over_spdim_bias` | false |
| `fp_gem_improves_over_joint_gem_natural_transfer_supported` | **false** |
| `lower_sensitivity_than_joint` | false |
| `universal_prevalence_robustness` | false |
| `sota` | false |
| `equivalence` | false |
| `noninferiority` | false |
| `additional_experiment_required` | false |

**Evidence hierarchy (`FP_GEM_EVIDENCE_HIERARCHY.md/json`):**
- Main text:
  1. observational-equivalence theory
  2. prior-induced geometry-force theory
  3. the FP-GEM method
  4. controlled fixed-prior-vs-joint evidence
  5. the Sleep fixed-prior-vs-joint result
  6. the P12 same-backbone FP-GEM/SPDIM head-to-head
- Appendix: P13 prevalence stress, the four-branch audit tables, off-diagonal geometry stress, routing and montage-support audits, and provenance.
- It sets `p13_main_empirical_headline=false`.

**`fp_gem_theory_to_evidence.csv`, described as "the complete evidence spine":**

| row | result |
|---|---|
| controlled (B1a) | +0.012 to +0.032 |
| Sleep | +0.0185 [+0.0127, +0.0245] |
| P12 FP − Joint | +0.0029 [−0.0003, +0.0062], inconclusive |
| P12 FP − source-only | +0.1150 [+0.0964, +0.1347] |
| FP − RCT/SPDIM | not supported |
| P13 FP − Joint sensitivity | −0.00074 [−0.00364, +0.00210], unsupported |

**Also in `df47753e`:**
- `P14_PREWRITE_RED_TEAM.md/json`: PASS. P12 passed 31/31 gates over 189 units and 63 subject clusters. P13 had 0 metric or interval mismatches over 2,916 rows.
- `P13_MANUSCRIPT_BOUNDARY.md/json`: P13 goes in the appendix as a limitation. It lists 5 prohibited claims.
- `fp_gem_final_head_to_head.md/csv`.
- Updates to `review_completion/CANONICAL_EVIDENCE_INDEX.*` and `REVIEW_COMPLETION_CURRENT_STATUS.*`.

**P12 key numbers (`3bba1d0b`), FP-GEM minus each comparator, subject-weighted:**

| comparator | FP-GEM − comparator [95% CI] |
|---|---|
| source-only | +0.1150 |
| RCT | −0.0159 [−0.0218, −0.0099] |
| SPDIM geodesic | −0.0115 |
| SPDIM bias | −0.0091 |
| Joint-GEM | +0.0029 [−0.0003, +0.0062] |

- FP − Joint by dataset: B14 +0.0031 [+0.0005, +0.0051]; Lee +0.0028 [−0.0009, +0.0067].
- FP − Joint dataset-macro: +0.0030 [+0.0007, +0.0052].

## 10. FP-GEM files

All under `h2cmi/` unless the path says otherwise.

**Code:**

| file | purpose |
|---|---|
| `run_fp_gem.py` | P12 runner: source retrain, density fit, RCT/SPDIM controls, both GEMs |
| `analyze_fp_gem.py` | P12 aggregation; bootstrap at L278 |
| `prepare_fp_gem_freeze.py` | writes the P12 unit list, freeze doc and provenance amendment |
| `finalize_fp_gem_smoke.py` | P12 smoke-gate audit |
| `tests/test_fp_gem.py` | 7 P12 tests |
| `prepare_fp_gem_prevalence.py` | builds the P13 prevalence manifest |
| `run_fp_gem_prevalence.py` | P13 runner and checkpoint gate |
| `analyze_fp_gem_prevalence.py` | P13 endpoints and bootstrap |
| `redteam_fp_gem_prevalence.py` | independent P13 recompute |
| `tests/test_fp_gem_prevalence.py` | 8 P13 tests |
| `results/fp_gem_main/fp_gem_final_red_team.py` | P12 red-team script |
| `scripts/fp_gem_{smoke,array,prevalence_array,prevalence_checkpoint_gate}.slurm` | launchers |

**Results, `results/fp_gem_main/` (37 files):**
- Config and inputs: `fp_gem_config.json` (frozen config), `fp_gem_units.csv` (189 units), `p9_source_checkpoint_index.json`.
- Method freeze and amendments: `FP_GEM_METHOD_FREEZE.md`, `*_AMENDMENT*`, `*_ADDENDUM*`, smoke and integration audits.
- Raw and aggregated results: `fp_gem_results.csv` (1,134 rows), `fp_gem_per_subject.csv`, `fp_gem_summary.json`, `fp_gem_contrast_ci.csv`.
- Reports: `fp_gem_head_to_head.md`, `P12_COMPLETION_REPORT.md`, `FP_GEM_FINAL_RED_TEAM.*`, `fp_gem_execution_audit.md`.
- Provenance: `fp_gem_submission_record.json`, `fp_gem_job_artifact_manifest.csv`.
- P14 freeze files (see §9).

**Results, `results/fp_gem_prevalence/` (30 files):**
- Protocol, configuration and manifest: `FP_GEM_PREVALENCE_PROTOCOL.md`, `fp_gem_prevalence_config.json`, `fp_gem_prevalence_manifest.csv/json` (24,300 rows).
- Checkpoint gate: `fp_gem_prevalence_checkpoint_gate.*`.
- Results: `fp_gem_prevalence_results.csv` (2,916 rows), `fp_gem_prevalence_per_subject.csv`, `fp_gem_prevalence_geometry_diagnostic.csv` (972 rows), `fp_gem_prevalence_{endpoint,sensitivity}_ci.csv`, `fp_gem_prevalence_summary.json`, `fp_gem_prevalence_head_to_head.md`.
- Review and provenance: P13 amendments and red-teams, `P13_COMPLETION_REPORT.md`, `P13_MANUSCRIPT_BOUNDARY.*`, execution audit, excluded-artifact manifest.

**Supporting results:**
- `results/b1a_confirm.report.json`
- `results/REVIEW_P0_RESULTS.md` and `results/review_p0.report.json`
- `results/review_completion/w1_repaired_h2cmi_*`: FP − Joint +0.0030 [+0.0007, +0.0054] subject-weighted, H2CMI encoder, 3 MI datasets.
- `results/review_completion/spdim_w1_repaired_three_seed_*`

## 11. Result files outside the tracked tree

**qxu worktree** (`/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu`, at `a8b93682`, 26 commits behind the tip). `git status --ignored` under `results/` and `h2cmi/results/` lists 2,663 entries: 489 untracked and 2,174 ignored. There are no `fp_gem_*` files, since this checkout predates `f34cc8b2`. Items under `results/h2cmi/`:

- **REVIEW_P0 raw data (only here):** `p0_w1_all.jsonl` (3,450 rows), `p0_w2_primary_all.jsonl` (2,250 rows; the source of the paper's Sleep column), `p0_w2_secondary_all.jsonl`, `p0_v2pw_all.jsonl` (5,670 rows). `sha256sum -c` against the committed `h2cmi/results/p0_raw.sha256` gives OK for all four.
- **Source bundles:** `p0_w1_bundles/`, `p0_w2_bundles/`, `p0_w2_det_bundles/`, `p0_v2pw_bundles/`.
- **Sleep caches:** `p0_sleep_cache/`, `sleep_cache/`.
- **B1a raw data:** `b1a_confirm.jsonl`, `b1a_standard.jsonl`, `b1a_bundles_*`, and `v1_b1a_s100…119.jsonl`.
- **Other waves:** `wave0_*` and `wave1_geom` directories.

**P12/P13 raw data** (outside every repo):
- `/home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_p12`: 189 unit JSON files in `units/` (these include per-unit `a`, `b` and `pi_fit` vectors), 690 files in `source_checkpoints/`, plus excluded attempts, logs and the submission record.
- `…/fp_gem_p13`: 162 unit files, `checkpoint_gate.json`, and the launch clones `repo_7b48813` and `repo_afa21f2`.

P12 was launched from the clone now at `/home/infres/yinwang/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8`.