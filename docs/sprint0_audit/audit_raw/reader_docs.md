# FP-GEM revision docs (v1–v5 and Sprint-0 kickoff): contents, current plan, artifact map, and Sprint-0 definitions

I read all six Markdown files in `/home/infres/yinwang/CMI_AAAI/FP-GEM/` in full:

| File | Lines |
|---|---|
| REVISION_PLAN_TSP_TPAMI.md | 389 |
| REVISION_PLAN_v2_divergent.md | 290 |
| FP_GEM_REVISION_v3_review_and_execution_plan.md | 1307 |
| REVISION_PLAN_v4_positive_claims.md | 221 |
| FP_GEM_REVISION_v5_open_research_directions.md | 734 |
| EXECUTION_KICKOFF_sprint0.md | 125 |

All are dated 2026-09-26. Nothing was modified.

## 0. What I checked on this machine, beyond reading

- **v3 reviewed this exact v2.** The SHA-256 of `REVISION_PLAN_v2_divergent.md` (3baeb0af…486b) matches the hash v3 records in its Appendix A.2.
- **Documents referenced but missing from the folder:**
  - The "第二份 / second plan" at `Downloads/FP_GEM_major_revision_plan_20260926.md`. It holds the "six paper≠execution discrepancies" and the "Λ-weighted prior penalty" route B.
  - `fpgem_v2_math_checks.py` and `.json`.
  - Every `journal_revision/prechecks/*.py`.
- **No laptop-side artifact exists on the server.** I searched `git ls-tree` on every branch and ran a find with maxdepth 3. None of these exist anywhere: `journal_revision/`, `prechecks/`, the `fpgem` package, `convergence_sim`, `multiclass_sim`, `optimal_sim`, `mechanism_sim`, `version_b_optimal`, `FP-GEM_AAAI2027`, `submission_2026-07-2*`, `fpgem_v2_math_checks*`. Server-side code lives only in `h2cmi/` on the H2CMI branches.
- **Every commit SHA the docs cite exists:**

| SHA | Date | Commit message | Reachable from |
|---|---|---|---|
| `3b52e202` | 2026-07-25 | "Add P12 FP-GEM analyzer outputs" | origin/agent/fp-gem-stage2 |
| `b5fb5158` | 07-14 | "Evaluate FP-GEM under fixed-reservoir prevalence stress" | origin/exp/h2cmi-wave0-mechanism |
| `5bc9bf07` | 06-29 | "FINALIZER #4 TERMINAL results" | all 3 FP-GEM branches |
| `9a35cc97` | 06-29 | "track REVIEW_P0_MANIFEST.json" | — |
| `687003ff` | 07-26 | Sleep-EDF K=5 dump runner | origin/agent/fp-gem-stage2 |
| `722e33cd` | 07-26 | Sleep-EDF K=5 analyzer | origin/agent/fp-gem-stage2 |
| `e941bb5b` | 06-23 | W1-B BTTA-DG reproduction | — |
| `df47753e` | 07-14 | "Freeze final FP-GEM method story" | origin/exp/h2cmi-wave0-mechanism only |

- **Discrepancy:** v1 calls `9a35cc9` the "analyzer", but that commit only tracks the manifest file.
- **Stage-2 Sleep results are indeed not committed.** On origin/agent/fp-gem-stage2, `h2cmi/results/fp_gem_stage2_sleep/` holds only `FP_GEM_STAGE2_SLEEP_FROZEN.md`. This matches v1 §2.2(d).
- **Freeze documents are only on the remote branch.** `FINAL_FP_GEM_STORY_FREEZE.md`, `FP_GEM_EVIDENCE_HIERARCHY.md` and `P14_PREWRITE_RED_TEAM.md` (each with a .json) sit at `h2cmi/results/fp_gem_main/` on **origin/exp/h2cmi-wave0-mechanism only**. The local branch, 26 commits behind, lacks them.
- **Cho and EA provenance lead for T1.** origin/agent/fp-gem-stage2 carries these commits from 2026-07-27:
  - `4be89b0d` Cho2017 runner
  - `1b89a32d` EA arm for Cho
  - `ab03bd7a` EA arm for B14+Lee
  - `04a40e4e` Cho fresh source training

  Their dates match v1's statement that the final AAAI FP and Joint numbers come from the "07-27/28" run, which P12 (B14+Lee only) does not cover.

## 1. Per-document summary

### v1 — REVISION_PLAN_TSP_TPAMI.md (17:41)

**Purpose.** First journal plan: submit to **TSP, not TPAMI**. Rewrite the paper as estimation theory: joint estimation of geometry θ and class proportions π from a mixture, with weak identifiability. FP-GEM is demoted to one member of an estimator family plus a recipe: fixed-prior geometry → shift gate → stage-2 π estimation → separate decision weights.

