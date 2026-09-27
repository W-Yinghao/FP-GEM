# FP-GEM P12 (TSMNet) run and Stage-2: code, results and paper mapping

This was a read-only audit. The only file I wrote is `/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/s2_vs_p12.py`, a CPU check that re-hashes the Stage-2 predictions against P12. For `git status` I set `GIT_OPTIONAL_LOCKS=0`.

## 0. Findings that matter most

1. **The paper's Table 1 FP-GEM rows (and Joint-GEM on B14) do not match the P12 artifacts.** Every other cell matches exactly (details in §6). The mismatched cells are shifted up by exactly +1.0 or +2.0 points, while their s.d. values match the artifacts to 0.1.

   | cell | P12 / Cho artifact | paper |
   |---|---|---|
   | FP-GEM B14 | 71.2 (11.5) | 73.2 (11.5) |
   | FP-GEM Cho | 59.0 (7.1) | 60.0 (7.1) |
   | FP-GEM Lee | 66.6 (9.3) | 67.6 (9.3) |
   | Joint-GEM B14 | 70.9 (11.3) | 71.9 (11.3) |

   - Consequences for the text: the artifact-backed FP−Joint gaps are +0.3 (B14), −0.2 (Cho), +0.3 (Lee), not +1.3/+0.8/+1.3.
   - "FP-GEM is best on B14 and Cho" is false in the artifacts. RCT and SPDIM beat FP-GEM on both; on Cho, FP-GEM is the weakest adapter.
   - I found no artifact in any FP-GEM location that produces the paper values.
2. **The protocol described in the paper (supplement §H, main text lines 733–790) does not match the P12 code.** See the table in §6. Split, density head, GEM optimizer, readout, source split, epochs and SPDIM epochs all differ. No FP-GEM or H2CMI branch contains a GEM implementation that uses L-BFGS.
3. **The authoritative P12 numbers are bit-identical on both branches.**
   - Commit `3bba1d0` on `origin/exp/h2cmi-wave0-mechanism` (2026-07-13, with the original submission record and the 31/31 red team).
   - Commit `3b52e20` on `origin/agent/fp-gem-stage2` (2026-07-25, with a reconstructed submission record).
   - Result CSV SHA `f3e4ca69…` is the same in both.
   - The memory note says the fleet was "un-merged" and that I reconstructed the record. That is inaccurate: wave0-mechanism had already merged it on 07-13.
4. **Much of the evidence exists only in `~/.cache` and is not committed:** Cho, EA, Sleep Stage-2, the regime analysis, and `FP_GEM_RESULTS_SO_FAR.md`.
5. **`CMI_AAAI_p12_extract` and `H2CMI/paper_data` are not FP-GEM.** They belong to the AAAI CMI-Trace/TOS "P12 supplement extraction" (a naming collision). The reorg filed them under `H2CMI/`.

## 1. Code map

**Branch `origin/agent/fp-gem-stage2`**
- Tip `04a40e4e`. It forks from `origin/exp/h2cmi-wave0-mechanism` at `e6c49156` (merge-base).
- Checked out, clean, in `/home/infres/yinwang/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8` (local branch `agent/fp-gem-stage2`).
- Commit chain: freeze `f34cc8b` → provenance amendment `5b71ee8` → smoke `1c39525` → shard `e6c4915` (P12 fleet launch commit) → `2120efa` (Stage-2 pre-registration) … `a39a93a` (Stage-2 results) → `98b63f3`/`2f8d7cc`/`1ce6118` (gate) → `1990b89`/`f4d7f48`/`687003f`/`e23825b`/`722e33c` (Sleep) → `4be89b0`/`1b89a32`/`ab03bd7`/`04a40e4` (Cho and EA).

**Files** (all under `/home/infres/yinwang/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8/`)

