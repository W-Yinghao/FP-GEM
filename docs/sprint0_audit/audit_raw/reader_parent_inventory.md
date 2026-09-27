## CMI_AAAI parent-folder inventory and FP-GEM relevance (read-only audit, 2026-09-26)

Root: `/home/infres/yinwang/CMI_AAAI`. The main worktree is on `agent/cedar-eeg-p0` @1ab08225. There are 41 top-level entries. Sizes are `du -sh` on disk, with apparent size in brackets where it differs a lot. `git worktree list` shows 45 worktrees: the main one plus 44 admin entries in `.git/worktrees`. All 44 gitdir pointers currently resolve and none are prunable or locked. Even so, never run a bare `git worktree prune` (user rule). `ACAR_V4_COMPAT_PREFLIGHT_5237378` now sits nested inside `ACAR/CMI_AAAI_acar/`, not outside the repo as `DIRECTORY_MAP.md` says. No SLURM job is running from any CMI_AAAI path: `squeue` shows only `CS_QMI/ssl_pilot` jobs.

### Top-level entries
| entry | size | what it is | research line | FP-GEM relevance |
|---|---|---|---|---|
| `.git/` | 181M [116M] | main object store. It holds every FP-GEM commit via `origin/*`, 121 refs, 2 stashes (oaci, csc), tags incl. `H2CMI_METHOD_FREEZE` (27601945), and 10 `refs/codex/turn-diffs/*` | all | **support** |
| `.claude/` | 14K | `settings.local.json` | tooling | unrelated |
| `.gitattributes` `.gitignore` | tiny | tracked | all | support |
| `.watch_baseline.txt` `.watch_baseline2.txt` | 12K | Tri-CMI watcher baselines (tracked) | Tri-CMI | unrelated |
| `A Unified EEG Data Registry_v1.0.xlsx` | 374K | tracked dataset registry | general | unrelated |
| `ACAR/` | 76M | `CMI_AAAI_acar` [branch acar] plus nested detached worktree `ACAR_V4_COMPAT_PREFLIGHT_5237378` | ACAR | unrelated |
| `CEDAR_TALOS_TTAMECH/` | 14K | README pointer to the root packages | CEDAR/TALOS/TTA-MECH | unrelated (TTA-MECH audits SPDIM, so tangential) |
| `CIGL/` | 4.5G | cigl_r123 756M, dcigl 234M, fcigl 34M, metacmi 3.5G, bootstrap_docs | CIGL/MetaCMI | unrelated |
| `CMITRACE/` | 5.1G | cmitrace 1.8G [agent/cmi-trace-cross-session-fullstrength @a72f533b], infoladder, readout, readout_prior 3.2G, theoryspectrum | CMI-Trace | unrelated. It is the correct home for the misfiled `H2CMI/CMI_AAAI_p12_extract` and `H2CMI/paper_data` |
| `CODE_INVENTORY.md` `PROJECT_SUMMARY.md` `README.md` `Tri-CMI_EEG_DG_AAAI_research_plan.docx` | <100K | Tri-CMI-era docs (tracked, stale) | Tri-CMI | unrelated |
| `CSC/` | 189M [484M] | csc plus `_frozen/` (3 detached worktrees) | CSC | unrelated |
| `DIRECTORY_MAP.md` | 5K | reorg map | meta | support (has inaccuracies; see below) |
| **`FP-GEM/`** | 1.6M | submitted main PDF, supplement PDF, OpenReview print, revision plans v1 to v5, Sprint-0 kickoff | FP-GEM journal revision | **core** (user docs) |
| `FSR/` | 1.7G | fsr 40M, rq4 1.7G | FSR | unrelated |
| **`H2CMI/`** | 8.4G [11G] | FP-GEM/H2-CMI evidence plus launch clones and shards (details below) | H2-CMI / FP-GEM | **core/support** |
| `OACI/` | 137M | CMI_AAAI_oaci plus slurm_logs | OACI | unrelated |
| `PROJECT_B/` | 52M | projectB, projectB_next | refusal router built on frozen h2cmi | unrelated (tangential) |
| `REFERENCE/` | 169M | papers (43 PDFs, incl. TSMNet), repos (SCLDGN, SupContrast, TSMNet), loose_pdfs | reference | support (FP-GEM runs used `~/.cache/h2cmi_external/SPDIM_1b0de0c…`, not `REFERENCE/repos/TSMNet`) |
| `S2P/` | 5.8G | s2p 2.3G, s2p_b1_launch 1.4G, s2p_faced 740M, s2p_launch, s2p_d1_launch 1.3G (clone), s2p_panel2_launch (clone) | S2P | unrelated |
| `STAR/` | 2.9G | star 37M, star_runtime 2.8G | STAR | unrelated |
| `TOS/` | 4.8G | CMI_AAAI_tos [paper-v4-integration] | TOS-CMI | unrelated |
| `TRICMI_LPC/` | 128M [298M] | archive/lpc-cmi-failed 112M plus 1396 logs | Tri-CMI/LPC | unrelated |
| `_TRASH/` | 2.3M | stale acar/oaci/csc/tos_cmi stubs, empty configs, pycache-only tests, .pytest_cache | misc | unrelated (verified redundant; see candidate C12) |
| `_reorg_move.sh` | 4K | script that produced the 2026-08-30 layout | meta | support |
| `analysis/` `synthetic/` | ~0.8M | Tri-CMI analysis and Milestone-1 simulator | Tri-CMI | unrelated. The FP-GEM controlled-Gaussian sims (Fig 2, Tables S1–S4) are **not** here |
| `cedar_eeg/` `talos_eeg/` `tta_mech_eeg/` | ~2.2M | current branch line (tracked) | CEDAR/TALOS/TTA-MECH | unrelated |
| `cmi/` | 2.1M | Tri-CMI harness (tracked) | Tri-CMI | unrelated (ancestor) |
| `h2cmi/` | 5.4M | root h2cmi package at the Project-A version (last change 183f27fc, 2026-07-07). It has **no** FP-GEM code (no `run_fp_gem.py`); 159 ignored pycache files | H2-CMI | support |
| `notes/` | 17M | mixed notes (for example `hierarchical_D.md`) | mixed | support |
| `results/` | 29M | dualpc/cedar/talos/tta_mech/cigl results; no FP-GEM results | mixed | unrelated |
| `scripts/` | 1.3M | SLURM launchers | mixed | support |