**Key content:**
- §1: 12 reviewer items R1–R12, from yczf, hTrM and the AI reviewer.
- §2: evidence inventory.
  - The AAAI table (§2.1).
  - P12: FP−Joint = +0.003 [−0.0003, +0.006], not significant.
  - P13: the Joint prior stays at 0.46–0.50 while q goes 0.1→0.9, and geometry shifts by about 1.4.
  - REVIEW_P0 Sleep: one-shot 0.695 > fixed_iterative 0.656 ≈ identity 0.657 > joint 0.637. FP−Joint = +0.0185 [+0.0127, +0.0245]. Decision-prior effect = −0.144.
  - W1 MI: 115 subjects, not significant.
  - Stage-2: +0.050 under shift, −0.0125 when balanced; with the gate, false-alarm rate 4.8% and detection 33%.
  - V2P_WEIGHTED supersedes the old V2P.
  - W1-B BTTA-DG reproduction: Δ = 0.
  - Local simulations.
- §5: new theory items.
  - T5, tolerance radius: δ* ≈ sqrt(3/(8n))·t⁻³.
  - T6: the (a) bias-amplification factor 1/(1−t²S), (b) the joint-EM rate S(t), and (c) the three knobs α/k/gate.
  - T4: multiclass t⁴.
  - T7: stage-2 properties.
- §6: simulations S1–S6 and EEG blocks 6.2–6.6.
- §7: R→action map. §8: TSP structure. §9: 9–10 week timeline. §10: stop-loss rules. §11: artifact index.

**What it retracts.** The AAAI headline "FP-GEM > Joint on four datasets" is no longer the main claim, and old V2P is superseded by V2P_WEIGHTED.

**Non-claims:** no SOTA; no prevalence-invariance; not "FP more stable under stress"; not "FP > Joint significant on MI".

### v2 — REVISION_PLAN_v2_divergent.md (18:06)

**Purpose.** A rewrite, not a patch. The main line becomes **E, "prevalence sensitivity of alignment estimators"**: EA, Recenter, SPD normalization, CMMN, diagonal GEM and SPDIM are all estimators on a class mixture.