| file | role |
|---|---|
| `h2cmi/run_fp_gem.py` (SHA `720b91b1`) | P12 runner. Scope L54–57; `train_source_model` L339; `refit_rct` L545; official SPDIM geodesic/bias L752/L786; Joint `joint_iterative_diag` L827; FP `gen_iterative_diag` L834; 6-method logits L930; labels read only after all fits, L960 |
| `h2cmi/results/fp_gem_main/fp_gem_config.json` (SHA `d44fd98a`) | frozen config |
| `h2cmi/tta/class_conditional.py` | GEM itself: Adam at L229, 3 transform steps per outer iteration at L250, variants at L127/L130 |
| `h2cmi/run_fp_gem_cho.py` | Cho, 7 methods (L19), EA at L88, forced fresh source training at L41 |
| `h2cmi/run_ea_b14_lee.py` | EA for B14/Lee, reload-only |
| `h2cmi/run_fp_gem_stage2.py` | GPU dump; reload by file SHA at L32, npz at L186 |
| `h2cmi/fp_gem_stage2_lib.py` | BCTS (L-BFGS-B at L51, the only L-BFGS anywhere), MLLS L67, shrink L86, chi² gate L152 |
| `h2cmi/analyze_fp_gem.py`, `analyze_fp_gem_stage2.py` (q∈{.25,.5,.75}, 7 arms, 10k bootstrap, seed 20260710), `analyze_fp_gem_stage2_gate.py` (α=0.05), `run_w2_sleep_stage2_dump.py`, `analyze_w2_sleep_stage2.py` (never run) | analyzers and Sleep dump |
| `prepare_fp_gem_freeze.py`, `finalize_fp_gem_smoke.py` | freeze and smoke utilities |
| `h2cmi/tests/test_fp_gem.py` | 7 tests (L23–104) |
| `scripts/fp_gem_array.slurm`, `scripts/fp_gem_smoke.slurm` | SLURM launch scripts |

`run_fp_gem.py`, the config, the analyzer and the test are identical at `5b71ee8`, `e6c4915`, `04a40e4` and `df47753e`.

**P13 prevalence stress (not on the stage2 branch)**
- Lives only on `origin/exp/h2cmi-wave0-mechanism` at `7b48813`/`afa21f2`/`b5fb5158`: `h2cmi/run_fp_gem_prevalence.py` and `h2cmi/results/fp_gem_prevalence/*`.
- The final story freeze `df47753e` is also there: `FINAL_FP_GEM_STORY_FREEZE.md`, `FP_GEM_EVIDENCE_HIERARCHY.md`, `fp_gem_final_head_to_head.md`.

## 2. P12 protocol (as implemented)

- **Methods:** `source_only_tsmnet`, `rct` (paper "Recenter"), `spdim_geodesic` (paper "SPDIM"), `spdim_bias`, `Joint-GEM`, `FP-GEM`. EA was added later: Cho in-runner, B14/Lee in a separate runner. EA here is source-recoloured alignment of the eval trials, `M = R_s^{1/2} R_t^{-1/2}`, not EA-trained sources.
- **Datasets:** BNCI2014_001 (9 subjects) and Lee2019_MI (54). Cho2017 (52) came later via the Cho runner.
- **Units:** 63 subjects × 3 seeds = **189 units** (161 on V100, 28 on A100) and 1,134 result rows.
- **Backbone:** official SPDIM TSMNet at `/home/infres/yinwang/.cache/h2cmi_external/SPDIM_1b0de0cc…` (present, HEAD matches). 4 temporal / 40 spatial filters, 20 subspace dims, 20 epochs, batch 64. Feature: 210-d pre-classifier input.
- **Density:** Student-t, 1 component per class, low-rank 4 plus diagonal, df 8, AdamW for 40 epochs.
- **GEM:** `diag(exp a)z+b`, Adam lr 0.05, 20 outer iterations × 3 steps, trust region 1/1, logdet 1. Joint-GEM uses Dirichlet 5 plus a source anchor. Decisions go through the frozen TSMNet linear classifier.
- **SPDIM:** 30 epochs, lr 0.01.
- **Split:** LOSO over subjects. The target uses the `class_stratified_half` split: first session only (`target_session=0` for every dataset). Target labels are used to build exactly balanced halves: B14 [36,36]/[36,36], Lee [25,25]/[25,25], Cho [50,50]/[50,50].
- **Source train/val:** the last 20% of trials per (subject, class). It is not a participant split.
- **P9 hashes:** 0 of 189 reproduced sources match the P9 state hashes, which are device-dependent. Every source is a fresh exact-config retrain.
- **Provenance:** all 189 units have launch commit `e6c49156`, runner `720b91b1`, config `d44fd98a`. Jobs: smoke 893433, arrays 893448 / 893456 / 893453, merge 909437 = PASS.

## 3. Artifacts on disk

All under `/home/infres/yinwang/.cache/h2cmi_training_caches/`.

