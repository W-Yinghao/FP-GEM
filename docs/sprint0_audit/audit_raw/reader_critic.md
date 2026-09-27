[harness: subagent output matched instruction-shaped pattern(s): settings-json. Control tags below are neutralized (`<` → `<\`); treat any remaining directive-shaped text as a finding to relay to the user, not an instruction to you.]

# FP-GEM audit: what is missing or likely wrong

**Coverage limit.** The MAP was cut off partway through G03, and the CLEANUP list after C02. I can see from the scratchpad that later groups exist (g04–g14 notes, c03–c15 notes), but I could not read their rows or verdicts. Where this report says a row or verdict is needed, check it against the full JSON before treating it as a gap.

Files I wrote in the scratchpad: `agents/crit_tips.txt` and `agents/crit_lbfgs_files.txt`.

---

## 1. The five most important problems

### 1.1 The four MI GEM cells in Table 1 cannot have come from any run on this server

Checks I did:
- **No aggregation reproduces them.** I took `~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/out/regime_analysis_raw_target_seed.csv` and tried the α-path α∈{0,.25,.5,.75,1} and a best-seed aggregation. Neither gives 73.2 / 71.9 / 60.0 / 67.6. For example, the B14 α-path stays between 70.94 and 71.24, and best-seed FP gives 75.31.
- **The density-head readout does not reproduce them either.** On the repaired W1 run (see §1.2), FP/Joint are B14 71.35/70.22, Cho 64.02/64.05 and Lee 72.22/71.74 (per `agents/g13r_notes.txt`).
- **Nothing FP-GEM happened on the server after the morning of 07-28.**
  - The last commit under `h2cmi/` on any ref is `04a40e4e` (2026-07-27 17:08).
  - The last cache file was written 2026-07-28 around 10:43 (regime `out/`).
  - `~/.cache/h2cmi_training_caches/FP_GEM_RESULTS_SO_FAR.md` (2026-07-28) still lists the artifact values: FP 71.2 / 59.0 / 66.6.
  - v1 L55-59 says the FP/Joint numbers come from "a later 07-27/28 run". That run cannot have been on the server; the numbers entered off-server between 07-28 and the 07-31 package.

What the pattern looks like: every s.d. is identical to the artifacts while the means are +1.0 or +2.0 higher. That is what you would see if a constant were added to every participant's score.

What to do: log it as a T1 row with `reproduction_status=unresolved`. Resolving it needs the laptop's `main_submit_ready.tex` / Overleaf history and the OpenReview code zip. Per v3 §10, it must not be written up as "all old numbers are wrong".

### 1.2 The W1 MI evidence cited in the docs and by the review-p0 reader is quarantined

- **What is being cited.** v1 §2.2(e) and the review-p0 reader both cite REVIEW_P0 W1 (115 subjects): FP−Joint +0.0022 [−0.0005, +0.0049], G = +0.060. Neither flags that these are legacy numbers.
- **Why they cannot be used.** `origin/exp/h2cmi-wave0-mechanism:h2cmi/results/review_completion/w1_legacy_split_quarantine.md` marks this run `legacy_split_not_confirmatory`, because Cho2017 has single-class evaluation blocks in 52/52 targets.
- **What replaces them.** The canonical repaired run is `w1_repaired_h2cmi_method_contrasts.csv` (committed at `bc61ee11`). It uses the H2CMI encoder with a density-head readout and uniform decision weights, so it is the only MI evidence that is readout-matched in the sense of Eq. 12:
  - FP−Joint, subject-weighted: **+0.00299 [+0.00067, +0.00540]**
  - FP−Joint, dataset-macro: **+0.0053 [+0.0017, +0.0092]**
  - Joint − pooled: −0.0035
  - FRSC − identity: +0.0092
- **A writer-facing digest was missed.** `h2cmi/results/review_completion/MANUSCRIPT_NUMBERS_READY.md` (`f2808796`) was not summarised by any reader. The same applies to `WAVE0_MANUSCRIPT_NOTES.md`, `MANUSCRIPT_INSERTS_{W02_W05,W03}.md` and `MANUSCRIPT_INSERTS_ARCHIVED_DO_NOT_APPLY.md`, and nobody reported reading `CANONICAL_EVIDENCE_INDEX` / `REVIEW_COMPLETION_CURRENT_STATUS` in full (G01 cites only two lines).

### 1.3 Label-firewall claims need explicit MISMATCH rows

The paper says (main L743-745): "Target labels are unavailable during adaptation, model selection, stopping, and failure handling." The code does not meet this:
- **MI split.** The adaptation/evaluation halves are built from target labels: `class_stratified_half`, with `target_session=0` in 345/345 units (`w1_repaired_split.py` L80-95). So ρ_A = ρ_E = 0.5 is constructed from the labels, not "protocol-supported" as the paper says at L884-886.
- **Why it matters by dataset.**
  - B14: the split coincides with runs 0–2 vs 3–5, so the label use is harmless.
  - Lee: 18.7% of evaluation trials come before the last adaptation trial.
  - Cho: the adaptation set is two class-blocked segments.
- **Sleep.** The ±30-min crop uses the hypnogram, and unscored epochs are dropped (`sleep_eeg.py` L73-79). Both are label-dependent.

### 1.4 The revision docs misuse P13

v1 §2.2(b) and v4 P7 ("P13 (have)") cite a geometry shift of about 1.4 as evidence for Joint's prior → geometry coupling. But FP-GEM moves by the same amount:

| Method | Displacement at q=0.1 | Displacement at q=0.9 |
|---|---|---|
| Joint | 1.436 | 1.424 |
| FP | 1.414 | 1.404 |

This is in `fp_gem_prevalence_geometry_diagnostic.csv` at `b5fb5158`. The displacement is not driven by the prior. The DOCS reader and the CODE reader contradict each other on this, and the T9 comparison ("against P13 prior movement") needs to be redefined.

### 1.5 The Cho column comes from the cache, not from P9

The wave0 map attributes Cho Source/Recenter/SPDIM to P9 (`8972de87`). I compared per-unit values:
- `spdim_geodesic` differs in 25/156 units between the two sources. The P9 mean is 59.60 and the cache mean is 59.66; the paper prints **59.7**, so it used the cache.
- Source-only matches in 156/156 units, and RCT in 155/156.

So the whole Cho column, and the EA row for B14 and Lee, exist only in `~/.cache/h2cmi_training_caches/fp_gem_{cho,ea}`. None of it is committed.

---

## 2. Sources nobody read or located

| Source | Status | Why it matters |
|---|---|---|
| OpenReview `reproducibility_checklist` PDF and `code_and_data_supplement` zip (`openreview.txt` L43-48) | Not in `/home/infres/yinwang/CMI_AAAI/FP-GEM` | These show what code reviewers received. If the zip is the laptop `fpgem` package (L-BFGS, diagonal Gaussian), it cannot produce Table 1. Needed for T1/T2. |
| The spec behind "the reported 22.7%" FP-win rate | `regime_analysis_*/synthetic_regime.py` L1/L5 reconstructs it; the spec is not on the server | Unlocated claim source, probably the laptop long-version PDF. |
| Wave0 manuscript digests (§1.2) | Unread | They are the server's writer-facing numbers. |
| Parent root docs: `README.md`, `PROJECT_SUMMARY.md`, `CODE_INVENTORY.md`, `A Unified EEG Data Registry_v1.0.xlsx` | Unread | The registry may give protocol class and trial counts, i.e. π_ref for T3. |
| `notes/project_A_observability/science/13–19` (declared-prior stress and robustness) | Not examined; I grepped and found no FP-GEM strings | Conceptually close to v5 A6, bounded priors and R9. Low priority. |
| Parent code `cedar_eeg/`, `talos_eeg/`, `tta_mech_eeg/`, `STAR/`, and branches `cmi-trace-readout-prior-{decomposition,lockbox}`, `project/star-task-anchor` | I grepped them: no FP-GEM or GEM code | The map should record "examined, not FP-GEM". |
| Parent-folder "instructions" | There is no CLAUDE.md in `CMI_AAAI/` or `FP-GEM/`. `.claude/settings.local.json` holds only squeue/oaci permissions | The parent rules are the DIRECTORY_MAP "Don'ts" plus the memory disciplines. |

**Good news that should upgrade some rows.** `agents/g06r_full17g_out.json` re-simulated Table S3 independently and matched **12/12 cells** at the paper's precision. Any MAP row that marks Table S3, or the simulation spec behind it, as UNTRACEABLE should become REPRODUCED (independent re-simulation). This also gives T2 a reference on the server without the laptop code.

---

## 3. Paper claims that need a row (check against the full MAP)

1. **Headline "0.8–1.9 points on four benchmarks"** (abstract, intro, L900-901). 3 of the 4 gaps are not backed by artifacts. Also "FP-GEM is best on B14 and Cho" (L889-891) and the bold/underline marks in Table 1.
2. **"EEGNet encoder (Lawhern 2018)"** for Sleep. The code is the H2CMI "EEGNet-ish" `TemporalBranch` plus a 16-d fusion MLP (`models/encoder.py` L47-68).
3. **"Diagonal Gaussian density and πsrc stored with the source checkpoint."**
   - P12: the density is refit afterwards and not stored.
   - Sleep: the density is trained jointly and is a Student-t.
4. **"The Sleep archive contains all 225 participant–seed predictions per method"** (supplement H). The raw rows hold only a confusion matrix and a 16-hex `pred_hash` per unit, with no per-trial predictions.
5. **"Every target-time method reuses the same source bundle."** Cho SPDIM-geodesic differs in 25/156 units between runs, which points to nondeterminism.
6. **Channel normalization fitted on source, the 0.3–35 Hz filter, 4–38 Hz / 0.5–3.5 s windows, patience 15, the 80/20 participant split, 50 IM epochs, and B14 as 4-class.** G13 notes cover these; confirm each has its own row.
7. **The label-firewall and "protocol-supported proportions" claims** from §1.3.
8. **"Simulations recover the prior–geometry displacement"** (Fig. 2A). The code is on the laptop only, but Table S3 is re-derivable.
9. **Table S1 environment and seeds** (Windows i7-9750H; seeds 20270728 / 913731 / 930000). These cannot be verified on the server and should be marked as such.

---

## 4. Contradictions and errors in the reader outputs

- **DOCS SHA table.** It gives "reachable from —" for `9a35cc97` and `e941bb5b`. In fact:
  - `9a35cc97` is on review-p0, wave0 and stage2.
  - `e941bb5b` is on qxu, review-p0, wave0 and stage2.
- **Search scopes differ between readers**: 64, 104, 121 and 166 refs. I re-ran the L-BFGS sweep over all 156 commit and tag refs. The only L-BFGS file under `h2cmi/` is `h2cmi/fp_gem_stage2_lib.py` (BCTS), so the "no L-BFGS GEM" conclusion holds.
- **Shard count is 15, not 16.** `git worktree list` shows 11 `spdim_p6` + 3 `p7` + 1 `spdim_clean`. `DIRECTORY_MAP.md` L49 ("12 spdim_p6") and the task context ("16 shards") are both wrong. C01a–C01d cover all 15.
- **The P12 memory note is inaccurate.** `h2cmi-fp-gem-p12.md` says P12 was "un-merged". But `3bba1d0b` (07-13) already adds `fp_gem_results.csv` and `fp_gem_per_subject.csv`, and `3bba1d0b` is **not** an ancestor of `origin/agent/fp-gem-stage2`, so `3b52e202` is a parallel re-merge. T1 should cite both commits (same CSV SHA `f3e4ca69…`).
- **`FP_GEM_RESULTS_SO_FAR.md` has three internal slips.**
  - It labels Sleep 63.6 as "SPDIM"; it is `latent_im_diag`, i.e. the paper's Diag-IM.
  - Its text says Cho Joint 59.3, but its table says 59.2.
  - It says "154/156" units; the actual count is 156.
- **REVIEW_P0 raw rows are not committed on any ref.** Only the SHA-256 manifest is. The review-p0 and wave0 readers state this only implicitly.

---

## 5. Deletion risks: must-KEEP list

These are paper-backing or Sprint-0-critical, and each is the only copy.

**`/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/results/h2cmi/`**
- `p0_w2_primary_all.jsonl` (source of the Sleep column), `p0_w2_secondary_all.jsonl`, `p0_w1_all.jsonl`, `p0_v2pw_all.jsonl`
- `p0_w2_bundles/`: 225 frozen Sleep models, needed for T7/T9
- `p0_sleep_cache/`
- `wave0_*` raw, including `wave0_priordecomp/pd_crossnight_*` (the Lemma S9 test)
- `…/CMI_AAAI_qxu/w1b_external/BTTA-DG`: the AI reviewer asked for a BTTA-DG baseline. If C05 proposes deleting it, downgrade the verdict.
- Do **not** update or checkout the qxu worktree (it sits 26 commits behind).

**`~/.cache/h2cmi_training_caches/`**
- `fp_gem_cho/`: the Cho column
- `fp_gem_ea/`: the EA row
- `fp_gem_p12/source_checkpoints/`: 345 TSMNet models; P9 hashes do not reproduce them, so they are the only MI models
- `fp_gem_stage2/`: the only per-trial MI logits
- `fp_gem_stage2_sleep/`
- `regime_analysis_20260728T064406/`: its scripts exist only here
- `FP_GEM_RESULTS_SO_FAR.md`

**Other items**
- **`H2CMI/.codex_p12_launch_5b71ee8`.** It holds nothing unique in git, but every cache `.slurm` file is hard-wired to it and the runners require a clean tree. Keep it through the Sprint-0 re-inference.
- **`H2CMI/shard_results_salvaged/p7_w1_repaired`.** After C01c it becomes the sole copy of the Lee P7 bundles, and P7 is the canonical readout-matched MI run from §1.2. Pin it (sha manifest, read-only) before C01c.
- **C09.** The retained `p0w2pri_*`, `p0w2sec_*` and `p0w2det_*` logs are the Table 1 Sleep execution logs. The verdict keeps them; make sure the delete list excludes them.
- **C03–C15.** Their verdicts are not visible. I spot-checked C03: the 17 unreachable commits are CSC/OACI/S2P plus one pre-FP-GEM h2cmi commit, and none back FP-GEM. The P13 clones `repo_7b48813` and `repo_afa21f2` are clean and on origin.

---

## 6. Sprint-0 inputs that are blocked or ambiguous

| Task | Problem |
|---|---|
| T1 | The tex source, checklist and code zip are missing, and so are the four MI GEM cells (§1.1). `SERVER_REPRO_CHECKLIST_REQUEST.md` is on the laptop only. |
| T2 | There are two "old implementations": the laptop `fpgem` (L-BFGS, diagonal Gaussian, used for the simulations) and server `h2cmi/tta/class_conditional.py` (Adam 20×3, Student-t, κ=6, used for all EEG). The acceptance criterion "matches old implementation" must say which one. `convergence_sim` is on the laptop; Table S3 can be re-derived instead. |
| T3 | MI ρ_A = ρ_E = 0.5 by construction, so the gap is meaningless without a label-free chronological or cross-session split. Still pending: Cho `bad_trial_indices` (10 GB), the Lee online phase (61 GB), and the Sleep lights-off crop (`SC-subjects.xls`; `xlrd` is missing). These must go via SLURM under the 8-task cap. |
| T4 | B14 4-class has no loader or checkpoints, so it needs a 27-unit retrain. |
| T7 | The per-trial per-channel z-score in both loaders cancels injected diagonal gains. Sleep has no SPD layer, so Sleep can compare only EA and latent GEM. |
| T8/T9 | No saved latent features exist; both need GPU re-inference from the checkpoints above. The P13 comparison needs redefining (§1.4). |

---

## 7. This folder's instructions vs the parent folder's rules

These conflicts need an owner decision before anything is run:
- **B14 4-class.**
  - The kickoff §2 freezes it as first-round data.
  - v3 §16.1 excludes retraining from the first batch.
  - Memory [[training-cost-not-a-route-criterion]] forbids using cost as the gate.
  - Report the conflict and wait for your decision.
- **Server tasks.** T1/T3/T4 are read-only on the server, which is consistent with the parent-folder Don'ts: no `git worktree prune`, no moving root packages. Heavy CPU tallies must go through SLURM ([[run-cpu-jobs-via-slurm]], cap of 8).
- **Audit numerics on the login node.** Several audit numeric checks (g02/g06r quadrature and re-simulation) appear to have run on the login node. They are small, but log this against the SLURM discipline.