**Key content:**
- Routes compared: A (v1 family), B (second plan's Λ constraint), E. Choice: E as skeleton, A for the family, B reduced to a worst-case criterion.
- New theory N1–N8:
  - N1 sensitivity functional and 5-row bias/variance table.
  - N2 SPD and spectral versions.
  - N3 confounded direction v.
  - N4 oracle displacement ⇔ class-dependent geometry.
  - N5 "knob optimum ∈ {0, 1}".
  - N6 joint-EM contraction S(t).
  - N7 identifiability meter t⁶/6.
  - N8 multiclass t⁴.
- Method: a "constrained-prior geometry EM family" with Proj_U, TV ball of radius r, anchor κ, depth k and gate.
- Experiments L1–L6:
  - L2: prevalence-intervention map over q 0.1…0.9.
  - L3: separation strata, equated to "BCI illiteracy".
  - L4: natural shift, with "fresh" confirmation sets BNCI2014-004 and 2015-001.
  - L5: decision layer. L6: BN generality check.
- §7 **G0 hard gate**, listing six paper≠execution discrepancies:
  - B14 run as binary;
  - Student-t density;
  - MI frozen classifier-head readout;
  - Joint with 6 pseudo-counts;
  - fixed-budget Adam with no stopping rule;
  - class_stratified_half split.
- Plus: an optional split into two papers, a 14-week plan with gates G0–G4, and a risk list.

**What it supersedes.** It drops v1's GEM-centred framing and adds six new directions: BCI illiteracy, BN/AdaBN, the CSC atlas, and others.

### v3 — FP_GEM_REVISION_v3_review_and_execution_plan.md (20:39)

**Purpose.** A review of v2 with mathematical corrections and an execution specification. It accepts E but **pairs prevalence sensitivity with geometry recovery (G, B)**, and poses four questions: RQ1 proportion response, RQ2 geometry recovery, RQ3 mismatch and optimization, RQ4 prior information. It uses evidence tags [V2]/[MAIN]/[SUPP]/[REV]/[CHECK]/[DERIVATION]/[PLAN].

**Retractions and corrections of v2** (§3 disposition table):

| Item | v3 correction |
|---|---|
| N5 | "Endpoint {0,1} optimal" withdrawn. Gaussian counterexample: α* = r²/(r²+v₁); with v₀=.01, v₁=.04, r=.2, worst-case risk is .05 at both endpoints vs .03 at α=.5. δ* survives only as a *local MSE crossing of two specified endpoints*. |
| N6 | Joint slow rate is **(1+t²)S(t) = 1 − (2/3)t⁶**, not S(t). At t=.35: 2813.6 iterations vs 19.8. New finite-k dual response G_k, B_k, with B_k/G_k independent of k. |
| N8 | Universal t⁴ withdrawn. The K=3 simplex known-covariance translation model gives **I_{a\|η} = (t²/4)I₂ + O(t⁴)**. |
| N3 | Model-relative diagnostic only. The "orthogonal component invariant" claim and "same object as the CSC atlas" are withdrawn. |
| N4 | The "iff" is withdrawn; a fixed ridge penalty is a counterexample. "FP pins the compromise at source weights" is withdrawn. |
| N7 | Exploratory. No universal uniform-fallback gate. I_ηη = O(t²) and I_{η\|a} = t⁶/6 must not be conflated. |
| N1 | The unified variance ordering is removed. |
| N2 | Operator-by-operator derivatives required (EA whitening via the Daleckii–Krein F matrix; LE vs AIRM; spectral ∂log H). |

**Other withdrawals:** "BCI illiteracy = weak identifiability"; "fresh confirmation sets" (unless a repo-wide audit confirms they are unused); fixed 14 weeks; "all CPU recompute"; two-paper split as default; BN as a required item.

**Additions:** §10 G0 traceability CSVs and the reference interface; §11 experiment layers and the CP/CG/CPG design; §12 mismatch rules; §13 statistics; §14 server deliverable tree and gates G0–G5; §16.2 claim boundaries; Appendix B claim ledger C01–C10.

### v4 — REVISION_PLAN_v4_positive_claims.md (20:49)

**Purpose.** Integration after v3, stated as positive claims. It accepts all four v3 retractions and claims each "verified" item has a script in `journal_revision/prechecks/`.

**Claims P1–P10:**

| Claim | Content |
|---|---|
| P1 | Order set by configuration symmetry: I = (t²/4)Q + O(t⁴), with Q from the third-moment tensor Σ v⊗v⊗v. Centrally symmetric configurations give t⁴ (binary ≈ 2/3; four-class cross ≈ 0.17); K=3 simplex t²/4; K=4 simplex ≈ t²/3. |
| P2 | Value of information: sample-size factor I_aa/I_{a\|η} of ~120× at t=.35, ~32× at .5, ~3× at 1; one label ≈ 1000 / 160 / 5 unlabeled trials. |
| P3 | (1+t²)S(t), said to be "consistent with Table S4" (6074 mean iterations, 83% convergence). |
| P4 | B_k/G_k independent of k; early stopping = shrinkage; s* and k*. |
| P5 | Calibrated anchor κ* = 1/(I_{η\|θ}r²), independent of n; Monte Carlo at n=200 beats both endpoints at t=1 and 1.5 and equals FP at t=.5; κ=6 in the released code called "unjustified". |
| P6 | Per-operator derivatives: EA, Recenter, CMMN, BN. |
| P7 | Three real-EEG predictions: P13 (have), REVIEW_P0 (have), "K=5 gate power > K=2" (to test). |
| P8 | Decision layer. |
| P9 | (G, B) frontier plot. |
| P10 | Class-dependent-geometry test. |

**Also:** divergent directions D1–D8 (labels-for-prior, symmetry as a design quantity, acquisition protocol, online bandwidth, fMLLR, BN, ComBat, IMU-HAR); a TSP plan of 3–4 months and a TPAMI plan of +3–4 months; minimal method set §3.3; verification ledger §6.

### v5 — FP_GEM_REVISION_v5_open_research_directions.md (21:48)

**Purpose.** A direction pool, not claims. It **turns v4's positive claims back into questions** (§1 table).

**It explicitly does not accept:**
- K≥3 ⇒ the prior is estimable / Sleep more identifiable than MI;
- one label = a fixed number of unlabeled trials;
- less movement ⇒ more stable;
- κ* portable across models;
- one slope for all normalizations;
- "κ* losing still counts as positive because it auto-selects endpoints".

**It relaxes:** EM, full density, single batch, zero labels, full-geometry target, frozen representation, latent shared affine.

**Routes:**
- A: information.
  - A1 multi-batch known proportions (M = ΠC; bagMME already covers unmixing).
  - A2 sequence and state-space models.
  - A3 multi-view.
  - A4 class-free calibration anchors.
  - A5 artifact rejection / selection, with retained-proportion bounds (max(0,N_y−D)/N_ret ≤ ρ_y^ret ≤ min(N_y,N_ret)/N_ret).
  - A6 what labels should buy (I_total = n_U I_U + m I_L + I_meta).
- B: estimators.
  - B1 prior-free moment equation ψ_t(z) = z³ − (t²+3)z. Var = 4t⁴+18t²+6; Var(â) ≈ 3/(2nt⁴); multi-root equation d(d²+3(2ρ−1)td+2t²).
  - B2 decision-level partial identification.
  - B3 pipeline feedback.
- C: representation.
  - C1 physically shared transform becomes class-dependent after the encoder.
  - C2 source-density error and contamination.
  - C3 training for adaptability.
  - C4 amortized inference.
- D: theory.
  - D1 identifiability phase diagram.
  - D2 statistical vs optimization difficulty.
  - D3 diffusion.
  - D4 side lines.

**Also:** seven alternative paper stories; units U1–U8; route-selection criteria; literature R1–R12.

**Status as stated in v5:** it did **not** rerun the prechecks and ran no EEG. Only the B1 algebra was checked.

### EXECUTION_KICKOFF_sprint0.md (22:00, current)

**Purpose.** Judges v5 and launches a four-week Sprint 0. After four weeks, choose the main line.

**Adopted from v5:**
- the posture;
- B1 — reviewed with the new `prechecks/precheck_v5_moment_estimator.py`. As an estimator it is dominated. As a **fixed-prior mismatch test** it has power ≈ 0.4 at t≥1, δ=.2, and none at t=.5;
- A1 and A5 (A5 moves into G0);
- A6, C1 ("the most important Sprint-0 experiment"), C2, D1, D2.

**Deferred:** A2, A3, A4, B2, B3 (B3 folded into the v3 diagnostic matrix), C3, C4, D3, D4.

**What v5 lacks, per the kickoff:** a timebox and gates, the evaluation currency, a statistics spec, traceability detail, the decision layer, and submission discipline. It says v4 P1/P3/P4/P5 stay as **conditional theorems**.

**One disagreement with v5 (§1.4).** Within the specified model, κ*'s behaviour (auto-FP when separation is weak, auto-Joint when strong, better than both in between) is already a conditional positive result from Monte Carlo. Real-data performance is a separate proposition.

## 2. Consolidated current plan (kickoff plus v5)

**Research lines** (kickoff §3):

| Line | Content | Paper if it holds |
|---|---|---|
| (i) | Estimator sensitivity plus calibrated anchoring = v4 P1–P9 | Theory paper; κ* is the method, the B1 test a diagnostic |
| (ii) | Prior-free estimation plus protocol design = B1 + A1 + A6 | "Geometry without estimating proportions" and "design acquisition to be identifiable" |
| (iii) | Which layer geometry is shared at = C1: EA vs Recenter vs latent diagonal GEM under the same physical perturbation | "Why shared acquisition change looks class-dependent in deep representations"; the method moves back to the signal or SPD layer |

The author's prior: (iii) is the most important finding if it holds; (i) supplies the theory skeleton; (ii)'s test is a diagnostic module for (i). All three share one implementation and one data set.

**Sprint 0 tasks** (kickoff §4). T1–T4 run in parallel with T5–T6. **T7–T9 depend on T2 and T4.**

| Task | What | Where | Input | Output | Acceptance |
|---|---|---|---|---|---|
| T1 | G0 tables `manuscript_result_map.csv` and `artifact_capability_matrix.csv` | Server, read-only | Old tables, branches, artifacts | Two CSVs | Every old table cell has a status; for each dataset, which operators can be rerun is known |
| T2 | Unified reference implementation. Switches: density, readout, prior rule (fixed, κ, KL projection, pure joint), optimizer, upstream normalization. Per-iteration log of π, θ, objective, gradient | Drafted locally, validated on the server | Released `fpgem` package | Installable package and tests | Reproduces `convergence_sim` Table S3; FP and Joint endpoints match the old implementation numerically |
| T3 | A5 audit: per dataset and subject, ρ_A, ρ_E, retained trial count, rejection rule | Server CPU | Dumps and manifests | One table | Protocol vs observed proportion gap is quantified |
| T4 | Dump inventory: trial time order, pre-stimulus segments, raw-signal availability | Server | Data lake | Inventory | Decides whether A2, A4 and C1 are feasible |
| T5 | Theory ledger: general Q and remainder for P1; P3; P4; correspondence of P5's Dirichlet-EM and penalized MLE; general B1 (null space of feature map W) and efficiency bound | Local | Existing scripts | sympy / numeric ledger | Every result independently recomputed |
| T6 | Simulation: B1 vs FP / Joint / κ* extended to multiclass and diagonal affine; C2 source-density misspecification | Local | — | Figures and tables | Agrees with the binary case, or the difference is explained |
| T7 | **Discriminating experiment 1 (C1).** Inject a known gain / reference transform into raw signals; compare EA, Recenter and latent diagonal GEM; test whether the latent response depends on the class region | Server, light GPU | Raw signals, frozen models | (G, B) table and class-dependence test | Answers whether a shared physical transform stays shared in latent space |
| T8 | **Discriminating experiment 2 (A1).** Build label-driven sub-batches with different proportions from balanced data; single batch vs multi-batch known proportions vs intervals only | Server CPU | Dumps | Geometry error vs batch-matrix condition number | Answers whether multi-batch structure adds information |
| T9 | **Discriminating experiment 3 (B1 test).** Fixed-prior mismatch-test readings and power on Sleep and MI | Server CPU | Dumps | Per-subject test statistics | Compared against P13 and REVIEW_P0 prior movement |
| T10 | Freeze the evaluation-currency and statistics spec | Local | v3 §11–13 | One-page spec | All experiments record its fields |

**Week-4 decision rule** (kickoff §5):
- If T7 shows the same physical transform is significantly **class-dependent in latent space** while EA or Recenter stay shared → main line (iii). Then (i) becomes theory sections 3–4 and (ii) a diagnostic.
- Else, if T7 is not significant and T8 shows multi-batch structure significantly improves geometry error → (ii) + (i).
- Otherwise → (i), with the B1 test as the answer to R9.
- Always kept: P1–P5 theorems, G0, (G, B) evaluation, the decision layer, the non-claims list.
- TPAMI is decided at week 10 after a one-week BN or HAR pilot. Upgrade only if the closed-form bias and κ* point the same way on the new modality.

**Frozen vs open** (kickoff §2):
- Frozen:
  - G0 traceability plus the unified implementation;
  - (G, B) + task risk as the currency for every operator;
  - v3 §13 statistics;
  - the non-claims list;
  - first-round data: B14 binary and 4-class, Lee, Sleep;
  - the three candidate lines;
  - the week-4 decision.
- Open: the lead method; whether Stage-2 stays; TPAMI modality; whether to do A2.

**This week's five actions** (kickoff §6):
1. Send read-only T1/T3/T4 requests to the server, reusing the wording of `submission_2026-07-28/SERVER_REPRO_CHECKLIST_REQUEST.md` and adding ρ_A, ρ_E, trial order and pre-stimulus segments.
2. Start T2 locally: add the switches and logging to the released `fpgem` package, first reproducing `convergence_sim`.
3. T5: write the general Q (third-moment tensor projection) for P1 and the correspondence proof for P5.
4. T6: extend `precheck_v5_moment_estimator.py` to multiclass and diagonal affine.
5. T10: write the one-page spec.

**What not to do:**
- **Kickoff §7:** don't start A2, A3, C3, C4, D3, TPAMI-modality experiments, any new data collection, or any dataset choice made because it is "easier to get significant".
- **v3 §16.1:** the first batch excludes full-repo retraining, full method sweeps, and rewriting the abstract from new results.
- **v3 §11.1:** no large multiclass grid before the nuisance set is locked; don't expand all datasets or hyperparameters at once; don't attribute every counterexample to class-dependent geometry; don't explain all cross-time drift with same-distribution formulas; don't report metrics from two prediction sets as one strategy's guarantee.
- **v3 §16.2 claim boundaries:**
  - fixed prior ≠ prevalence-invariant;
  - small displacement ≠ strong recovery;
  - the confounded direction ≠ a causal decomposition for all operators;
  - oracle displacement ≠ uniquely class-dependent geometry;
  - interior shrinkage cannot be excluded without proof;
  - known-geometry information ≠ profile information;
  - not significant ≠ harmless or non-inferior;
  - a label-constructed intervention ≠ a deployed method;
  - tables with different readout, upstream normalization or K cannot be spliced;
  - a model-level numeric check ≠ EEG validation.
- **v3 §15.2 — not yet writable:** "real EEG reproduces a unified ordering", "one-shot is best on Sleep", "weak identifiability coincides with a low-performer group", "the protocol-aware recipe is safe".
- **v1 §4 / v2 §2 non-claims:** no SOTA; no invariance; not "FP significantly > Joint on MI"; not "Stage-2 universally safe".
- **v3 §15.4:** don't merge CMI-TRACE, identity removal, FSR, ACAR or OACI; don't add diffusion, full-encoder TTA or large nonlinear adapters as the main revision.

**Tensions between the documents that the caller should know about:**
1. The kickoff freezes "B14 binary **and 4-class**". v2 §7 and v3 §10.2 say 4-class needs a real run, because a binary dump cannot become 4-class evidence. v3 §11.7 says pick one MI and one Sleep setting by G0 completeness.
2. v4 P3 equates the translation-model rate with Table S4's affine run (6074 iterations). v3 §6.3 forbids exactly that equation.
3. v4 P4 and P7 assume a Sleep one-shot advantage and "K=5 gate power > K=2". v3 §15.2 and v5 reject these as premature, and the kickoff drops "class number determines identifiability".
4. v1 T6(b) (joint rate S(t), 20 iterations to move 90%) and v1/v2's use of δ* as a deployable criterion are both superseded by v3.
5. v2 §4.1 uses a Euclidean/TV projection. v3 §10.5 requires a KL M-step, and T2 lists "KL 投影".
6. v2 §9 puts reference-implementation extension on the server; v2 §11 puts it local. The kickoff settles it: drafted locally, validated on the server.

## 3. Artifacts referenced (doc and section; where the docs place them)

"Laptop" means the docs call it 本地 (local). "Server" means this machine or the repo branches.

**Laptop, per the docs — none found on the server:**

| Artifact | Referenced in |
|---|---|
| `journal_revision/REVISION_PLAN_TSP_TPAMI.md` (v1's original path) | v2 header |
| `Downloads/FP_GEM_major_revision_plan_20260926.md` ("second plan") | v2 header; v4 and kickoff headers |
| `journal_revision/prechecks/precheck_theory.py` and `precheck_theory_output.txt` | v1 §5.2, §11; v4 §6 |
| `journal_revision/prechecks/precheck_v3_claims.py` | v4 §6 |
| `journal_revision/prechecks/precheck_positive_claims.py` (parts A, B) | v4 P1, P5, §6 |
| `journal_revision/prechecks/precheck_value_of_information.py` | v4 P2, §6 |
| `prechecks/precheck_v5_moment_estimator.py` | kickoff §1.1, §6.4 |
| `fpgem_v2_math_checks.py` / `.json` (SHA 14730a44… / d1892d1e…) | v3 §0.2, §17, App A; location unstated |
| `convergence_sim` (strict-convergence Table S3) | v1 §2.2(g), §6.1, §11; v2 §4.2; kickoff T2 |
| `mechanism_sim` | v1 §2.2(g), §6.1, §11 |
| `multiclass_sim` (Joint strict-convergence rate only 63–67%) | v1 §2.2(g), T4, S5, §11 |
| `optimal_sim` (interior α significantly better in only 2/50 cells) | v1 T6(c), S4; v2 N5; v3 §5.3 |
| `version_b_optimal` | v1 §11 |
| Released `fpgem` package | v2 §4.2, §11; kickoff T2, §6.2 |
| `FP-GEM_AAAI2027/submission_2026-07-28/` (`main_submit_ready.tex`) | v1 §11 |
| `output/submission_2026-07-31/FP-GEM` (code package only) | v1 §2.1 |
| `submission_2026-07-28/SERVER_REPRO_CHECKLIST_REQUEST.md` (never answered) | v1 §2.1, §11; kickoff §6.1 |
| `rewrite/SERVER_AGENT_STATUS_QUERY.md` | v1 §11 |
| `FP-GEM_AAAI2027/notes/sleep_result_provenance.md` | v1 §11 |
| `sources/research_20260728_eeg_tta_regime.md` (MI datasets balanced by design) | v1 §7 R2 |
| `AAAI_CMI/When_Alignment_Chases_Prevalence_final(1).pdf` (22-page long version) | v1 header, §5.1, §11 |

**Server / repo, per the docs:**

| Artifact | Location | Referenced in |
|---|---|---|
| P12 head-to-head, per-subject | `agent/fp-gem-stage2` @`3b52e202`, `h2cmi/results/fp_gem_main/` (`fp_gem_per_subject.csv`) | v1 §2.2(a), §6.2, §11 |
| P13 prevalence stress (Lee 54×3; RCT sensitivity 0.0357) | `exp/h2cmi-wave0-mechanism` @`b5fb515`, `h2cmi/results/fp_gem_prevalence/` | v1 §2.2(b), M1; v2 N2, L2; v4 P7; kickoff T9 |
| Story freeze, evidence hierarchy, red team: `FINAL_FP_GEM_STORY_FREEZE.md`, `FP_GEM_EVIDENCE_HIERARCHY.md`, `P14_PREWRITE_RED_TEAM.md` | same branch @`df47753` | v1 §4, §9 wk 7, §11 |
| REVIEW_P0 (Sleep 75, W1 115 MI subjects, V2P_WEIGHTED, W0.3 decomposition) | `exp/h2cmi-review-p0-corrections` @`5bc9bf0`, `h2cmi/results/REVIEW_P0_RESULTS.md`, `review_p0.report.json`; "analyzer" `9a35cc9` | v1 §2.2(c)(e), §11; v2 L2, L4, L5, §6; v4 P7, P8; kickoff T9 |
| Stage-2 (+ gate) | `agent/fp-gem-stage2`, `h2cmi/results/fp_gem_stage2/` | v1 §2.2(d), P1; v2 §6 |
| Sleep K=5 chi-square gate runner / analyzer (results not committed) | `687003ff`, `722e33cd` | v1 §2.2(d), P2 |
| W1-B BTTA-DG reproduction | `e941bb5`, `h2cmi/results/W1B_REPRODUCTION.md` | v1 §2.2(f), §6.5, §11; v2 §6 |
| CSC label-prior direction atlas | `csc` branch | v2 N3, §6; v3 §8.1 ("not the same object without checking") |
| Few-shot results (label efficiency) | `agent/cmi-trace-readout-label-efficiency` (exists) | v4 D1 |

**Other named server-side items:**
- B2b source-power study (v2 N7, §6; v3 §8.3).
- V2-A / V2-B metadata routing (v2 §6).
- ACAR, TOS, OACI, CMI-TRACE, excluded (v2 §6; v3 §15.4 adds FSR).
- "Stage-2 npz dump" (v1 §6.2); "已存 dump" / stored dumps everywhere.
- "Final-round per-subject scores, iteration logs, dump inventory" (v1 §9 wk 1).
- "Source density head, RCT/SPDIM fitted objects" (v2 §11).
- "dump 与 manifest" (kickoff T3); raw signals / data lake (kickoff T4, T7).

**Proposed, not existing** (v3 §14.1): the `journal_revision_v3/` tree:
- `evidence/`: `manuscript_result_map.csv`, `artifact_capability_matrix.csv`, `claim_evidence_ledger.csv`
- `theory/`: `derivation_registry.md`, `numerical_checks/`
- `prereg/`: `pilot_protocol.md`, `intervention_manifest.json`, `metrics_and_failure_rules.md`
- `configs/`: `frozen_reference_config.json`
- `outputs/`: `per_unit_metrics.csv`, `intervention_responses.csv`, `solver_trajectories/`, `source_and_prediction_hashes.csv`
- `reports/`: `pilot_results.md`, `diagnostic_findings.md`, `claim_updates.md`

**Paper anchors.** Locations are in the extracted text files under the scratchpad `txt/` directory.
- Main text:
  - Thm 1: line 277, p3.
  - Props 2 and 3: lines 327 and 355, p3.
  - Props 4 and 5: lines 374 and 406, p4.
  - Thm 6: line 447, p4.
  - Algorithm / eq (10): line 594ff, p5.
  - Readout / Recenter note: lines 758–775.
- Supplement:
  - Thm S2: line 68, p1. Cor S3: line 113, p1.
  - Thm S4: line 134, p2. Cor S6: line 265, p2.
  - Prop S7: line 312, p3. Prop S8: line 413, p3. Lemma S9: line 449, p3.
  - Thm S11: line 515, p4. Thm S12: line 553, p4. Prop S13: line 580, p4.
  - Thm S14: line 641, p5.
  - F.1–F.5: lines 739–875.
  - Table S3: line 919, p7 (FP−Joint, nA=500, t ∈ {.35, .5, .75, 1.5} × ρ ∈ {.5, .7, .92}).
  - Table S4: line 975, p7 (at t=.35 Joint converges in 167/200 runs, mean 6074.3 iterations).
  - Thm S15: line 1026, p8.
  - H, EEG implementation: line 1179, p8; label firewall / pairing: lines 1264–1275.

**Datasets named:** BNCI2014-001 (B14), Lee2019, Cho2017 (14/52 subjects below chance, v2 L3), Sleep-EDF (75 subjects), BNCI2014-004, BNCI2015-001, HGD, Stieger2021, RLSbench, CIFAR-10-C, ImageNet-C, UCI-HAR, PAMAP2, Opportunity.

**Baselines named:** Recenter, SPDIM (geodesic / bias), EA, Diag-IM / Latent-IM-Diag, CMMN, T-TIME, BTTA-DG, Tent / SAR / AdaBN / DELTA / NOTE / LAME, JCPOT, bagMME.

## 4. v3 §10–13, which Sprint 0 depends on

**§10 G0 (traceability):**
- Finding one inconsistent implementation must not be written up as "all old numbers are wrong". Until every cell is mapped, only "the submission spec differs from some checked implementations" is allowed.
- Two CSVs, schemas in §5 below.
- Reference interface: FrozenSourceBundle → AdaptInput (no labels, no metrics) → AdapterConfig → AdapterOutput (state, trajectory, convergence flags, hashes) → Evaluator (predictions first, then labels). Every controlled method shares the same frozen bundle for a given subject, seed and split.
- Minimal control group: No-GEM, one pooled estimator, one-shot fixed, converged fixed, Pure Joint, one pre-specified shrinkage. **Pure Joint and Anchored Joint must be named differently.**
- Upstream normalization none vs Recenter is its own factor. Same-head Recenter is the key net-GEM control.
- Constrained M-step: π⁺ ∈ argmax_{π∈U} Σ r̄_y log π_y ≡ argmin KL(r̄‖π). Not a Euclidean projection. TV = ½‖·‖₁. Check monotonicity or GEM surrogate, otherwise call it a generic optimizer.

**§11 experiments:**
- Layers L1–L6.
- L2 design: C0 / CP / CG / CPG (§5 below).
- Keep both weighted and real-subsample versions. Record n_eff = (Σw)²/Σw², plus n_unique, per-class counts, duplicates, time blocks.
- Labels are used only by the constructor, never as adapter input.
- On real EEG, "recovery" means incremental recovery of a known injected perturbation, compared on fixed probes; irreversible operations (channel loss, rank-reducing re-reference) are named separately.
- Per-cell fields: predicted and observed proportion and geometry responses; transform action on fixed probes; margin and prediction change; bAcc, acc, class recalls, NLL (NLL only for calibrated posteriors); prior, objective and surrogate trajectories; gradient residual; convergence status; boundary hits; n_raw, n_unique, n_eff, time blocks.
- First round: one MI and one Sleep setting chosen by G0 completeness. Sleep mechanism experiments use within-night non-overlapping blocks.

**§12 mismatch:**
- Oracle-sensitivity diagnostic matrix: λ=0 vs penalty path; finite sample; optimizer (residual, multi-start); density variant; shared T vs per-class T_y (oracle, never in the main table); upstream normalization.
- Solver status is one of `stationary`, `budget_exhausted`, `boundary_solution`, `numerical_failure`. Pre-declared fallback, e.g. identity. Never drop failed units post hoc. Equal-budget and strictly-stationary tables are both kept and do not substitute for each other.
- Separate task separability, density discrimination and model identifiability. Label-defined strata are post-hoc and need cross-fitting.
- §12.4 table of disallowed inferences.

**§13 natural shift, decision layer, statistics:**
- Natural shift does not validate the local theory.
- Stage-2 must refit geometry for each proportion condition. The old version is relabelled a pure decision-layer experiment.
- h_BA = argmax p̂_y(x), h_Acc = argmax ρ̂_y p̂_y(x); a posterior must be divided by π_src.
- Every prediction set reports accuracy, bAcc and per-class recall together. A bAcc that never uses ρ̂ is invariant by construction.
- Gates need their own construction, calibration and evaluation sets, with no post-hoc thresholds.
- Statistics (§13.4):
  - the subject is the unit;
  - aggregate seeds and sessions within subject, then run a paired subject bootstrap;
  - pre-declare the primary estimand (per-dataset subject-weighted or dataset-macro);
  - seed-score averaging ≠ posterior ensemble;
  - report CI, effect size, coverage, failures and pre-set win/tie/loss thresholds;
  - "CI includes 0" does not prove harmlessness or non-inferiority;
  - bootstrap is conditional on fixed checkpoints, and overlapping LOSO sources correlate subjects.
- v1 §6.2 adds 10k paired bootstraps and Holm only on one pre-registered contrast per panel.
- §13.5: "fresh confirmation" requires a repo-wide audit, otherwise call it "extended validation".
- §14.2 per-unit metadata: experiment_id, dataset, label_set, subject, session, seed; checkpoint, density, preprocessing, adapt-manifest, eval-manifest and intervention hashes; geometry family and strength, prevalence condition, upstream normalization, readout, fitting-prior and decision rules, penalty, prior strength, optimizer, budget, stop rule; source_data_used and a `target_labels_used` field that distinguishes construction / oracle / post-hoc / adapter input; oracle_flag, status, fallback, residual, Δobjective, boundary hits; prediction, result and commit hashes.
- Gates: G0 traceability, G1 math and implementation, G2 small intervention, G3 mismatch, G4 confirmation, G5 reconstructable. Each passes on evidence quality, not on a positive direction.

## 5. Definitions Sprint 0 needs

**`manuscript_result_map.csv`** (v3 §10.2). Columns:

`table_id, cell_id, dataset, label_set, method, reported_value, commit, config_path, config_hash, split_manifest, split_hash, source_checkpoint, checkpoint_hash, density_family, readout, upstream_normalization, prior_update, optimizer, stopping_rule, prediction_path, aggregation_script, reproduction_status, notes`

`reproduction_status` takes at least: `reproduced`, `located_not_recomputed`, `unresolved`, `known_different_implementation`. An unresolved entry is never counted as refuted. Map each old cell to config → split → checkpoint → prediction file → commit (v2 §7).

**`artifact_capability_matrix.csv`** (v3 §10.2). Columns:

`dataset, label_set, subject, seed, raw_signal_available, pre_normalization_features_available, post_normalization_features_available, source_density_available, source_validation_available, checkpoint_available, trial_ids_available, split_available, can_rerun_latent_adapter, can_rerun_spd_adapter, can_rerun_signal_adapter, missing_dependency, artifact_hash`

With final embeddings only, do not promise EA, RCT/SPDIM or CMMN reruns. The kickoff's T4 adds trial time order and pre-stimulus segments; T3 adds ρ_A, ρ_E, retained counts and the rejection rule.

**ρ_A and ρ_E.** No document defines them formally. From v1 M3, v3 §2 and §11.3, and kickoff T3:
- ρ_A = empirical class proportions of the adaptation pool actually fed to the adapter, after rejection and splitting, computed only after predictions are written.
- ρ_E = the same for the evaluation set.
- Compare both against π_ref (protocol or source reference, source recorded) and ρ_T.
- v1's mismatch index is d_ρ = ½‖ρ̂_A − π_src‖₁.
- They are kept distinct from π_fit (fitting weight) and π_dec (decision weight).
- A5 bounds when only total drops D are known: max(0,N_y−D)/N_ret ≤ ρ_y^ret ≤ min(N_y,N_ret)/N_ret, subject to joint simplex feasibility.
- In CP, ρ_A varies and ρ_E is fixed. ρ_A ≠ ρ_E naturally belongs to L4/L5.

**(G, B) responses** (v3 §4.5, §6.4–6.5):
- G_A = ∂θ*_A/∂g, the response to a true recoverable geometry change. B_A = ∂θ*_A/∂ρ, the response to true proportions. Signed.
- Ideal: G≈I and B small. Identity has B=0 but no recovery.
- Estimators in different spaces are compared via a common action space, fixed-probe action, or task output — not raw parameter norms.
- General rule: ∂θ*/∂ρ_k = −H⁻¹(E_{P_k}ψ − E_{P_K}ψ).
- In the binary translation model (r_t = t²S(t)):

| Estimator | G | B |
|---|---|---|
| Identity | 0 | 0 |
| Pooled mean | 1 | −2t |
| One-shot fixed prior | 1−r | −2tS |
| k-step fixed prior | 1−rᵏ | −2tS(1−rᵏ)/(1−r) |
| Converged fixed prior | 1 | −2tS/(1−r) |
| Free joint (correctly specified, solved) | 1 | 0 |

- B_k/G_k = −2tS/(1−r), independent of k. At t=0.5 this is −0.99367.
- In the recovery test, compare 𝒜(P_gA)(P_gx) with 𝒜(A)(x) on fixed probes.
- Currency = (G, B) + task risk (kickoff §2).

**Interventions** (v3 §11.3). Same frozen source, subject and base pool throughout:

| Condition | Proportions | Injected geometry | Question answered |
|---|---|---|---|
| C0 | Base | None | Identity / replay check |
| CP | Changed | None | Pure proportion response; evaluation set fixed |
| CG | Base | Changed (applied to adapt and eval inputs, sample IDs paired) | Geometry recovery |
| CPG | Changed | Changed | Joint effect and interaction |

- First use small, centrally symmetric perturbations for first derivatives, then larger ones for the nonlinear range. The q grid 0.1…0.9 is a candidate, not frozen.
- Report weighted vs real-subsample versions separately.
- T7 implements CG on raw signals (gain / reference). T8 implements CP-style multi-batch Π matrices.