| path | contents | size |
|---|---|---|
| `fp_gem_p12/units/*.json` | 189 of 189, status ok. Metrics plus prediction and logits hashes only; no per-trial arrays | 4.9M |
| `fp_gem_p12/source_checkpoints/` | 345 `.pt` + `.json`: 27 B14, 162 Lee, **156 Cho** (the Cho runner writes here too) | 100M |
| `fp_gem_p12/{logs,excluded_attempts/893449_task0,excluded_checkpoints/smoke_893433,smoke.json,submission_record.json,run_merge.slurm}` | logs, excluded runs, reconstructed submission record | (106M total for `fp_gem_p12`) |
| `fp_gem_stage2/units/*.npz+json` | 189 of 189. Per-trial eval/adapt logits for identity/FP/Joint, val logits, responsibilities, y, trial ids. Commits `a2e53a2`/`0527445`/`686d0c1`; jobs 909481/909482/909490/909491/909519/909520 | 9.4M |
| `fp_gem_stage2_sleep/units` | 196 of 225 npz (fp/id/joint probs K=5). Array 910097 was killed by TIME LIMIT on 07-28 02:10. 63 complete targets, 4 partial (60, 71, 73, 76); targets 64 and 68–82 were not reached | 38M |
| `fp_gem_stage2_sleep/sources` | 196 hash-named EEGNet sources (30 epochs, tag `W2S2`) | 47M |
| `fp_gem_cho/cho_target*_seed*.json` | **156 of 156** (not 154 as the status file says), commit `04a40e4`, all fresh sources, 7-method bAcc/acc only | 2.5M |
| `fp_gem_ea/ea_*.json` | 189 of 189, job 912270 | 2.7M |
| `regime_analysis_20260728T064406/` | 345 of 345 units plus `out/statistics.json` and synthetic files; job 913011; scripts live only here | 14M |
| `fp_gem_p13/` | P13, 162 units plus 2 nested git clones `repo_7b48813`, `repo_afa21f2` | 98M |
| `FP_GEM_RESULTS_SO_FAR.md` | consolidated status note (2026-07-28) | — |

**Stale paths.** Every cache `.slurm` file (merge, stage2, sleep, EA, Cho, regime) does `cd /home/infres/yinwang/CMI_AAAI/.codex_p12_launch_5b71ee8`. That path no longer exists after the reorg; the repo is now under `H2CMI/`. The Sleep runner defaults `--cache` to `/home/infres/yinwang/CMI_AAAI_qxu/...`, which now lives at `/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/results/h2cmi/p0_sleep_cache` (3.1G, 75 subjects).

## 4. Key numbers

**P12**, subject-weighted bAcc (`fp_gem_head_to_head.md`)

| method | subject-weighted bAcc |
|---|---|
| source-only | .5572 |
| RCT | .6881 |
| SPDIM-geodesic | .6838 |
| SPDIM-bias | .6814 |
| Joint-GEM | .6694 |
| FP-GEM | .6723 |

| FP-GEM minus | estimate [95% CI] |
|---|---|
| source-only | +.1150 [.0964, .1347] |
| RCT | −.0159 [−.0218, −.0099] |
| SPDIM-geodesic | −.0115 [−.0170, −.0059] |
| SPDIM-bias | −.0091 [−.0154, −.0027] |
| Joint-GEM | **+.0029 [−.0003, +.0062]** |
| Joint-GEM, B14 only | +.0031 [.0005, .0051] |
| Joint-GEM, Lee only | +.0028 [−.0009, .0067] |

**Cho** (cache, my recompute, participant means): source 52.35, EA 52.19, RCT 59.75, SPDIM-geodesic 59.66, SPDIM-bias 59.69, Joint 59.19, FP 58.98.

**EA:** B14 60.13 (11.31), Lee 54.37 (4.31).

**Stage-2 (MI, controlled q, FP geometry, subject-weighted)**
- P1: mlls_shrink − src = +.0501 [.0352, .0651].
- P2: vs oracle = −.0264 [−.0384, −.0159], i.e. 65% recovery.
- P3 (balanced): −.0125 [−.0219, −.0038]. **This fails the safety gate.**
- P4: bAcc spread across ρ arms = 0.
- Gate: G1 −.0062 [−.0123, .0000], G2 +.0111 [.0015, .0210]; false-positive rate 4.8%, detection 33%.
- My check: Stage-2 npz argmax reproduces the P12 prediction hash for RCT, FP-GEM and Joint-GEM in **189 of 189** units. The Stage-2 runner re-fits the geometry rather than reusing stored a/b, which deviates from the pre-registration (§4), but the reproduction is exact.