### H2CMI/ in detail
| sub-entry | size | git state | content | verdict |
|---|---|---|---|---|
| `CMI_AAAI_qxu` | 7.1G | worktree on local `exp/h2cmi-wave0-mechanism` @a8b93682 (26 commits **behind** origin tip df47753e); 0 modified tracked files; 489 untracked plus 2385 ignored | `results/h2cmi` 4.1G: Wave0/W1/W2/V2P/REVIEW_P0/B1A/B2 raw bundles. 4207 of 4244 non-pycache untracked files are **not in any git ref** (hash-checked against 4 H2CMI refs). Also `p0_sleep_cache` 3.1G, `sleep_cache` 696M, and `w1b_external/BTTA-DG` 3.0G (data 2.9G, SincAdaptNet ckpts 41M, xlsx, tar, patch) | **CORE, keep** (only the sub-parts in C04–C06 and C13 are candidates). Its tracked code is pre-FP-GEM |
| `.codex_p12_launch_5b71ee8` | 132M | full clone, branch `agent/fp-gem-stage2` @04a40e4 (= origin/agent/fp-gem-stage2 04a40e4e); 0 commits missing from the main repo incl. reflog; clean tree plus pycache | execution checkout for the P12, Stage-2, Sleep Stage-2, Cho, EA and regime fleets | code redundant; **defer** (C03) |
| `.codex_p12_launch_f34cc8b` | 54M | full clone @f34cc8b2 (in origin); clean | used only by the superseded smoke job 893416 | redundant (C02) |
| `_frozen_shards/` (16) | 477M | detached @6a6e5b77 ×11, @ab93820d ×3, @493f6499 ×1 (directory named `spdim_clean_a8b9368` but its HEAD is 493f6499), plus 3 P6 shards with no untracked files at all; all commits are in both origin FP-GEM branches | outputs salvaged | redundant except 57 logs (C01) |
| `shard_results_salvaged/` | 57M | untracked | 16 SPDIM P6 audit/csv plus 495 P7 files. The 486 Lee P7 bundles are **disjoint** from `~/.cache/…/p7_w1_repaired_bundles_bc61ee1` (183 bundles) | **keep** (canonical copy) |
| `CMI_AAAI_p12_extract` | 707M | detached @a72f533b, the same commit as the CMITRACE branch `agent/cmi-trace-cross-session-fullstrength` | **not FP-GEM.** This is the CMI-Trace/TOS AAAI "P12 supplement extraction" (`tos_cmi.run_eeg_frozen_pilot`). About 414 of 433 `tos_cmi/results` files (det_verify, eeg_frozen_v2, v2det, 69 of 88 eeg_frozen; ~650M) exist nowhere else. The `repos` symlink dangles (→ `/home/infres/yinwang/CMI_AAAI/repos`) | **MISFILED: move to CMITRACE/, do not delete** |
| `paper_data/` | 564K | untracked | CMI-Trace supplement extraction (nullspace artifact, 11-cell deployment table, figs A6/A9) | **MISFILED: move to CMITRACE/** |

### FP-GEM data outside the repo (referenced by committed code; not deletable)
- `~/.cache/h2cmi_training_caches` (381M) holds the analyzer default raw roots (`h2cmi/analyze_fp_gem.py:449,451`, `analyze_fp_gem_stage2*.py`, `run_fp_gem_cho.py:110`, `run_ea_b14_lee.py:52`, `analyze_fp_gem_prevalence.py:926`):
  - `fp_gem_p12`: 345 source checkpoints incl. Cho, 189 units, `submission_record.json`.
  - `fp_gem_p13`: 162 units plus launch snapshots `repo_7b48813` and `repo_afa21f2`.
  - `fp_gem_stage2`.
  - `fp_gem_stage2_sleep`: 196/225 units, never aggregated.
  - `fp_gem_cho`: 156.
  - `fp_gem_ea`: 189.
  - `regime_analysis_20260728T064406`: runner, analyzer and results are **not committed anywhere**.
  - `FP_GEM_RESULTS_SO_FAR.md`: not committed.
  - `p7_w1_repaired_bundles_bc61ee1`, `p8_*`, `p9_*`: SPDIM baselines.
- `~/.cache/h2cmi_external/SPDIM_1b0de0ccd4c48a4ff28f087b866a0b671b029c39` (6.2M): the official SPDIM/TSMNet code used by the runs.
- `~/slurm_logs`: 23,602 loose H2CMI-era files (16.9M apparent) plus 259 launch `.slurm`/`.py` scripts, only 1 of which is in git. Its 22 subfolders belong to other projects.
- Raw data: `/projects/EEG-foundation-model/datalake/raw` (Sleep-EDF at `sleep-edf/sleep-cassette`).
- No `/scratch/PERSO/yinwang` exists.
- `~/cmi_epoch_cache` (19G; Shin2017A/Stieger2021) is not FP-GEM.

### FP-GEM code on git (the code is not named FP-GEM in the paths; it lives in `h2cmi/`)
- `origin/exp/h2cmi-wave0-mechanism` @df47753e: P13 prevalence stress (b5fb5158), official-SPDIM eval (3bba1d0b), `FINAL_FP_GEM_STORY_FREEZE.md`, `FP_GEM_EVIDENCE_HIERARCHY.md`. It has 8 commits not in stage2.
- `origin/agent/fp-gem-stage2` @04a40e4e: P12 analyzer outputs (3b52e202), Stage-2 plus gate (a39a93a2/1ce61180), Sleep Stage-2 (687003ff/722e33cd), Cho (4be89b0d), EA (ab03bd7). It has 22 commits not in wave0.
- The two tips diverged at e6c49156, so **neither is a superset. Keep both.** No local branch tracks `agent/fp-gem-stage2`.
- `exp/h2cmi-review-p0-corrections` @5bc9bf07 (REVIEW_P0 terminal) and `exp/h2cmi-responsibility-qxu` @09e92499 (W1-B e941bb5b) are fully contained in both tips.
- The Gaussian-simulation code and `journal_revision/prechecks/*.py` referenced in the FP-GEM docs are **not on this server**. Per `REVISION_PLAN_TSP_TPAMI.md` they are in the user's local `FP-GEM_AAAI2027/`.

### Paper ↔ artifact mapping
- **Table 1, Sleep column** = REVIEW_P0 W2_primary. See `git show exp/h2cmi-review-p0-corrections:h2cmi/results/REVIEW_P0_RESULTS.md` lines 79–81: identity .657 = Source 65.7, joint_geom .637 = Joint 63.7, fixed_iterative .656 = FP 65.6, Latent-IM-Diag .636 = Diag-IM 63.6. The Sleep EA 65.3 is `review_p0.report.json` W2_primary/source_recolored_ea 0.6530. The supplement's "225 participant–seed predictions" are `H2CMI/CMI_AAAI_qxu/results/h2cmi/p0_w2_bundles` (675 files = 225 × 3), on top of `p0w2_primary/` and `p0_w2_primary_all.jsonl`. Input: `p0_sleep_cache` (75 subjects). Launch scripts: `~/slurm_logs/p0w2*.slurm`.
- **Table 1, MI rows Source/EA/Recenter/SPDIM (all 3 datasets) and Joint-GEM on Cho and Lee** match local artifacts (see `~/.cache/h2cmi_training_caches/FP_GEM_RESULTS_SO_FAR.md` §2):
  - P12: `h2cmi/results/fp_gem_main/fp_gem_per_subject.csv`, raw `~/.cache/…/fp_gem_p12`.
  - Cho: `fp_gem_cho` plus the P9 CSV `h2cmi/results/review_completion/spdim_w1_repaired_three_seed_results.csv`.
  - EA: `fp_gem_ea`.
- **PROVENANCE GAP.** The paper's FP-GEM MI numbers (B14 73.2, Cho 60.0, Lee 67.6) and Joint-GEM B14 (71.9) do **not** match any local artifact. Local values are FP 71.2/59.0/66.6 and Joint 70.9/59.2/66.3. The regime fleet puts FP−Joint on B14 at +0.003. `REVISION_PLAN_TSP_TPAMI.md` §2.1 already says these came from "a later round" whose subject-level outputs are not local. Until this is resolved, **no FP-GEM raw root, launch clone or snapshot should be deleted.**
- **Revision evidence (TSP plan §2.2):**
  - (a) P12: as above.
  - (b) P13: `origin/exp/h2cmi-wave0-mechanism:h2cmi/results/fp_gem_prevalence/` plus `~/.cache/…/fp_gem_p13`.
  - (c) REVIEW_P0: as above.
  - (d) Stage-2: `origin/agent/fp-gem-stage2:h2cmi/results/fp_gem_stage2/` plus `~/.cache/…/fp_gem_stage2` and `fp_gem_stage2_sleep`.
  - (e) V2P_WEIGHTED: qxu `p0_v2pw_bundles` and `p0_v2pw_all.jsonl`.
  - (f) W1-B: qxu `w1b_external` plus `W1B_REPRODUCTION.md` (e941bb5b).
  - Regime analysis: `~/.cache/…/regime_analysis_20260728T064406` (uncommitted).

### FP-GEM/ docs folder (user docs; flag only)
- The md5s of all 9 files are distinct. The 3 PDFs are the only copies on the server; there are no duplicates. `(2)` in `26843_When_Priors_Push_Geometr (2).pdf` is only a download suffix.
- Plan chain: `REVISION_PLAN_TSP_TPAMI.md` (v1) → `REVISION_PLAN_v2_divergent.md` → `FP_GEM_REVISION_v3_review_and_execution_plan.md` (formally retracts v2's endpoint optimality, S(t) rate, universal t⁴, and the oracle "iff") → `REVISION_PLAN_v4_positive_claims.md` (absorbs v3) → `FP_GEM_REVISION_v5_open_research_directions.md` → `EXECUTION_KICKOFF_sprint0.md` (active; lists all earlier ones as predecessors).
- **Archive candidates (move to `FP-GEM/archive/`, never delete):** v1, whose §2 is still the only compiled evidence inventory with SHAs, and v2. Keep v3/v4 in place because they hold the unique derivations and counterexamples.

### DIRECTORY_MAP.md inaccuracies found
1. `H2CMI/CMI_AAAI_p12_extract` and `H2CMI/paper_data` are the CMI-Trace "P12", not FP-GEM P12. The two share a name only.
2. The claim that `_frozen_shards` are "pure redundancy" is true for result files but misses 57 SLURM logs (601K) that were never salvaged.
3. ACAR_V4 is now nested in `ACAR/CMI_AAAI_acar`.
4. Many recorded absolute paths predate the reorg and are now broken: `/home/infres/yinwang/CMI_AAAI_qxu`, `/home/infres/yinwang/CMI_AAAI/.codex_p12_launch_5b71ee8`, `/home/infres/yinwang/CMI_AAAI_p12_extract`, `/home/infres/yinwang/CMI_AAAI_spdim_clean_a8b9368`. They appear in the `~/.cache` slurm files, the P13 `submission_record.json` and `~/slurm_logs` scripts.

Audit scratch (hash lists and the unsalvaged-log list): `/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/inventory/` (`UNSALVAGED_SHARD_LOGS.txt`, `qxu_not_in_git.txt`, `shard_files.sha`, `salvaged.sha`).