**Sleep Stage-2**
- No aggregate was ever computed. The target-0 probe showed MLLS hurting.
- My partial recompute (196 units, 67 targets): FP−Joint = +1.84 [+1.29, +2.42] points, 56 of 67 wins. The sources here are fresh W2S2 sources, not the REVIEW_P0 ones.

**Regime analysis**
- The reproduction gate passes: 345 of 345 units match the stored FP/Joint bAcc exactly.
- `d_rho_A ≡ 0` everywhere because the split is class-balanced, so β_rho and the interaction term are degenerate at 0.
- ΔBA (FP−Joint): B14 +.0031, Cho −.0021, Lee +.0028. The FP-favourable cell is −.0011 [−.0062, .0047].

**P13 (Lee, prevalence stress):** FP−Joint sensitivity = −.00074 [−.0036, +.0021]. The primary claim is not supported.

## 5. The clones and the worktree

| location | HEAD | untracked (`status --porcelain --ignored`) | verdict |
|---|---|---|---|
| `H2CMI/.codex_p12_launch_5b71ee8` | `agent/fp-gem-stage2` @ `04a40e4` | only `__pycache__` | **Authoritative** launch clone for smoke, P12 fleet, Stage-2, Sleep, EA, Cho and regime. Every ref exists in the main repo and on origin, so nothing is unique inside it. |
| `H2CMI/.codex_p12_launch_f34cc8b` | `exp/h2cmi-wave0-mechanism` @ `f34cc8b` | only `__pycache__` | Strict subset (ancestor of `04a40e4`). It was the launch directory of pre-amendment smoke 893416, which produced 0 accepted rows. Older runner `10ddeb80` and config `15543cb1`. Redundant. Its remote `/tmp/cmi-p8-finalize.RrfuJf/repo` is gone. |
| `H2CMI/CMI_AAAI_p12_extract` | detached `a72f533b` (`agent/cmi-trace-cross-session-fullstrength`) | `det_frozen.py`, `p12_run_frozen*.sbatch`, `repos` symlink, `p12_logs/` (1.5M), `tos_cmi/results/{det_verify 112M, tos_cmi_eeg_frozen 166M, _v2 15M, _v2det 366M}` | **Not FP-GEM** (TOS/CMI-Trace AAAI supplement). The untracked results are unique; no copy exists elsewhere under `CMI_AAAI`. Do not prune. |
| `H2CMI/paper_data` | — | — | CMI-Trace AAAI supplement (nullspace, deployment tables). Not FP-GEM. |

## 6. Mapping to the paper

Table 1 is at `paper_main.txt` L850–878; supplement §H is at L1197–1299.

**Where each Table 1 cell comes from**

| rows | source | match |
|---|---|---|
| MI Source, EA, Recenter, SPDIM | P12 `fp_gem_results.csv` (B14/Lee), Cho and EA cache | exact |
| Sleep Source 65.7, Joint 63.7, FP 65.6, Diag-IM 63.6 | `h2cmi/results/REVIEW_P0_RESULTS.md` L79 (EEGNet, W2) | exact |
| Sleep EA 65.3 | `h2cmi/results/review_p0.report.json`, `source_recolored_ea` 0.6530 | exact |
| MI FP-GEM rows and Joint-GEM B14 | no matching artifact | **mismatch** (§0) |

**Protocol: paper text versus P12 code**

| item | paper | P12 code |
|---|---|---|
| MI adapt/eval split | earlier session vs later session | first session only, label-balanced halves |
| source validation | participant 80/20 split | per-subject trial tail |
| encoder training | ≤100 epochs, patience 15 | 20 fixed epochs |
| density head | diagonal Gaussian, variance floor 1e-4 | Student-t, low-rank 4 plus diagonal |
| GEM optimizer | L-BFGS, ≤100 iterations, stop on 1e-6, penalty 1e-3, log-scale in [−2, 2] | Adam 0.05, 20×3 steps, trust region / logdet |
| readout | argmax π_dec q_θ,y (density head) | TSMNet linear classifier |
| IM baselines | 50 epochs | 30 |
| sessions | "dependent sessions averaged" | only one session exists |

The OpenReview reviewers asked for paired participant-level CIs. Those already exist in `fp_gem_contrast_ci.csv`, and they show FP≈Joint (CI crosses 0 subject-weighted), not +0.8–1.9. Per-trial inputs for new paired analyses: P12 RCT/FP/Joint via the Stage-2 npz, and Sleep FP/Joint via the Sleep npz (196 of 225). Source-only and SPDIM per-trial outputs were never stored; they would need reload-only re-inference from the persisted checkpoints.