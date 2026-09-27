## G01_global_ambiguity — Main p.3 §3.1–3.2 (Theorem 1, Prop 2, stabilizer text); Supp p.1–3 §A–B (Def S1, Thm S2, Cor S3, Thm S4, Cor S5, Cor S6)

### Tracer
G01 (Main p.3 §3.1–3.2: Thm 1, Prop 2 and the stabilizer text; Supp p.1–3: Def S1, Thm S2, Cor S3–S6) is entirely analytic.

**Status: all 14 checkable claims match; nothing disagrees.**
- An independent sympy + scipy re-derivation passes 43/43 checks. Script: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g01_theory_check.py (sha256 57b0896fe4b5f040…); log: g01_theory_check.log in the same folder. It confirms:
  - the Student-t3 normalizer 2/(π√3), Var_f=3 and Var_g=3/d²=300/121;
  - r(u)=d[(1+u²/3)/(1+d²u²/3)]² with range (d^−3, d] = (0.751315, 1.1];
  - 2/3≤(10/11)³ and 11/10≤3/2;
  - p1=3f−2g and p2=3g−2f, both nonnegative and normalized;
  - both mixture identities, symbolic in α and β;
  - W_P and W_G yield the same g (max error <1e-12);
  - Var p1=489/121 and Var p2=174/121 exactly;
  - Cor S3: a_j=1, b=0 is the unique positive solution;
  - Prop 2's γ/2, and Cor S6's minimax g0g1/(g0+g1) at q*=g1/(g0+g1).
- The Thm S2 proof was checked by hand.

**Provenance.**
- No project code or result artifact produces any G01 number. I searched all 121 refs (64 unique tips) with git grep, /home/infres/yinwang by filename to depth 6, and /home/infres/yinwang/AAAI_2026 by content.
- The only code tie is the definitional family Eq.(3): h2cmi/tta/class_conditional.py Transform 'diag_affine', L44-46/L67-74. It is the same blob 6db965db on df47753e, 04a40e4e, e6c49156 (P12 launch) and 278fc85e (REVIEW_P0).
- The frozen hierarchy @df47753e (FP_GEM_EVIDENCE_HIERARCHY.md L7) lists 'observational-equivalence theory' as main-text evidence #1. The frozen fp_gem_theory_to_evidence.csv and claim gate carry no row or flag for it.

**Correction to the task hint.** Per the upper-folder docs (/home/infres/yinwang/CMI_AAAI/FP-GEM/REVISION_PLAN_v4_positive_claims.md L212-219; REVISION_PLAN_TSP_TPAMI.md L212-225), the local-only precheck_theory.py covers T5/T6 (tolerance radius, bias amplification), not Thm 1 or S2–S6. None of the prechecks is on this server. This audit is the first documented independent check of G01. The journal plans (TSP_TPAMI L205-206, v4 L144, v2 L71) keep S2/S3 and Thm 1 + Cor S6 in the main text.

**Wording and scope notes (not errors).**
1. The main-text Prop 2 leaves implicit that actions are restricted to {Id, T} and that samples are i.i.d.; Cor S6 states both.
2. The main text writes the closed interval [(1.1)^−3, 1.1] as a containment, while the supplement gives the exact range (d^−3, d].
3. Thm 1's bounded-ratio hypothesis cannot hold for a Gaussian f under any nonidentity diagonal-affine T. The exact ambiguity therefore needs a heavy-tailed witness, consistent with the paper treating the Gaussian case through weak identification (Thm 6).
4. The deployed density heads satisfy Cor S3's finite-moment condition: Student-t df=8, rank 4 in P12 (fp_gem_config.json @df47753e) and rank 2 in REVIEW_P0 (h2cmi/config.py L39, L187-189).

No empirical run is involved, so the EEGNet-REVIEW_P0 vs TSMNet-P12 mixing issue does not arise for this group. No files were changed outside the scratchpad, and there were no checkouts or SLURM calls.

### Adversarial re-check
I re-checked G01 (global ambiguity: Main p.3 §3.1–3.2; Supp §A–B, S1–S6) adversarially. The whole group is analytic. Its only code counterpart is the positive-diagonal affine family (h2cmi/tta/class_conditional.py, blob 6db965db4f2f, identical on every FP-GEM ref). No run, artifact or gate on the server corresponds to Thm 1, Prop 2 or S2–S6, and the paper claims none: supplement §F covers only the Gaussian study.

**Theory rows.** All 13 are MATCH on independent re-derivation.
- The tracer's g01_theory_check.py passes 43/43, but three checks are hard-coded or trivial (L33 int_g=1 set to True; L73-74 3·1−2·1==1).
- I therefore wrote an independent check, /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g01_recheck_independent.py (sha256 79fe520e…). It uses scipy's t3, quadrature for every integral and moment, a 400k-draw Monte Carlo KS test between the two worlds (D=0.0023, p=0.238) and a brute-force S6 minimax. Result: ALL_PASS 28/28.
- Wording and scope notes only, no errors:
  - Prop 2 needs the two-action restriction {Id,T}. Cor S6 states it; the main text does not.
  - The main text's "hence nonzero variance" is a small logical leap.
  - The closed interval [(1.1)^−3, 1.1] versus the exact half-open (d^−3, d] is a harmless containment.
  - Bounded r can never hold for a Gaussian f, so the exact ambiguity needs heavy tails. This is consistent with deferring the Gaussian case to Thm 6.

**Flagged precheck row: stays UNTRACEABLE, reframed.**
- The scripts cited by the revision docs (precheck_theory.py and siblings in journal_revision/prechecks/) are on no git ref (98 unique tips, plus `-S` history search) and in no directory. I searched home to maxdepth 9, /tmp, the datalake, AAAI_2026, and the Claude/Codex transcripts.
- TSP plan §11 puts them on the author's local machine.
- Even per the docs they do not cover G01: §5.2 pre-checks T5/T6/T4, while G01 sits in §5.1 "retain" with no pre-check, and v4's verification table has no G01 row.
- G01 should be recorded as ANALYTIC_ONLY.

**Evidence-freeze row: corrected from PARTIAL to MATCH.** FP_GEM_EVIDENCE_HIERARCHY.md L7 @df47753e lists observational-equivalence theory as main-text item 1. The "complete spine" has no row for it by design, because fp_gem_theory_to_evidence.md and CANONICAL_EVIDENCE_INDEX L24 say it is the EMPIRICAL spine. One residual gap is bookkeeping, not a paper mismatch: the story-freeze claim gate has no flag for this theory (only theory_prior_feedback_claim_supported).

**Closest related server material, not G01:** Project A's non-identifiability notes on the target prior with geometry held fixed (notes/project_A_observability/07_counterexample_catalog.md CE-R0-3, CE-R1-2; 04_prior_decoupled_theory.md TU-1), and the identity-fallback "identifiability boundary" guards in class_conditional.py L19-20 and L297-302.

No files were modified outside the scratchpad, and no git state was changed.

## G02_gaussian_weak_identification — Main p.4–5 §3.4 (Theorem 6, Eqs 6–7, 'Where the weak direction comes from', sample-complexity paragraph); Supp p.7–8 §G (Theorem S15 + proof); Abstract/Fig 1 caption O(1)→O(t^4), O(t^6), O(t^3)

### Tracer
G02 (Theorem 6 / S15, Gaussian weak identification) is purely analytic, and no code or result artifact for it exists on this server. So every row is UNTRACEABLE with respect to the server, but every mathematical statement is CORRECT: I re-derived each one independently.

**Audit script (scratchpad only, nothing committed):** /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g02_theorem6_audit.py, output g02_theorem6_audit.json and g02_fisher_eig.txt; env icml (sympy 1.14, mpmath 1.3, dps 40), runtime seconds, CPU.

**What it checks:**
- Symbolic: the scores from differentiating m_{a,eta}; the sech^2 coefficients; the W moments; the S(t) series to t^10 (next term -227/15 t^10); the Fisher blocks, both Schur complements, and the A, K, B series; the derivatives of BA.
- Numeric: quadrature of S(t) and of the Fisher blocks, with errors around 1e-40.
- A direct KL minimisation over a at t = 0.3, 0.5, 1.0 and δ = 1e-3 and 5e-4. This does not use the Fisher shortcut, and it reproduces A(t), K(t) and B(t) to about 1e-7 relative.
- The iterated limits -2, 4/3 and 2phi(0).

**Rendered-PDF check (PyMuPDF):** the printed forms are right, including Ia|eta = 1 - t^2S/(1-S).

**Two non-numeric caveats:**
- (a) Main text L496-497 gives S only to O(t^8). That is not enough for the -2t^6 term of Eq.(6), which needs the 13/3 t^8 coefficient given only in the Supplement.
- (b) The Fig.1 caption says the information 'along the coupled (eta, a) direction is O(t^4)'. That is true for the profile information of translation, Ia|eta, but the smallest Fisher eigenvalue in (a, eta) coordinates is about t^6/6.

**Where I searched:**
- git grep over all 166 refs (104 unique tips).
- git log --all pickaxe for sech, 62/315, 17/45, Pinsker, profile information.
- The home tree by filename (depth 7), including fpgem*, precheck*, *math_check*, *_sim*, *fisher* and *theorem*.
- A content grep of CMI_AAAI and AAAI_2026.
- ~/.cache/h2cmi_training_caches, including regime_analysis and the P13 clones.
- The local folders the revision docs name: FP-GEM_AAAI2027, AAAI_CMI, journal_revision, prechecks.

The only hits were unrelated: tos_cmi/fisher.py (TOS-CMI mean scatter), DualTrace reference_math_checks.py, OACI/FSR 'weak_identifiability' labels, and notes/theory/verify_tension.py (LPC-CMI).

**Server-side context:**
- The frozen FP-GEM story (origin/exp/h2cmi-wave0-mechanism @ df47753e: FP_GEM_EVIDENCE_HIERARCHY.md and fp_gem_theory_to_evidence.csv) does not contain this theorem.
- The review-completion audit (@29a21959, orthogonal_score_blockers.md) states that score and Fisher blocks were never implemented for the GEM family. There is therefore no empirical EEG counterpart of Ia|eta or Ieta|a.
- W0.4 (c79a041e) is a Sleep batch-size sweep of the decision prior (EEGNet REVIEW_P0 bundles) and is not evidence for Theorem 6.

**Parent folder /home/infres/yinwang/CMI_AAAI/FP-GEM:** read for context only; none of its Sprint-0 T2-T10 tasks were executed. v3 §6.3 / §8.3 and v2/v4 restate or re-check this theorem using local-only scripts (fpgem_v2_math_checks.py and .json, SHA-256 in v3 L1251-1257). All their quoted values agree with my recomputation: S(0.35), (1+t^2)S(0.35), B_k/G_k(0.5) = A(0.5), and Ieta|a = t^6/6.

This group involves no EEG runs, so the EEGNet-vs-TSMNet mixing risk does not apply. The audit script could seed the T5 theory ledger if the author wants it committed.

### Adversarial re-check
G02 (Gaussian weak identification: main Theorem 6 §3.4, p.4-5; Supp Theorem S15 §G, p.7-8; the O(1)→O(t^4), O(t^6), O(t^3) statements in the Abstract, Intro, Fig. 1 and Conclusion). All rows stay UNTRACEABLE: the claims are analytic, and the server has no code or artifact for them.

**Search.** I searched hard for server-side evidence:
- git grep over all 104 unique ref tips plus 2 stashes;
- `git log --all --reflog` pickaxe for sech, Schur, 'profile information', 'profiling out', 'When Priors Push', 0.8901398 and `cosh\(`: 0 hits;
- no FP-GEM LaTeX source on any ref;
- content grep of H2CMI (qxu, _frozen_shards, shard_results_salvaged, paper_data, p12_extract, both .codex clones), results, notes, h2cmi, ~/.cache/h2cmi_training_caches, AAAI_2026, ICML_2026, CS_QMI and jeanzay: only the WAVE0_FROZEN.md copies matched;
- find for fpgem_v2_math_checks, precheck_*.py, journal_revision, prechecks and FP-GEM_AAAI2027: 0 hits.

The nearest items are all different experiments: the W0.4 batch-size sweep, `regime_analysis/synthetic_regime.py`, the paper_data Theorem-1 figure (CMI-Trace) and the DualTrace math checks.

**Math.** I re-derived everything independently of the tracer with `/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g02_recheck_independent.py` (.json alongside). It uses SciPy quadrature over central-difference scores, plus direct KL minimisation with no Fisher shortcut. Every formula and coefficient is correct:
- Iaa, Iaη, Iηη and Ia|η = 1 - t^2S/(1-S) = 2/3t^4 - 2t^6;
- Iη|a;
- A = -2tS/(1-t^2S), with the negative sign confirmed;
- K = 4/3t^6;
- B = 2t^3φ;
- the S(t) series;
- the iterated limits and Pinsker.

**Corrections to the tracer.**
1. **Fig. 1 caption.** The caveat is weaker than the tracer said. Ia|η is invariant to how η is scaled, and it is O(t^4). The smallest Fisher eigenvalue is O(t^6) only in raw (a,η) coordinates. With η rescaled so the scores are commensurate (the paper's own 'rescaled composition score'), it is ≈t^4/3. The caption is fine; the rewording is optional.
2. **Timeline.** 'Added after the 07-14 freeze' is not supported. WAVE0_FROZEN.md @ e7b7f887 (2026-07-06) L21/L78 already cites 'the weak-identification theory'. The server simply has nothing that contains or dates the Gaussian t^4/t^6/t^3 form. The FP-GEM evidence hierarchy at df47753e omits it, and W0.4 must not be cited as its evidence.
3. **Parent-folder numbers.** Every recorded value reproduces to all printed digits: S(0.35), (1+t^2)S, 19.79 / 2813.61 rounds, the G_k/B_k table, the J_EM eigenvalues, Iη|a ≈ t^6/6, 3/(2nt^4), and the v4 value-of-information figures (≈120×/≈1000, ≈32×/≈160, ≈3×/≈5). The generating scripts are local-only. v2 L82 drops A(t)'s minus sign; v3 L472 already fixes this.
4. **Presentation gap (confirmed).** The main text's S expansion to O(t^8) does not determine the -2t^6 term; that needs the 13/3 t^8 coefficient, which only the supplement gives.

**Added rows.**
- The contributions bullet (p.2 L125-129).
- The parent-folder interpretive claims that Iη|θ ≈ t^6/6 explains the P13 Joint-prior immobility and the Stage-2/B2b gate power. These are untested hypotheses on a model that differs from the one in the code. Example: κ=6 at n=50 alone would allow π0 down to 0.14 at q=0.1, yet the observed value is 0.4636.

## G03_estimator_theory — Main p.3–4 §3.3 (Eq 4–5, Prop 3, Prop 4, Prop 5), §4.2 (Eq 12); Supp p.3–5 §C (Prop S7, S8), §D (Lemma S9, Cor S10), §E (Thm S11, S12, Prop S13, Thm S14, attenuation paragraph)

### Tracer
G03 (estimator theory: Props 3-5, S7-S14, Eq 12) is ANALYTIC. None of it is produced by code or result files on this server. I searched all 155 git refs for the markers of the controlled-study and theory code: 0 hits in .py/.md files. I found no precheck/fpgem/journal_revision scripts under AAAI_2026, FP-GEM or H2CMI (maxdepth 4). The supplement says the Gaussian study ran on a laptop.

I re-derived every statement numerically. Script: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g03_theory_check.py; log: agents/g03_theory_check.log (CPU, 25 s). All checks PASS:
- Props 3 and S7 (binary and K=3, with a penalty): relative error ≤7e-10.
- Props 4 and S8: exact Schur/Loewner algebra, and a Monte Carlo check of the covariance within 1.6 SE.
- Props 5 and S13: the bound chain holds, and B_r=0 when r=τ.
- Lemma S9 and Cor S10.
- Thm S11 against the code's pooled formula (MC error 1e-3).
- Thm S12 identity: error 4e-15.
- Thm S14 closed form: error ≤7e-9, with a table of κ(t) values.
- κ(1) matches I_aa(1) independently, which ties S14 to Thm 6.

Where the theory meets the implementation (origin/exp/h2cmi-wave0-mechanism@df47753e; code identical at 278fc85e, 5bc9bf07 and 04a40e4e):

(1) Eq (12) uniform-density readout.
- MATCH for Sleep: REVIEW_P0 harness.py L32-36, p0_eval.py L77/L87-98.
- MISMATCH for MI (P12): run_fp_gem.py L928-929 passes T(z) through the frozen TSMNet Linear(210,2). The config's decision_rule says so explicitly (fp_gem_config.json L95). The §5.2 sentence "GEM rows use the stored Gaussian head with uniform decision weights" is therefore false for MI.

(2) The "source value" held fixed by FP-GEM differs by dataset.
- In P12 it is the empirical πsrc, 0.5/0.5 in all 189/189 unit JSONs.
- In REVIEW_P0 Sleep it is UNIFORM 1/5 (p0_source.py L71/L78 at 278fc85e), while ρ_source = [.339, .111, .351, .067, .132]. Sleep is thus Prop 5's misspecified-fixed-prior regime.
- Joint-GEM is a Dirichlet MAP with 6πS pseudo-counts, not Eq (11)'s plain mean update.

(3) Prop 4 wording. Main-text Prop 4 omits S8's unpenalized restriction, which OpenReview flagged. The implemented estimators use a non-vanishing penalty λ=1 plus a Dirichlet prior on η, so I⁻¹/n does not apply to the EEG fits.

(4) Real-data counterparts I found that bear on the theory (P12 cache ~/.cache/h2cmi_training_caches/fp_gem_p12/units; P13 b5fb5158):
- On exactly balanced B14 batches, the Joint prior collapses to the Dirichlet floor 3/78 in 18 of 27 units.
- On Lee, Spearman(|η̂_Joint|, ‖θ_J−θ_FP‖) = 0.943, consistent with the Prop 3 coupling. The coupling does not translate into bAcc (ρ=0.06). This is exploratory; the paper does not report it.
- P13: the Joint prior barely tracks q (0.46→0.50 while q goes 0.1→0.9).

(5) S12 and the S14 attenuation are contradicted directionally by REVIEW_P0 V2P_WEIGHTED (2-class MI, H2 encoder). There the oracle is the most prevalence-sensitive operator (1.96). The fixed-prior one-shot moves more than pooled on means: translation 0.297 vs 0.158; FRSC−pooled +0.265 [0.191, 0.341]. Per unit the picture is mixed (median ratio 0.90). The paper states both results only as model theorems, so there is no numeric mismatch, but they should not be extrapolated to EEG operators.

Useful for the revision but absent from the paper: Sleep decision-prior effect P = −0.1438 [−0.159, −0.128], a direct real-data illustration of Lemma S9; one-shot FRSC bAcc 0.6954.

Numbers are kept separate by run: REVIEW_P0 (H2/EEGNet-style encoder, Sleep, and the V2P MI units) versus P12/P13 (TSMNet, MI).

### Adversarial re-check
I re-checked the eight G03 rows the tracer flagged, read-only. I made no checkouts, jobs or edits; my notes are in scratchpad/agents/g03_recheck_notes.txt.

**Status changes**
- **Eq (12), MI columns: MISMATCH confirmed and strengthened.**
  - All three MI runners read predictions from the TSMNet linear classifier: run_fp_gem.py@df47753e L927-929, run_fp_gem_cho.py@04a40e4e L85-86, and regime_unit.py L119.
  - The six MI GEM standard deviations in the paper equal the P12/Cho linear-readout artifacts exactly (ddof=1). The paper's MI GEM cells therefore came from those runs, not from a density-head rerun.
  - No other MI FP/Joint run after 04a40e4e exists in any git ref or cache.
- **Lemma S9: upgraded UNTRACEABLE → PARTIAL.**
  - A committed, pre-registered real-data test exists: origin/exp/h2cmi-wave0-mechanism@aae5a89b, h2cmi/results/wave0_metricswitch.report.json.
  - On Sleep, uniform decision weights maximise BA among {Unif, ρ_A, ρ_E, π_J}: 0.6572 vs 0.4953 for the true ρ_E, +0.162 [0.144, 0.180], 74/75 subjects. I reproduced this from the raw rows.
  - The same report shows the premise is violated: ordinary accuracy also prefers uniform weights, so the Student-t head is not a correctly specified class-conditional model.
- **Prop 3, Prop S7, Prop 4/S8, Prop 5/S13, Cor S10, Thm S14: remain UNTRACEABLE.** They are analytic, and the tracer's checks plus my κ/S spot check pass. No server code evaluates the formulas.

**New supporting artifacts added to those rows**
- **Prop 3:** a pre-existing coupling diagnostic in ~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/out/statistics.json. Spearman between D_T (the FP–Joint displacement) and Joint's prior departure is 0.918 pooled (0.941 Cho, 0.919 Lee). It fails on B14, where 18/27 Joint priors sit at the Dirichlet floor.
- **Prop 5:** an uncommitted synthetic label-shift grid in the same folder. FP falls behind Joint as the prior mismatch grows: Δ_BA goes from −0.0006 to −0.0223.
- **Cor S10:** h2cmi/EXPERIMENTS.md L37 states that no experiment on the server knows θ0, by design.

**Corrections to the tracer's rows**
- Sleep fit-prior mismatch per unit is 0.624 under the uniform prior actually used, against 0.406 had the empirical πsrc been used. The tracer's "≈0.56" is the mean-vector value.
- The ref count is 166 refs (104 unique tips), not 155.

**Mapping to the FP-GEM folder**
- The folder's docs say the theory and simulation code is local-only, not on the server: REVISION_PLAN_TSP_TPAMI.md L266 and L380-381; EXECUTION_KICKOFF_sprint0.md L89 and L116. This covers precheck_theory.py, convergence_sim/ and the fpgem package.
- Consistent with that: GitHub probes for separate FP-GEM repos under W-Yinghao returned "repository not found", and all 60 origin heads are present locally.
- The docs already flag three of the gaps above:
  - Prop 4's penalty wording: REVISION_PLAN_TSP_TPAMI.md L207 and L248; FP_GEM_REVISION_v3 L195-205.
  - The raw-posterior argmax on MI not being a uniform class-conditional decision: FP_GEM_REVISION_v3 L1028.
  - S9's real-data counterpart: REVISION_PLAN_TSP_TPAMI.md L107.
- REVISION_PLAN_TSP_TPAMI.md L60 claims a "later round" of FP/Joint runs on 07-27/28. No such MI run exists on the server.

## G04_sim_local_response_fig2A — Main p.6 §5.1 'The local response predicts…' + Fig 2A (p.7); Supp p.5–6 §F.1 'Numerical checks', Table S1 row 'Local-response calculation', §F.2

### Tracer
I could not trace G04 on this server. Every number in the group is UNTRACEABLE after a complete search:
- **Main p.6 §5.1 and Fig 2A (p.7):** the 4,000-fit local-response check (minimum cosine 0.9999999); the 2,038-fit local subset; R² = 0.998 (99.83%); median vector relative error 1.37%.
- **Abstract:** "R² = 0.998".
- **Supp §F.1/F.2 and Table S1:**
  - relative error: median 0.080%, maximum 0.357%;
  - the Hessian is negative definite in all 4,000 batches;
  - finite-difference discrepancies 2.0e-10, 1.4e-10 and 6.5e-11 (seed 913731);
  - projected-gradient pass on all fits, with 40 Joint fits (1.0%) at the |η| = 10 boundary;
  - execution environment and timings.

**Where I searched:**
- **Git refs:** all 166 refs in /home/infres/yinwang/CMI_AAAI (104 unique tips), via git grep for the sim constants and identifiers.
- **Git history:** every path ever committed on any ref (14,811 paths; list at /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g04_all_history_paths.txt), plus pickaxe searches over all history for 20270728, 913731, 0.9999999, d_eta and H/G symbols. The only hits are digit-level coincidences in the unrelated CSC, OACI and STAR projects.
- **Filesystem, by file name:** `find /home/infres/yinwang -maxdepth 9` for convergence_sim, mechanism_sim, multiclass_sim, optimal_sim, local_resp, fpgem, FP-GEM_AAAI, submission_2026-07*, main_submit_ready, precheck_theory and the SERVER_REPRO_CHECKLIST files. It completed with 0 hits. Output is in scratchpad agents/g04_find_home.txt.
- **Filesystem, by content:** grep over /home/infres/yinwang/CMI_AAAI (all worktrees, including H2CMI/*), ~/.cache/h2cmi_training_caches and ~/.cache/h2cmi_external. It completed with 0 relevant hits.
- **Supplement zip:** no copy of the OpenReview Code and Data Supplement zip exists anywhere in the home directory.
- **Partial search:** a shared /projects/EEG-foundation-model search timed out. That tree holds datasets only.

**Why the server code cannot be the source:**
1. **Optimizer.** The paper uses exact L-BFGS-B optima with analytic gradients and Hessians, and Joint-GEM's fitting logit η is boxed in [−10, 10]. The server GEM (h2cmi/tta/class_conditional.py at origin/exp/h2cmi-wave0-mechanism df47753e, same on origin/agent/fp-gem-stage2 04a40e4e) runs a fixed 20×3 Adam steps (L229, L235, L249-256), has no Hessian, and anchors Joint with κ = 6 (L243-245).
2. **No L-BFGS GEM.** The only L-BFGS-B call in any FP-GEM branch is BCTS temperature calibration (fp_gem_stage2_lib.py L51).
3. **Frozen evidence spine.** The spine at df47753e (h2cmi/results/fp_gem_main/fp_gem_theory_to_evidence.md: "These six rows are the complete empirical evidence spine") has no local-response or R² row.

**Closest server analogs.** These are different experiments and must not be mixed with G04:
- B1a C_prior_coupling: FP−Joint bAcc of +0.0076 to +0.0315 in the H2CMI EEG simulator (b1a_confirm.report.json).
- ~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/synthetic_regime.py: a 20-D Gaussian grid using the Adam GEM, bAcc only.
- The real-EEG V2P displacement, where fixed_iterative 0.640 equals joint 0.640 (REVIEW_P0_RESULTS.md L116-117).
- The P13 real-EEG Joint fitted prior, 0.4636 / 0.4850 / 0.5007 across q (I recomputed this). Only 30–40% of units have |η̂| ≤ 0.4.

**The authors' own documents say the simulation is local.** In /home/infres/yinwang/CMI_AAAI/FP-GEM, REVISION_PLAN_TSP_TPAMI.md L266 and L380, and EXECUTION_KICKOFF_sprint0.md L89 and L116, place convergence_sim and mechanism_sim, the "published fpgem package" and the AAAI tex source on the author's local machine. Supp F.1 names a Windows i7-9750H host, and no server conda env matches its Python 3.8.8 / NumPy 1.22.2 / SciPy 1.10.1 stack.

**Internal consistency.** The manuscript agrees with itself: main text, Fig 2A annotation, caption and supplement give the same 4,000, 0.9999999, 2,038 and 1.37% values; 0.9983 rounds to 0.998; and 4 × 5 × 200 = 4,000.

**What is needed to trace this group:** the OpenReview Code and Data Supplement zip (openreview.txt L47-48) or the author's local convergence_sim/ and mechanism_sim/ raw rows (per-fit θ_FP, θ_Joint, η̂_Joint, dη, Hessian eigenvalues, cosine and SHA-256 array fingerprint, master seed 20270728).

### Adversarial re-check
Adversarial re-check of G04 (controlled Gaussian local response, Fig 2A, Supp F.1/F.2, Table S1). All 11 original rows stay UNTRACEABLE, and I added a 12th row for main-text L724-728. Neither the producing code nor any output exists on the server.

What this pass searched, beyond the tracer's work:
- **Git history:** pickaxe `git log --all --reflog -F -S` in /home/infres/yinwang/CMI_AAAI for 0.9999999, 99.83, 2,038, i7-9750H, 195.6, 890.3, 930000, convergence_sim, mechanism_sim, moment-matching, fitting logit, local response, Priors Push, FP-GEM_AAAI and SERVER_REPRO_CHECKLIST. Every hit was an unrelated number in CMI-Trace, OACI, CSC or STAR data.
- **All ref tips:** `git grep` over the 104 unique tips (166 refs) for simulation-specific regexes. The only hits were false positives: the `fixed_logits` readout in run_fp_gem*.py, and the L-BFGS-B calls in tos_cmi/eval/readout_{calibration,prior}.py and h2cmi/fp_gem_stage2_lib.py L51.
- **Alternative names:** the user noted the FP-GEM code may be named differently. I scanned the 14,811 committed paths for other simulator names and checked h2cmi/data/paired_simulator.py, h2cmi/run_synthetic.py and h2cmi/THEORY.md. None of them is a 4-D Gaussian local-response study.
- **Unreachable objects:** `git fsck --unreachable` (193 blobs, 7 stash commits) gave 0 hits.
- **Independent clones:** H2CMI/.codex_p12_launch_5b71ee8, H2CMI/.codex_p12_launch_f34cc8b, and ~/.cache/h2cmi_training_caches/fp_gem_p13/repo_7b48813 and repo_afa21f2 contain no commits that are missing from the main repo.
- **Filesystem:** a full find over home (excluding anaconda3 and mne_data; completed in 189 s) turned up no convergence_sim, mechanism_sim, fpgem, SERVER_REPRO or FP-GEM zip.
- **Content grep:** covered H2CMI (qxu untracked results, _frozen_shards, shard_results_salvaged, paper_data), CMI_AAAI/results, CMI_AAAI/notes, ~/.cache/h2cmi_training_caches, AAAI_2026, ICML_2026 and slurm_logs.
- **Transcripts and scratch:** Codex sessions and attachments, Claude transcripts, and /tmp/claude-* scratchpads. None contains simulation content; the one "9750H" hit is inside a base64 blob.
- **SLURM:** slurm_logs file names show nothing. The sacct database was unreachable.

Where the numbers came from: the authors' own index (FP-GEM/REVISION_PLAN_TSP_TPAMI.md L132-135, L266, L380; EXECUTION_KICKOFF_sprint0.md L89, L116) places the producer in local-only convergence_sim/ and mechanism_sim/, run on a Windows laptop (Supp F.1). The OpenReview "Code and Data Supplement" zip (openreview.txt L48) is not on the server.

The server's FP-GEM code cannot produce these numbers:
- FP-GEM is `gen_iterative_diag` and Joint-GEM is `joint_iterative_diag` in h2cmi/tta/class_conditional.py @df47753e.
- It uses Adam for 20 outer rounds of 3 steps (L229/L235/L250), a Student-t density, and a κ=6 Dirichlet prior update (L243-245; config.py L110-111).
- It has no Hessian, no fitting-logit parameter and no L-BFGS-B.

Internal consistency checks:
- 4×5×200 = 4,000 fits; 2,038/4,000 = 51%; 40/4,000 = 1.0%.
- 1/(1+e^10) = 4.54e-5, which is consistent with "within 4.6e-5".
- R² = 0.998 and 99.83% agree.
- Minimum cosine 0.9999999 and maximum relative error 0.357% can both hold only if the finite-difference error in the worst fit lies almost entirely along the derivative. That is possible but worth checking on a rerun.

One real internal inconsistency: main text L724-726 says all 4,000 fits pass the finite-difference (2.0e-10) check. Supp F.1 L762-766 says that check ran on a single off-grid batch (nA = 173, seed 913731).

Context only, not traces:
- P13 real-EEG Joint |η̂| ≤ 0.4 fractions, recomputed: 37.7%, 40.1% and 29.6% at q = 0.1/0.5/0.9, over 162 units each.
- Regime-analysis Spearman between D_T (the FP-vs-Joint transform displacement) and the Joint prior's distance from the source prior (d_joint_src): 0.918 pooled (n = 115; ~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/out/statistics.json). This is a rank correlation of magnitudes, not a first-order vector R².

Two ways to substantiate these numbers: get the OpenReview zip or the author's local package, or re-implement the study CPU-only from Table S1 and the seed recipe (Sprint-0 T2). The seed-string formatting is not fully specified, so bit-exact batches may not reproduce.

## G05_sim_batch_size_tableS2_fig2B — Main p.6 §5.1 'Overlap creates a weak direction…' first paragraph + Fig 2B (p.7); Supp p.6–7 §F.3 + Table S2

### Tracer
I could not trace any number in G05 to code or results on this server. All 23 rows are UNTRACEABLE. The paper's own numbers are internally consistent, with two small wording problems and one inconsistency about which cells Fig 2B omits.

**Where I searched (read-only):**
- **Git:** all 166 refs in /home/infres/yinwang/CMI_AAAI (104 unique tips, 2 stashes). `git ls-remote origin` shows GitHub W-Yinghao/CMI has 60 heads, all identical to the local origin/* refs, so nothing is unfetched.
  - `git grep` over every tip for convergence_sim, mechanism_sim, multiclass_sim, optimal_sim, 20270728, i7-9750, fitted.logit and the Table S1 grid literals returned no relevant hits.
  - `git log --all --name-only` shows no simulation path was ever committed.
- **Filesystem:**
  - A name search of /home/infres/yinwang (depth 7) and /tmp (depth 6) found no convergence_sim, mechanism_sim, FP-GEM_AAAI2027, journal_revision, precheck_theory or fpgem.
  - No fpgem package in any conda env or ~/.local.
  - The OpenReview code_and_data_supplement is not on the server.
  - A content grep for the Table S2 values found only coincidental digit matches, e.g. `class_occupancy` 0.068041 in `H2CMI/CMI_AAAI_qxu/results/h2cmi/b1a_confirm.jsonl`.

This matches the paper: Supp F.1 says the run was on a Windows i7-9750H laptop.

**Upper-folder docs** (/home/infres/yinwang/CMI_AAAI/FP-GEM):
- `REVISION_PLAN_TSP_TPAMI.md` L132-135, L266 and L380 list the local-only directories convergence_sim/ and mechanism_sim/ (also multiclass_sim/, optimal_sim/, version_b_optimal/).
- `EXECUTION_KICKOFF_sprint0.md` L89 and L116 put T2 (local) on a 'published fpgem package' whose acceptance test is reproducing convergence_sim.
- L132 calls convergence_sim the 'strict-convergence version of Table S3'. So it is not established which local script produced Table S2; convergence_sim is a hypothesis, and mechanism_sim is equally possible.
- I treated these as documents to read. I did not execute any Sprint-0 tasks (T2 and later).

**Server experiments that must NOT be substituted:**
- B1a H2CMI EEG-simulator grid (`origin/exp/h2cmi-wave0-mechanism:h2cmi/run_b1a_grid.py`, `results/b1a_confirm.report.json`; bAcc FP−Joint +0.012..+0.032, no transform-MSE, no nA axis).
- `~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/synthetic_regime.py` (20-D, Adam GEM, ΔBA only; it calls itself a 'Reconstruction, not the original protocol').
- W0.4 real-Sleep batch sweep (`h2cmi/run_w2_wave0_batchsweep.py`, `results/w04_by_n.csv`; n=16..256, decision-prior P_J).
- The server GEM (`h2cmi/tta/class_conditional.py` L229-256: Adam, 20×3 steps, trust region) cannot have produced Table S1's L-BFGS-B multistart results. The only L-BFGS-B on the server is BCTS calibration (`origin/agent/fp-gem-stage2:h2cmi/fp_gem_stage2_lib.py` L51).

**Internal consistency check** (`scratchpad/agents/g05_tableS2_consistency.py`):
- All 20 Table S2 means equal their bracket midpoints to within 5e-6, i.e. symmetric Student-t intervals with t=1.972.
- The differences of means at t=0.5 (−0.0666, −0.0626, −0.0672, −0.0574, −0.0644) and t=1.5 (−0.0818, −0.0112, −0.00117, −0.00033, −0.00026) match the Fig 2B points read from a 400-dpi render (`scratchpad/agents/g05_fig2B_crop.png`).
- They also match Table S3 (−0.0672, −0.0012) and the main text (−0.00117).
- For t=0.35 and t=0.75, only the nA=500 points can be checked, against Table S3 (−0.0332 and −0.0719).

**Problems to fix in the revision:**
1. The main text says 'Figure 2B shows' absolute FP MSEs of 0.0680 → 0.00316, but Fig 2B plots only the FP−Joint difference.
2. Fig 2B drops t=1.5 at nA=200 as well as nA=100, but F.2 calls only nA=100 boundary-sensitive.
3. 'Both ≈0.003 at t=1.5' holds only at nA=2000; at nA=500 both are ≈0.014.
4. F.3 says the two estimators 'concentrate together by nA=500', yet the paired difference at nA=500 is still nonzero: −0.0012 [−0.0021, −0.0002].
5. The fitted-logit SDs (1.48, 2.21, 1.65, 0.050), the 40 boundary hits and the exclusion-robustness claim have no second source anywhere.

**Action for the owner:** the raw per-batch rows and the per-cell summary exist only on the author's local machine (Windows host). Committing convergence_sim/ and mechanism_sim/ with their raw output (optimizer status, selected start, fitted η, boundary flags) is required before G05 can be traced. No EEGNet or TSMNet real-EEG numbers are involved in this group, so there is no risk of mixing runs.

### Adversarial re-check
Re-check verdict: all 21 rows stay UNTRACEABLE on the server; no status changes. No code or output for the controlled 4-D Gaussian study (Table S1/S2, Fig 2B, F.1–F.3) exists on this server, despite a much wider search than the tracer's. The search covered:
- git pickaxe on the Table S2 values, 195.6 and the seeds;
- all 14,811 historic paths, including reflog and both stashes;
- git grep of all 104 unique tips;
- a tolerant ±5e-6 numeric scan of 81,074 text files, which found only coincidental hits in large dumps (scripts in scratchpad/agents/g05r/);
- find over /home/infres/yinwang and /tmp;
- Claude transcripts;
- GitHub ls-remote probes of 8 candidate repos, and PyPI.

The upper-folder docs agree with the paper: /home/infres/yinwang/CMI_AAAI/FP-GEM/REVISION_PLAN_TSP_TPAMI.md L6, L59, L132-135, L266 and L380, plus EXECUTION_KICKOFF_sprint0.md L89/L116, place the producers in the author's local directories (`FP-GEM_AAAI2027/`, `convergence_sim/`, `mechanism_sim/`, a local `fpgem` code package). The server's frozen FP-GEM evidence spine (df47753e fp_gem_theory_to_evidence.md) never included this study; its only controlled evidence is the B1a EEG simulator.

The paper is internally consistent. Every Table S2 mean is its CI midpoint, the Fig 2B t=0.5 and t=1.5 points equal the differences of the Table S2 means, and the nA=500 points match Table S3 and the main text. New check: nA × FP-MSE is 6.3–7.2 in all 10 cells, which is 1/nA scaling close to the ≈6.2/nA asymptotic variance. This implies 'MSE' means the summed squared error over the 8 transform parameters, a definition the paper never states.

Issues to fix in the text:
1. Main L697 says 'Figure 2B shows' absolute MSE, but Fig 2B plots only FP−Joint differences.
2. Fig 2B drops the t=1.5, nA=200 cell without a stated reason; F.2 names only nA=100.
3. Main L702 'both ≈0.003' holds only at nA=2000.
4. F.1 L827 says 'objective-matched' where everywhere else says 'source-matched' or 'proportion-matched'.
5. Main L726 'every tested cell with t≤0.75' should read 'every matched-proportion batch-size cell'.
6. Four of five points on each of the t=0.35 and t=0.75 curves, and all fitted-logit SDs (1.48/2.21/1.65/0.050), have no numeric source anywhere.

Tracer correction: 'the only L-BFGS-B on the server is BCTS' holds only within the FP-GEM/H2CMI code. Unrelated TOS files, tos_cmi/eval/readout_calibration.py L46/L65 (e.g. 2677709f) and readout_prior.py, also use it.

Next step: get the local convergence_sim/mechanism_sim per-fit raw rows from the author.

## G06_sim_mismatch_tableS3_fig2C — Main p.6 §5.1 second paragraph (nA=500 contrasts) + Fig 2C (p.7, symmetric-log axis); Supp p.6 §F.4 + p.7 Table S3

### Tracer
Verdict for G06 (Table S3, Fig 2C, main §5.1 nA=500 contrasts): all 21 rows are UNTRACEABLE on this server. There is no code, raw output or figure source for the paper's controlled Gaussian prior-mismatch study anywhere I could reach.

Search coverage:
- Git: all 166 refs (104 unique tips) with git grep for sim names, seeds and constants in code and text files. Full history (1,824 commits) via pickaxe: -S20270728 found 0 commits; -G on convergence_sim, mechanism_sim, multiclass_sim, optimal_sim, i7-9750H and precheck_theory found 0. Both stashes checked, plus 4 standalone clones (H2CMI/.codex_p12_launch_5b71ee8, H2CMI/.codex_p12_launch_f34cc8b, fp_gem_p13/repo_7b48813, fp_gem_p13/repo_afa21f2), which have no refs missing from the main repo.
- Filesystem: a completed name search to depth 8 over /home/infres/yinwang (large dirs pruned). A content grep over CMI_AAAI, AAAI_2026, ~/.cache/h2cmi_training_caches, ~/.codex and ~/.claude. /projects/EEG-foundation-model and /tmp to depth 4. A co-occurrence search for the Table S3 values found only chance float substrings. The paper's .tex source is not on the server either.

The upper folder /home/infres/yinwang/CMI_AAAI/FP-GEM agrees that this study is local-only:
- REVISION_PLAN_TSP_TPAMI.md L132-135, L266 and L380 put `convergence_sim/` and `mechanism_sim/` in the laptop tree FP-GEM_AAAI2027/.
- EXECUTION_KICKOFF_sprint0.md L89 and L116 set T2's acceptance test as "reproduce convergence_sim's Table S3".
- REVISION_PLAN_v2_divergent.md L109, L149 and L165 and REVISION_PLAN_v4_positive_claims.md L155 and L212 say the same.
- This matches Supp F.1: a Windows i7-9750H host, Python 3.8.8, NumPy 1.22.2, SciPy 1.10.1.

One ambiguity must be resolved on the laptop. The TSP plan (L132, L266) calls `convergence_sim` the "strict-convergence version of Table S3, conclusion unchanged". That could mean it produced the submitted objective-matched Table S3 (L-BFGS-B multistart, master seed 20270728). It could also mean it produced the strict identity-started EM check (Table S4, seed 930000), in which case the submitted Table S3 came from `mechanism_sim` or an earlier script.

What I could verify is that the paper's numbers are internally consistent (pure arithmetic; script at scratchpad/agents/g06_internal_consistency.py):
- All 12 Table S3 intervals are symmetric about their means, as Student-t intervals with n=200 should be.
- In every row, ΔMSE and ΔBA have opposite signs.
- The main text's −0.0672, 0.632, −0.00117 and 0.198 match Table S3 exactly or after rounding.
- The Table S2 marginals reproduce the ρ=.50 row: 0.01276 − 0.07992 = −0.06716, and 0.01379 − 0.01496 = −0.00117.

Do not substitute server artifacts for this study. Two are easy to confuse with it:
- The server's "controlled" evidence row (df47753e fp_gem_theory_to_evidence.csv, B1a +0.012 to +0.032) comes from the H2CMI EEG simulator.
- regime_analysis_20260728T064406/synthetic_regime.py is a 20-D pure label-shift grid (132 cells, 24.2% FP wins) that uses the κ=6 Adam GEM.

Both are different designs, and their estimators differ from the paper's unanchored L-BFGS-B Joint MLE. Where comparable, the regime values disagree with Table S3; at sep 0.3 and ρ=.5 its ΔBA is exactly 0. This bears on T2: reproducing Table S3 needs the local `convergence_sim` code and raw rows (with the per-row SHA-256 array fingerprints), not the server's h2cmi/tta/class_conditional.py.

Action item: ask the owner for a copy of the laptop FP-GEM_AAAI2027/convergence_sim (and mechanism_sim) scripts, raw per-batch rows and the Fig 2 plotting script. Then record their hashes in manuscript_result_map.csv.

### Adversarial re-check
RE-CHECK VERDICT: The claim that the authors' code and artifacts are not on the server holds up under a harder search. Calling the NUMBERS "untraceable", however, is too pessimistic. I wrote an independent implementation using only the paper text (main §5.1 eqs 13-16 and Supp Table S1). It regenerates every Table S3 cell exactly at the printed precision: 12 cells, 24 point estimates, 48 CI bounds. The one exception is a last-digit difference in one lower bound: ΔBA(0.50,0.50) comes out 0.52846 against the printed 0.529, which is consistent with rounding the mean and the half-width separately. The same code also regenerates:
- all 20 FP/Joint means in Table S2;
- the §F.3 fitted-logit SDs (1.478 / 2.209 at t=.5, 1.646 / 0.050 at t=1.5);
- every main-text §5.1 mismatch number (−0.0672, 0.632 [0.529, 0.735], −0.00117, 0.198 [0.126, 0.270]).

Script: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g06r_full17g.py (sha256 e59481ed…). It imports g06r_indep_resim.py and g06r_variant2.py from the same folder. Output: g06r_full17g_out.json (sha256 039fef77…). Supporting runs: g06r_tableS2_check.txt, g06r_tstr.py, g06r_gen_variants.py. Runtime is about 4 minutes on 1 CPU. No training and no SLURM.

Conventions the paper leaves unstated but that are needed for an exact match:
1. In the seed string SHA256('20270728|nA|t|rho|s'), t and ρ are formatted with 17 significant digits ('%.17g'): 0.35→'0.34999999999999998', 0.7→'0.69999999999999996', 0.92→'0.92000000000000004'. Python str/repr reproduces only the three ρ=.5 cells at t∈{.5, .75, 1.5}, plus Table S2.
2. y=+1 iff U(0,1)<ρ is drawn first, then standard_normal((nA,4)).
3. The objective is the negative log-likelihood averaged over the batch (mean, not sum).
4. The moment-matching start matches the mixture mean (2π−1)t and variance 1+4π(1−π)t².
5. BA is analytic: ½[Φ(t−c)+Φ(t+c)], where c is the sign-rule threshold.

The ρ=.5 row reuses the source-matched batches: FP 0.012761 / Joint 0.079924 is identical to Table S2 at nA=500, t=.5.

So the published Table S3 and Fig 2C values are genuine and reproducible from the paper's own specification. Provenance is still missing: no authored script, no raw rows with fingerprints, and no figure file anywhere on the server. The revision docs put them locally: /home/infres/yinwang/CMI_AAAI/FP-GEM/REVISION_PLAN_TSP_TPAMI.md L6, L132-135, L266, L380-381 (laptop tree FP-GEM_AAAI2027/convergence_sim, mechanism_sim; journal_revision/prechecks/precheck_theory.py).

Additional searches this round (all read-only, all empty):
- git log --all --reflog -G on isolated tokens 1.1287 / 7.548 / 1.0784: 0 commits. Plain -S hits were chance float substrings, e.g. S2P 4d45a89f, OACI d2720b85, initial fb2a8781.
- grep -rIlE on the isolated tokens over CMI_AAAI/H2CMI (including CMI_AAAI_qxu untracked results, paper_data, shard_results_salvaged, _frozen_shards), CMI_AAAI/results, notes, h2cmi and ~/.cache/h2cmi_training_caches: 0 files. Every grep finished (exit 1, no timeout). Log: g06r_fs_grep.txt.
- 193 unreachable blobs and 7 unreachable WIP/index commits from fsck: 0 hits.
- git ls-remote origin: 134 refs, all present locally except the GitHub auto-merge refs refs/pull/{2,3,4}/merge. The PR heads themselves are present.
- 150 git repos under ~ (depth 5): no FP-GEM remote (gh is not installed).
- ~/.claude/projects and ~/.codex transcripts: convergence_sim, FP-GEM_AAAI2027 and 20270728 appear only in this session.
- No SERVER_REPRO_CHECKLIST_REQUEST, sleep_result_provenance, journal_revision, prechecks or main_submit_ready anywhere.
- /data, /scratch, /store, /work: no user files at depth 4.
- Commit messages: only unrelated W0.3 'metric-prior mismatch' commits.

Repository discrepancy to flag: the frozen evidence spine df47753e:h2cmi/results/fp_gem_main/fp_gem_theory_to_evidence.csv cites B1a (EEG-simulator BA +0.012 to +0.032) as the 'controlled' evidence. The paper reports this 4-D Gaussian study instead, and nothing in the repo indexes it.

Actionable: the sprint-0 T2 target ('reproduce convergence_sim's Table S3', EXECUTION_KICKOFF_sprint0.md L89) is already met by the audit script above. The Supp §F.1 seed specification should state the '%.17g' formatting and the draw order.

## G07_sim_optimizer_checks_config — Main p.5 §5.1 Design (λ=0, multistart, 200 paired batches, Eq 13–16) + p.6 'Optimization checks'; Supp p.5–6 §F.1 (Randomness and pairing, Numerical checks, Execution environment), Table S1, §F.2

### Tracer
G07 (the controlled Gaussian study: design, optimizer, checks and environment) cannot be traced on this server. I did not find a single claim in the group in code or result artifacts. Every row is UNTRACEABLE. None is a MISMATCH, because there is nothing on the server to compare against.

Where I searched (read-only):
(1) git grep -w over all 166 local ref tips of /home/infres/yinwang/CMI_AAAI, plus stash@{0} and stash@{1}. I searched for 20270728, 913731, maxls, pgtol, multistart, fixed_logit, convergence_sim, the ℓ0/b0 constants, and the reported numbers (9750H, 0.9999999, 2,038, 195.6, 890.3, 6.5e-11, 1.4e-10, 2.0e-10). git ls-remote origin lists 60 heads, and all 60 commits exist locally, so this also covers GitHub W-Yinghao/CMI.
(2) Pickaxe across all history: git log --all -S20270728 returned 0 commits. -G for a standalone 913731 returned 0. --reflog returned 0. -G'pgtol|L-BFGS-B' returned only e5282225 (the Stage-2 BCTS temperature fit), afc857f3 and 09475f5c (CMI-Trace), all unrelated.
(3) find under /home/infres/yinwang (maxdepth 8) for convergence_sim, mechanism_sim, multiclass_sim, optimal_sim, version_b_optimal, FP-GEM_AAAI2027, journal_revision, fpgem*, precheck_theory, submission_2026-07-28 and *code_and_data*. Nothing found.
(4) Content grep for the seeds over all of /home/infres/yinwang/CMI_AAAI (every worktree, the .codex_p12 clones and _frozen_shards), AAAI_2026, ~/.cache/h2cmi_training_caches (including the P13 clones repo_7b48813 and repo_afa21f2), ICML_2026 and CS_QMI. 0 files.
(5) No conda env or ~/.local contains an fpgem package.

As you suggested, the FP-GEM code on this server goes by other names: FP = gen_iterative_diag, Joint = joint_iterative_diag, in h2cmi/tta/class_conditional.py at df47753e, with the FP/Joint switch at L406. It is a different estimator: Adam lr 0.05, autograd, fixed 20×3 steps, λ≠0 through the logdet 1 and trust-region 1/1 terms, and a single start. It could not have produced any §5.1 number. The server's own 'controlled' evidence is a different experiment: B1a on the H2CMI EEG simulator (h2cmi/results/b1a_confirm.report.json, 4,900 rows, FP−Joint +0.012..+0.032). There is also a 20-D Adam 'regime' reconstruction at ~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/synthetic_regime.py (rng seed 0, 3 reps). Do not mix either with the paper's 4-D L-BFGS-B study.

The revision docs in the parent folder place the study on the author's laptop. REVISION_PLAN_TSP_TPAMI.md L132-135, L266 and L380 name local FP-GEM_AAAI2027/convergence_sim/ and mechanism_sim/. EXECUTION_KICKOFF_sprint0.md T2 plans to reproduce convergence_sim Table S3 with the local 'published fpgem package'. The OpenReview record (openreview.txt L47-48) lists a 'Code and Data Supplement' zip, which is not on the server. The paper's own Windows i7-9750H environment agrees with all of this. The server is a Linux Xeon E5-2630 v4 with Py3.9.25, NumPy 1.26.4 and SciPy 1.13.1.

Three things in the paper text itself need fixing:
(a) Main p.6 says all 4,000 fits pass the 'finite-difference (2.0×10⁻¹⁰)' check. F.1 says the FD check was run on one deterministic batch (t=0.75, nA=173 off-grid, seed 913731 outside the SHA scheme), and 2.0e-10 is that batch's maximum discrepancy. The main-text wording overstates what was done.
(b) The same run is called 'proportion-matched', 'source-matched' and 'objective-matched'. The last is likely a typo.
(c) The seed-string format for t and ρ is unspecified, and it changes the seed: '0.5' and '0.50' give different seeds. The replication spec should pin it.

The paper's internal arithmetic is consistent: 20×200=4,000; 40/4000=1.0%; σ(−10)=4.54e-5 ≤ 4.6e-5; 99.83% corresponds to R²=0.998.

To close G07, the author needs to supply the local convergence_sim raw per-fit output (status, selected start, objective, iterations, gradient residual, boundary hits, array fingerprints) and the gradient unit-test script. Search log: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g07_search_log.txt (remote-heads list: g07_lsremote.txt).

### Adversarial re-check
Re-check verdict for G07: all 27 rows stay UNTRACEABLE. None moved to MATCH or MISMATCH. I verified the tracer's code and artifact statements and ran several searches the tracer did not; none of them turned up the controlled 4-D Gaussian simulation or its outputs on this server.

New searches, beyond the tracer's:
(a) A ripgrep of the whole of $HOME, including hidden and gitignored files, for 20270728, 913731, convergence_sim, mechanism_sim, FP-GEM_AAAI2027 and precheck_theory. The only real hits are the FP-GEM revision docs. The rest are float substrings.
(b) A full file-name listing of $HOME. It contains no fpgem, *_sim, submission_2026-07-28/-31, fpgem_v2_math_checks, SERVER_REPRO_CHECKLIST, code_and_data or LaTeX-source files.
(c) Word-level `git grep` over every ref of about 70 distinct git object stores under $HOME, and over the 193 unreachable blobs in /home/infres/yinwang/CMI_AAAI. No relevant hits.
(d) All Codex and Claude transcripts. The only relevant item is ~/.claude/history.jsonl line 190 (2026-07-28 17:09 CEST). It cites C:/Users/15339/Downloads/FP-GEM_AAAI2027/theoryfirst/experiment_results_table.tex and .../clarity/eeg_protocol_appendix.tex. That is direct evidence that FP-GEM_AAAI2027 sits on the Windows laptop, which agrees with the Windows build 26100 host stated in supplement §F.1.
(e) `git ls-remote origin` shows 60 heads, 66 tags and 7 pull refs. All are present locally except the GitHub-synthesized refs/pull/{2,3,4}/merge.
(f) Probes for W-Yinghao/{FP-GEM, FPGEM, fp-gem, fpgem, FP-GEM_AAAI2027} on GitHub all return "Repository not found".
(g) The three paper PDFs contain no embedded-file markers.
(h) No conda env runs Python 3.8.8.

The one server-side synthetic Gaussian script, ~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/synthetic_regime.py, calls itself "Reconstruction, not the original protocol". It is a different model: 20-D, pure label shift, no θ0 transform, Adam GEM. So the server agents never had the original simulation either.

The revision docs say where the missing pieces live: /home/infres/yinwang/CMI_AAAI/FP-GEM/REVISION_PLAN_TSP_TPAMI.md lines 59, 132-135, 266, 378-380 and 388, which name local `convergence_sim/` and `mechanism_sim/`, a code-only package at `output/submission_2026-07-31/FP-GEM`, and the LaTeX source under `submission_2026-07-28`. Recovering G07 needs the local laptop folder or the OpenReview code_and_data_supplement zip.

Minor corrections to the tracer:
- 930000 also appears as code in the S2P project (s2p/scripts/tueg_subject_loader.py L247; introduced at 12478063). This is unrelated to FP-GEM.
- The Table S1 prior-mismatch and EM-check grid spans 4 t × 3 ρ = 12 cells (2,400 batches), not only the three ρ values.
- The L-BFGS-B uses at ref tips also include unrelated tos_cmi readout files.

The tracer's internal-consistency notes all hold:
- 40/4000 = 1.0%, and σ(−10) = 4.54e−5 is within the stated 4.6e−5.
- 99.83% rounds to R² = 0.998.
- The seed depends on how t and ρ are formatted as strings; I confirmed three different seeds.
- The main text says every fit passed the finite-difference check, but §F.1 shows it was one unit check on a single batch.
- The same run is called three names: proportion-matched, source-matched and objective-matched.

Search log: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g07r_recheck_log.txt. Supporting files in the same folder: g07r_home_rg_all.txt, g07r_allrepos_grep2.txt, g07r_lsremote_all.txt.

## G08_sim_strict_EM_tableS4 — Main p.6 'Optimization checks' last sentence (EM matches direct to 1e−8); Supp p.6 Table S1 'Strict generalized EM' + §F.5 + p.7 Table S4 + following paragraph

### Tracer
G08 (the strict identity-started generalized-EM check, i.e. main p.6 '1e-8' + Supp Table S1 'Strict generalized EM' + F.1 seed/timing + F.5 + Table S4 + the following paragraph) is ENTIRELY UNTRACEABLE on this server: all 14 rows have no producing code and no result artifact. This is not a mismatch; the evidence simply is not here.

Where I searched:
- Git: all 166 refs (104 unique tips; remote list matches local, all objects present), using git grep for seeds 930000/913731/20270728, the Table S4 numbers 6074.3/2216.9/890.3, and the names convergence_sim/strict_em/generalized-EM/identity-started/L-BFGS-B/fixed_logit/mechanism_sim/multiclass_sim/optimal_sim/fpgem. I also ran a full-history pickaxe (`git log --all -S/-G`).
- Filesystem: content and name searches over /home/infres/yinwang, /projects (maxdepth 3), /tmp (maxdepth 4) and ~/.cache/h2cmi_training_caches.
- Only false hits came back. Seed 930000 appears only in the unrelated S2P loader s2p/scripts/tueg_subject_loader.py L247. ~/.cache/.../regime_analysis_20260728T064406/synthetic_regime.py is a different 20-D reconstruction using the Adam GEM (seed 0, 3 reps), not strict EM.

Where the code must be: the revision docs place it in the author's LOCAL `convergence_sim/`, described as the 'strict convergence version of Table S3' (/home/infres/yinwang/CMI_AAAI/FP-GEM/REVISION_PLAN_TSP_TPAMI.md L132, L266, L380; EXECUTION_KICKOFF_sprint0.md L89, L116), run on the Windows i7-9750H host (Supp F.1). It may also be in the OpenReview 'Code and Data Supplement' zip (openreview.txt L47-48) or the local `output/submission_2026-07-31/FP-GEM` package (TSP plan L59). None of these is on the server.

The server's FP-GEM/Joint-GEM is a different algorithm and cannot have produced these rows:
- Location: origin/exp/h2cmi-wave0-mechanism@df47753e, identical at origin/agent/fp-gem-stage2@04a40e4e.
- Code: h2cmi/tta/class_conditional.py::_fit_transform.
- It uses Adam (L229), a fixed `range(em_iters)` loop with em_iters=20 (L235; config.py L112), and 3 Adam steps per M-step (L250).
- It has no convergence test and keeps no objective trace. Its penalties are trust-region plus logdet, and the Joint prior anchor is kappa=6.

Internal-consistency checks, all arithmetic only (script at scratchpad/agents/g08_consistency.py):
- The counts agree: 12 cells x 200 = 2,400.
- Every Table S4 interval is centered on its point estimate.
- Every convergence percentage is a whole count out of 200.
- The 1-D joint-EM slow rate (1+t^2)S(t) predicts about 559 and 41 iterations to reach 1e-8 at t=0.75 and t=1.5, close to the table's 596.2 and 41.1. At t=0.35 it predicts about 22.5k, above the 10,000 cap, which fits the 83.5% convergence. It also reproduces the plan's 2814 iterations for 90% at t=0.35 (S(t)=0.8901398309). This is plausibility only, since the paper's model is 4-D affine.

Issues for the author:
- At t=0.75 every run converges (200/200), yet the strict-EM contrast is about 55% of the direct Table S3 contrast (dMSE -0.0406 vs -0.0719; dBA +0.511 vs +0.945). FP direct and EM agree to 1e-8, so the difference must come from Joint-GEM reaching different stationary points from the identity start, or from the different batches (seed 930000 vs SHA-256 master seed 20270728, so S3 and S4 are not paired). The paper does not discuss this.
- The closing claim that strict EM recovers 'the same variance-bias crossover' is not supported by any tabulated number, because Table S4 covers rho=0.5 only.

Next step: get the author's local convergence_sim folder or the OpenReview code zip. No MI/Sleep (EEGNet REVIEW_P0 or TSMNet P12) artifact is relevant to this group, and none was mixed in.

### Adversarial re-check
The adversarial re-check CONFIRMS every G08 row as UNTRACEABLE. No row can be upgraded to MATCH or downgraded to MISMATCH, because no strict-EM code or output exists anywhere on this server.

The revision docs in /home/infres/yinwang/CMI_AAAI/FP-GEM name the producer as the author's LOCAL `convergence_sim/`:
- REVISION_PLAN_TSP_TPAMI.md L132, L266, L380 (§11 index)
- EXECUTION_KICKOFF_sprint0.md L89, L116

Searches that went beyond the tracer's, all negative:
- A name find at maxdepth 8 under home for every local-only path in §11 (FP-GEM_AAAI2027, submission_2026-07-*, journal_revision/precheck_theory, *_sim, fpgem, code_and_data).
- /projects and /tmp.
- Every relevant archive listing.
- 193 unreachable git blobs and 7 stash commits.
- git grep over 104 unique ref tips for 10,000-iteration or 1e-8/1e-10 EM loops.
- Pickaxe for 6074.3, 2216.9, convergence_sim, 167/200, 198/200.

The only server GEM is h2cmi/tta/class_conditional.py::_fit_transform, identical at origin/exp/h2cmi-wave0-mechanism@df47753e and origin/agent/fp-gem-stage2@04a40e4e. Its line numbers are re-verified: Adam L229, fixed loop L235, kappa=6 prior M-step L243-245, 3 steps L250; config L112-113 sets em_iters=20 and em_lr=0.05. It is a different algorithm from the paper's strict EM.

Corrections to the tracer:
1. **Slow-rate plausibility numbers.** The paper stops on per-iteration MOVEMENT, so the 1-D movement-rule estimates are about 13,825 / 2,587 / 457 / 41 iterations, not 22,509 / 3,626 / 559 / 41. Conclusions are unchanged. The implied mean over converged runs is 5,298.6 at t=.35 and 2,138.3 at t=.50, both feasible.
2. **t=0.75 gap.** It cannot be attributed only to Joint. S3 and S4 use different seeds (20270728 vs 930000), so FP's own MSE also differs across the tables.
3. **Objective trajectories.** Contrary to the tracer, the server does record GEM objective trajectories: ~/.cache/h2cmi_training_caches/regime_analysis_20260728T064406/units/*.npz. There the Adam surrogate objective is non-monotone in 330/345 FP and 315/345 Joint runs. This does not contradict the paper, but it confirms that no server trajectory can back 'every recorded strict-EM trajectory is nondecreasing'.
4. **Nearest server simulation.** The only server Gaussian FP-vs-Joint simulation is regime_analysis .../synthetic_regime.py (2-class, 20-D, Adam GEM, self-labelled 'Reconstruction'). It is unrelated to Table S4.

Author-attention items:
- The t=0.75 EM contrast is about 55% of the direct Table S3 contrast, and the paper does not discuss it.
- The 'same variance–bias crossover' claim at L1016-1019 is never tabulated for rho≠0.5.
- The main text says 'matches to 10^-8', while the supplement says 'approximately'.
- F.1 says eight workers, but this run used six.

Resolution requires the author to upload convergence_sim/ and its raw rows, or the OpenReview code_and_data_supplement zip.

Scratch helpers: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g08r_recheck.py and g08r_tips.txt.

## G09_table1_sleep — Main p.7 Table 1 'Sleep' column + p.7 text ('1.9 points on Sleep-EDF', 'FP-GEM … 0.1 point below Source-only on Sleep-EDF'); Supp p.9 §H ('75×3=225 participant–seed predictions', 'available Sleep summary reports means only')

### Tracer
G09 (Table 1 Sleep column, the p.7 contrasts and the §H Sleep statements) traces to a single run: REVIEW_P0 W2 primary on origin/exp/h2cmi-review-p0-corrections. Raw compute was commit 278fc85e (runner h2cmi/run_w2_p0.py, eval h2cmi/eval/p0_eval.py L82-101), the analyzer is 8ea5f994 (h2cmi/analyze_p0_final.py L165-184), and the report is 5bc9bf07 (h2cmi/results/review_p0.report.json W2_primary.branch_mean_bacc).

I recomputed every cell from the raw rows at /home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/results/h2cmi/p0_w2_primary_all.jsonl. Its sha256 bc605da7… matches the committed p0_raw.sha256; the file has 2250 rows = 225 units x 10 branches. The paper columns map to the code branches as follows:

| paper row | code branch | recomputed |
|---|---|---|
| Source | identity_uniform | 65.72 |
| EA | source_recolored_ea | 65.30 |
| Diag-IM | latent_im_diag_uniform | 63.62 |
| Joint-GEM | joint_geometry_uniform | 63.72 |
| FP-GEM | fixed_iterative_geometry_uniform | 65.57 |

All five match the paper after rounding. The W0.1 deterministic rerun rounds to the same values.

The two text contrasts are differences of rounded means:
- FP−Joint is +1.85 [+1.27, +2.45] exactly (63/75 wins). This equals the report's CI; the paper's '1.9' is 65.6 − 63.7.
- FP−Source is −0.15 [−2.17, +1.80] (40/35), which is not significant; the paper's '0.1' is 65.7 − 65.6.

The same run also produced one-shot fixed-reference 69.5 and pooled 66.0. Both beat every displayed Sleep row and are omitted from the paper.

§H claims:
- 'means only' is true of the summary, but per-subject s.d. can be computed from the raw rows (Source 9.77, EA 10.15, Diag-IM 11.25, Joint 10.97, FP 10.85).
- '225 predictions per method' is right as a count (225 rows per branch). What is archived is unit metrics plus pred_hash, not per-epoch predictions.

The code behind the Sleep numbers does not implement the method as the paper describes it:
- FP-GEM's fixed prior is uniform 1/5 (p0_source.py L71/L78), not the empirical pi_src = [.34, .11, .35, .07, .13].
- The density head is a jointly trained Student-t, rank-2 plus diagonal, not a post-hoc diagonal Gaussian.
- Geometry is fitted with Adam (20x3 steps) and trust/logdet penalties, not L-BFGS; Joint uses a kappa=6 Dirichlet anchor.
- Diag-IM runs a fixed 40 steps, not 50 tuned epochs.
- There is no band-pass filter; each epoch is z-scored separately, and nights are cropped using the target hypnogram (a firewall concern).
- Source training is a fixed 30 epochs with no validation.
- 'EEGNet' is the H2CMI EEGNet-style temporal branch plus an MLP to a 16-d latent.

Provenance cautions:
- Do not mix this EEGNet REVIEW_P0 run with TSMNet P12.
- The 07-28 Stage-2 Sleep dump is incomplete (196/225) and is not the source.
- FP_GEM_RESULTS_SO_FAR.md mislabels Diag-IM as SPDIM and FP−Source as FP−Joint.
- REVISION_PLAN_TSP_TPAMI.md is wrong to attribute the Sleep column to a 07-27/28 round.

Recompute notes are in /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g09_sleep_recompute.txt. No files were modified outside the scratchpad, and no SLURM jobs or checkouts were run.

### Adversarial re-check
I re-checked all three disputed G09 Sleep rows adversarially and all three stay MISMATCH. I searched all 166 refs with git log -S/-G, grepped the relevant files on every FP-GEM branch, and checked the qxu untracked results, the wave0 Sleep runners, the Stage-2 Sleep cache and FP-GEM/. None of these contains a Sleep run matching the paper's description.

(1) π_fit: every Sleep runner builds the source prior through get_source_p0, which calls reference_prior(..., "uniform"). This holds at 278fc85e, df47753e and 04a40e4e. 'source_marginal' appears in no commit after 0e6ebfd3. So the Sleep FP-GEM value of 65.6 comes from a fixed prior of [.2]*5, not from π_src ≈ [.339, .111, .351, .067, .132]. Uniform is about 2.3× further from the adaptation-night proportions in JS (0.080 vs 0.035). One correction to the tracer: the κ=6 Joint anchor is negligible on Sleep, because its weight 6/(n+6) is at most 0.9%.

(2) Density and optimizer: the Student-t hybrid-trained head and the Adam 20×3 fixed-budget GEM are confirmed. No L-BFGS GEM and no diagonal-Gaussian head exist on any ref; the only L-BFGS-B is BCTS in fp_gem_stage2_lib.py L51. New nuance: the [-2, 2] log-scale bound would never bind (max|a| = 1.264 over 450 fits). The 1.0/d-plus-logdet penalty, however, drives about a 2.7× expansion on 75% of latent coordinates.

(3) Preprocessing, training and firewall: sleep_eeg.py has one version ever (blob ff7ef451) and it has no band-pass. It applies a per-epoch z-score. Training is AdamW + cosine for a fixed 30 epochs, with no validation or patience and a CE+NLL+JS loss. Discarding movement and unscored epochs is disclosed in Supp §H. The hypnogram-based ±30-min crop is not disclosed. My read-only recompute, which reproduces the raw rows exactly (median n_A 1132, mean ρ_A), shows the crop removes about 57–59% of each night and cuts the wake share from 0.69 to 0.30. The target labels therefore fix the composition of A and E, which contradicts the stated label firewall.

Scratch script: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/sleep_crop_effect.py.

## G10_table1_B14 — Main p.7 Table 1 'B14' column + text ('1.3 on BNCI2014-001', 'FP-GEM is best on BNCI2014-001'); Supp p.8–9 §H (BNCI2014-001 retains four MI classes; 9 participants)

### Tracer
G10 (B14 column): 5 of the 6 displayed B14 numbers trace to real artifacts, but the FP-GEM and Joint-GEM cells, and the claims built on them, do not.

**What matches.** Source 61.0 (10.8), Recenter 72.7 (12.8) and SPDIM 72.7 (12.9) come from the P12 TSMNet fleet:
- Runner: h2cmi/run_fp_gem.py, launch commit e6c49156, runner sha 720b91b1, config d44fd98a.
- Results CSV sha f3e4ca69…, byte-identical at 3bba1d0b (origin/exp/h2cmi-wave0-mechanism) and 3b52e202 (origin/agent/fp-gem-stage2).
- Recomputed values: 60.957 (10.801), 72.737 (12.820), 72.737 (12.914).
- The P9 external reference would print SPDIM as 72.8 (13.0), so the paper used the P12 in-unit rerun.

EA 60.1 (11.3) matches ~/.cache/h2cmi_training_caches/fp_gem_ea (runner run_ea_b14_lee.py @ab03bd7a, job 912270), giving 60.134 (11.311). It is not committed to git. The 9-participant LOSO structure matches.

**What does not match.**
- **GEM cells:**
  - FP-GEM paper 73.2 (11.5) vs artifact 71.245 (11.480).
  - Joint-GEM paper 71.9 (11.3) vs artifact 70.936 (11.337).
  - Both are constant upward shifts (+1.96 and +0.96 pp) with identical s.d. Every independent recompute gives the artifact values: Stage-2 per-trial npz, the 07-28 regime re-run, and FP_GEM_RESULTS_SO_FAR.md.
  - Nothing on the server produces the paper values. I searched all 121 git refs, the FP-GEM history after 07-26, the H2CMI clones, and the caches.
  - The revision plan (REVISION_PLAN_TSP_TPAMI.md L60) says the GEM numbers come from a "later round". The server's 07-27/28 round reproduces P12, and no later round exists here, so any such run would be local-only.
- **Consequences for the text:**
  - FP − Joint is +0.31 pp [+0.05, +0.51], not +1.3.
  - "FP-GEM is best on B14" is false: FP trails Recenter and SPDIM, which tie at best, by 1.49 pp (CIs just cross 0). The bold/underline marks are inverted.
- **Protocol (supplement §H vs code):**
  - B14 is 2-class (LeftRightImagery, Linear(210,2), [36,36]), not 4-class. No 4-class path or checkpoint exists.
  - The split is session 0 runs 0–2 → runs 3–5, not cross-session.
  - The GEM readout is the frozen TSMNet classifier, not a diagonal-Gaussian density head. The density is Student-t, the optimizer is Adam 20×3 rather than L-BFGS, and Joint uses κ=6.
  - Preprocessing is 8–30 Hz, 0–2 s, per-trial z-score.
  - Diagnostic: the density-head readout from the stored responsibilities gives only about 56.6% on A.

**Do not mix:** the Sleep column is EEGNet REVIEW_P0 and belongs to a different group. W1-repaired H2CMI B14 (FP 71.35, Joint 70.11) is a different encoder and also does not match. The authoritative B14 source is P12.

Files: /home/infres/yinwang/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8/h2cmi/results/fp_gem_main/{fp_gem_per_subject.csv, fp_gem_results.csv, fp_gem_contrast_ci.csv, fp_gem_config.json}.

### Adversarial re-check
Adversarial re-check of G10 (the B14 column), read-only. I found no artifact that reproduces the paper's B14 GEM cells. All 9 flagged rows stand: 8 MISMATCH and 1 UNTRACEABLE (the upper-folder 'later round' claim). I also confirmed the matching cells: Source 60.957 (10.801), EA 60.134 (11.311), Recenter 72.737 (12.82), SPDIM 72.737 (12.914), and 9 participants in a LOSO split. These come from P12 (fp_gem_per_subject.csv sha 215d32b6, byte-identical at 3bba1d0b on origin/exp/h2cmi-wave0-mechanism and at 3b52e202 on origin/agent/fp-gem-stage2) and from the ~/.cache EA runs.

B14 GEM values in the artifacts:
- FP-GEM 71.245 (11.48); the paper has 73.2 (11.5).
- Joint-GEM 70.936 (11.34); the paper has 71.9 (11.3).
- FP − Joint = +0.31 pp [+0.05, +0.51], not the +1.3 in the paper.
- FP-GEM ranks third, behind Recenter and SPDIM, which tie for best, so the bold/underline markings in Table 1 are inverted.

Searches for a source of the paper values, none of which matched:
- git log --all with -S and -G over fp_gem/FP_GEM/tex paths.
- Every B14 per-subject aggregate computed from 150 branch tables (at df47753e, 04a40e4e, 5bc9bf07, 09e92499) and 866 on-disk tables.
- A text grep over H2CMI, results, notes, FP-GEM and the cache.
- 193 unreachable blobs.
- A completed depth-5 find over $HOME.
- Recomputed alternative estimators from the Stage-2 per-trial logits (3-seed ensembles, adaptation set A, A∪E, per-seed, max over seeds), the Stage-2 BCTS ensemble (FP 73.30 / Joint 73.15), and the density-readout H2CMI line (FP 71.35 / Joint 70.22).

Protocol checks:
- Every B14 artifact is 2-class (LeftRightImagery). MOABB B14 has 4 classes and 2 sessions.
- The split uses session 0 only: runs 0-2 adapt, runs 3-5 evaluate. It is not cross-session.
- Preprocessing is 8–30 Hz, 0–2 s post-cue, with a per-trial z-score.
- The GEM runs use a Student-t density, Adam for 20×3 steps, a κ=6 Dirichlet prior update and the frozen-TSMNet readout. None of these is what §H describes.

Notes for the orchestrator:
- The upper-folder docs already record several of these discrepancies (REVISION_PLAN_v2_divergent.md L225-229).
- REVISION_PLAN_TSP_TPAMI.md L60 claims the FP/Joint numbers come from a later round. That round is not on the server: every round after P12 reproduces P12 exactly.
- The uniform +1.0/+2.0 offsets with unchanged s.d. need author verification against the local submission package.

Scratch files are in /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/: g10r_scan.py, g10r_trees/, g10r_disk_list.txt, g10r_find_local.txt and g10r_stage2_summary.json.

## G11_table1_Cho — Main p.7 Table 1 'Cho' column + text ('0.8 on Cho2017', 'best on … Cho2017'); Supp p.8–9 §H (52 participants, left vs right)

### Tracer
G11 (Table 1, Cho column) traces to one artifact set that was never committed: /home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_cho/cho_target{1..52}_seed{0,1,2}.json. There are 156 files, all stamped commit 04a40e4e. They were produced by h2cmi/run_fp_gem_cho.py on origin/agent/fp-gem-stage2 (runner 4be89b0d, EA arm 1b89a32d, forced fresh source training 04a40e4e), launched from /home/infres/yinwang/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8 as SLURM array 912386, 156/156 ok. Averaging seeds within participant (n=52, sample s.d.):

| Method | Artifact | Paper | Status |
|---|---|---|---|
| Source | 52.35 (3.09) | 52.3 (3.1) | match |
| EA | 52.19 (2.92) | 52.2 (2.9) | match |
| Recenter (rct) | 59.75 (7.61) | 59.8 (7.6) | match |
| SPDIM (spdim_geodesic arm) | 59.66 (7.57) | 59.7 (7.6) | match |
| Joint-GEM | 59.19 (7.13) | 59.2 (7.1) | match |
| FP-GEM | 58.98 (7.14) | 60.0 (7.1) | **mismatch** |

- **SPDIM source:** only the Cho-cache spdim_geodesic arm reproduces 59.7 (7.6). P9 geodesic gives 59.6 and spdim_bias gives s.d. 7.7, so the column comes from this fleet, not P9.
- **FP-GEM cell:** the s.d. is identical but the mean is +1.02 higher than the artifact.
- **Independent check:** the reload-only regime re-inference (job 913011) reproduces FP and Joint bAcc exactly on 156/156 units. No α-path variant reaches 60.0.
- **Search for a 60.0 source:** nothing found. I checked the other result caches and the W1-repaired H2 encoder, all refs with `git log --all` for late Jul–Aug (no FP-GEM commit after 04a40e4e), and ran find/grep over the home directory. REVISION_PLAN_TSP_TPAMI.md L57-61 attributes the FP/Joint numbers to a 'later round'. The only such round on this server is this fleet, and it yields 58.98.

**Downstream claims the artifact contradicts:**
- **"+0.8 on Cho2017":** the artifact gives FP−Joint = −0.21 points, paired 95% CI [−0.56, +0.14], wins/ties/losses 23/4/25. This also falsifies the lower end of the "0.8–1.9 on four benchmarks" claim in the Abstract, Contributions and Conclusion.
- **"FP-GEM best on Cho2017" and the bold:** Recenter is best (59.75) and SPDIM second. FP is 4th of 6 displayed rows and significantly below both: FP−Recenter −0.78 [−1.22, −0.32], FP−SPDIM −0.68 [−1.11, −0.24].

**Supp §H checks:**
- 52 participants, 3 seeds, left/right: match.
- The split description does not match. The code uses class_stratified_half within session 0, with target labels used to build the halves (w1_repaired_split.py L80-96, manifest @ab93820d). The quarantined legacy contiguous split gives completely different Cho numbers (source-only 89.4).
- Preprocessing (8–30 Hz, 2 s, per-trial z-score) and the GEM implementation (Student-t rank-4 density, Adam 20×3, κ=6 anchor, TSMNet linear readout) also differ from the paper's diagonal-Gaussian/L-BFGS/density-readout description.

**Backbone check:** the Cho column is TSMNet-only and does not mix in EEGNet REVIEW_P0 or H2-encoder W1 numbers. The H2-encoder Cho values (about 64%) are a different backbone.

Recompute script: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g11_cho_recompute.py. The manifest and P9 copies are g11_manifest.csv and g11_p9.csv in the same directory.

### Adversarial re-check
Rechecked all 5 flagged G11 (Cho) rows. All stay MISMATCH, now with more evidence. The Cho column comes from one fleet: run_fp_gem_cho.py @ 04a40e4e (origin/agent/fp-gem-stage2), SLURM 912386, with 156 JSONs in /home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_cho. Five of its cells match the paper exactly: Source 52.35, EA 52.19, Recenter 59.75, SPDIM-geodesic 59.66, Joint 59.19. The same files give FP-GEM 58.98 (7.14), not 60.0 (7.1).

I searched hard for a 60.0 source and found none:
- pickaxe over all 166 refs;
- unreachable git objects;
- the three nested clones;
- a numeric scan of 116 Cho CSV/JSONL artifacts;
- Claude and Codex session logs;
- a home-wide find for files modified 07-28 to 08-01.

The only 60.0 mean on the server is P9 seed-0 Recenter, 59.98 with s.d. 8.78, so it is not the source.

The four mismatched MI GEM cells (B14 FP, B14 Joint, Lee FP, Cho FP) each equal the unrounded artifact mean plus exactly 2, 1, 1 and 1, with s.d. unchanged. I report this pattern only and make no claim about its cause.

What follows from the artifacts:
- **FP−Joint on Cho** is −0.21 [−0.57, +0.15]; wins/ties/losses 21/6/25 with a proper tie tolerance. The paper says +0.8.
- **Ranking on Cho:** FP-GEM is 4th of the 6 displayed methods, significantly below Recenter (−0.78 [−1.22, −0.32]) and SPDIM (−0.68 [−1.12, −0.24]). Bold should go to Recenter.
- **Split:** the Cho split is a label-constructed class_stratified_half within session 0 (all trial IDs have run=0). The paper describes a chronological run split. By construction ρ_A = ρ_E = 0.5.
- **GEM protocol:** it does not match the paper. The code uses a Student-t head, Adam 20×3 steps, a κ=6 Dirichlet Joint update, a TSMNet linear readout and 20-epoch sources. What does match: π_src is empirical (uniform on Cho), the GEM is fitted after Recenter, and FP and Joint are readout-matched.

Scripts and outputs: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g11r/{cho_alt_aggs.py, scan_cho.py, scan_cho.out, manifest.csv}.

## G12_table1_Lee — Main p.7 Table 1 'Lee' column + text ('1.3 on Lee2019-MI', 'trails Recenter and SPDIM on Lee2019-MI'); Supp p.8–9 §H (54 participants)

### Tracer
The Lee column matches the P12 TSMNet run (origin/exp/h2cmi-wave0-mechanism, runner at launch commit e6c49156, results committed at 3bba1d0b; the result CSV is byte-identical on origin/agent/fp-gem-stage2 04a40e4e). The EA row comes from the uncommitted cache ~/.cache/h2cmi_training_caches/fp_gem_ea, produced by run_ea_b14_lee.py at ab03bd7a (job 912270).

Cells that match to rounding:
- Source 54.85 (4.90)
- EA 54.37 (4.31)
- Recenter 68.16 (10.00)
- SPDIM 67.65 (9.84). The SD 9.84 shows this is P12, not P9, which gives 9.88.
- Joint-GEM 66.27 (9.24)

The Recenter bold and SPDIM underline are also correct.

**FP-GEM cell: MISMATCH.**
- The paper prints 67.6 (9.3). Every artifact gives 66.56 (9.35), and five independent derivations agree exactly: the committed per-subject CSV, 162 raw unit JSONs, the Stage-2 re-fit logits, the 07-28 regime re-fit, and the P13 q=0.5 center.
- The authors' own draft table (FP_GEM_RESULTS_SO_FAR.md L45) reads 66.6 ± 9.3.
- So the paper value is exactly +1.0 with an unchanged SD. The same pattern appears in the B14 and Cho FP-GEM cells.
- I found no 'later round' on the server: no FP-GEM commit on any ref after 04a40e4e (07-27), and no submission_2026-07-28, FP-GEM_AAAI2027 or checklist-request files under /home/infres/yinwang.
- A diagnostic on the adaptation set also argues against the paper's Gaussian-head readout as the source: that readout gives about 61.9, not 67.6.

**Text claims:**
- '+1.3 on Lee' is a MISMATCH. The artifact gives +0.28 pt, 95% CI [-0.09, +0.67], not significant, with 23 wins, 15 ties and 16 losses (fp_gem_contrast_ci.csv row 11). The frozen P14 claim gate sets FP > Joint on natural transfer to false.
- 'Trails Recenter and SPDIM' holds, but the real gaps are larger than the paper implies: -1.6 and -1.1 pt, both significant.

**Protocol claims in Supp §H: all MISMATCH.**
- Split: one session's label-stratified interleaved halves (25/25), not earlier-session adapts and later-session evaluates. So there are no dependent sessions to average.
- Preprocessing: 8-30 Hz, 0-2 s and a per-trial z-score, not 4-38 Hz, 0.5-3.5 s and source-frozen normalization.
- Source training: 20 fixed epochs with a per-subject trial-tail validation set.
- Density: Student-t rank-4.
- GEM: Adam 20x3 steps with a kappa=6 Dirichlet anchor, not L-BFGS.
- Readout: the TSMNet linear classifier, not the density head.

**Related, not used in the paper:** P13 prevalence stress on Lee (b5fb5158) gives FP-Joint sensitivity -0.00074 [-0.0036, +0.0021], not supported.

Do not mix any of this with EEGNet REVIEW_P0: the Sleep column is a separate run.

The recompute script is /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g12/lee_stats.py; extracted CSVs are in the same folder.

### Adversarial re-check
I re-checked all five disputed G12 (Lee) rows adversarially, read-only. All five stay MISMATCH; I corrected the evidence and nuance in three places.

1. **FP-GEM 67.6 (9.3):** I could not find this value anywhere on the server. The P12 result is 66.56 (9.35), and five independent derivations agree. I also tried about 15 alternative aggregations and readouts (single seeds, median, adapt or pooled sets, density argmax, alpha-path, P13 q-levels, Stage-2, the W1-repaired H2CMI encoder, max/mean combinations); none gives 67.6 (9.3). Full-home ripgrep and git pickaxe searches found only unrelated float substrings.
   - The table was edited on the Windows laptop: `~/.claude/history.jsonl` L190 (2026-07-28 17:09) cites `C:/Users/15339/Downloads/FP-GEM_AAAI2027/theoryfirst/experiment_results_table.tex`. That is after the 08:04 server note, which still read 66.6.
   - Every server output from 07-27/28 reproduces P12. No Claude transcripts from that window survive, and sacct is unavailable.
   - Four cells (B14 FP, B14 Joint, Cho FP, Lee FP) have means moved by exactly +1.0 or +2.0 while their SDs are unchanged. A genuinely different estimator would be unlikely to do that. The authors need to check this.
2. **"1.3 on Lee":** the artifact gives +0.28 pt, CI [-0.09, +0.67], which crosses 0. The paper's 1.3 is simply its own 67.6 − 66.3. Correction to the tracer: the P12 FP/Joint comparison is readout-matched (both use the TSMNet classifier; only the prior M-step differs). What is wrong is the paper's description of that readout, not the matching.
3. **Split:** it is within one session (session 0, offline run 0 only), class-balanced using target labels. Correction to the tracer: it is close to chronological, not broadly interleaved. At most 10-11 trials cross the boundary around epochs 45-60. Lee's second session is never used as a target.
4. **Preprocessing:** 8-30 Hz and 0-2 s with a per-trial z-score, against the paper's 4-38 Hz, 0.5-3.5 s and frozen source statistics. Only the 250 Hz resampling and the use of all native channels match.
5. **GEM protocol:** the code uses a Student-t rank-4 density, Adam for a fixed 20x3 steps with logdet and trust-region terms, a Dirichlet κ=6 Joint prior and the TSMNet readout. What matches the paper is the empirical π_src, identity initialisation with π_fit=π_src, and the variants differing only in the prior M-step. No L-BFGS GEM exists on any of the 166 refs; the only h2cmi L-BFGS is the BCTS calibration in `fp_gem_stage2_lib.py` L51.

Scratch files are in `/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g12r/`: the search log is `search_log.txt`, alongside copies of the P12 and P13 CSVs, the config and the manifest.

## G13_eeg_protocol_hyperparameters — Main p.6 §5.2 'Datasets and splits', 'Models and comparisons', 'Implementation details'; p.7 top; Supp p.8–9 §H (all paragraphs)

### Tracer
G13 checks the paper's EEG protocol and hyperparameter text (main p.6 §5.2 and p.7 top; supplement §H) against the code that produced Table 1: 48 claims, 20 MATCH, 20 MISMATCH, 8 PARTIAL. For much of this protocol, the paper describes an implementation that does not exist on this server.

**Where the numbers come from.** The table mixes two runs, and they must not be mixed in any claim:
- **Sleep column:** REVIEW_P0 W2. Code is on `exp/h2cmi-review-p0-corrections` (tip 5bc9bf07); the raw run is commit 278fc85e, code_sig 763bf49d. Rows are in `/home/infres/yinwang/CMI_AAAI/H2CMI/CMI_AAAI_qxu/results/h2cmi/p0_w2_primary_all.jsonl` (sha bc605da7…). Backbone is the EEGNet-style H2 encoder.
- **MI columns:** TSMNet. B14 and Lee are P12 (launch e6c49156; merged at 3bba1d0 on `origin/exp/h2cmi-wave0-mechanism`, tip df47753e). Cho comes from `run_fp_gem_cho.py` on `origin/agent/fp-gem-stage2` @04a40e4e. EA is a separate runner.

**Shared code.** The GEM adapter is byte-identical on all four refs (df47753e, 04a40e4e, 5bc9bf07, 278fc85e):
- `h2cmi/tta/class_conditional.py`, sha 270c8933
- `h2cmi/config.py`, sha 6f274555
- `h2cmi/data/real_eeg.py`, sha 5aa28bcb

FP-GEM is the variant `gen_iterative_diag`; Joint-GEM is `joint_iterative_diag`.

**What matches:**
- LOSO, the Sleep night 1 → night 2 split, and the participant counts.
- Seeds 0/1/2 sharing folds and checkpoints within each run.
- Sleep channels, 100 Hz, 30-s / 3000-sample epochs, and the 5-stage label map.
- MI all-channels, 250 Hz, and left/right for Cho and Lee.
- TSMNet with domain-specific SPD batch norm.
- Density on the TSMNet pre-head 210-d tangent vector or the Sleep latent.
- The diag(e^ℓ)u+b transform with identity initialization.
- FP-GEM pinning π_fit, GEM acting after Recenter, and Recenter-only-BN.
- The Sleep uniform decision rule.
- Seed → participant aggregation with sample s.d.

**What does not match:**
- **MI split:** session 0 only, class-stratified halves built from target labels. It is not earlier → later session, and for Cho it is not chronological.
- **Source validation:** no participant-level 80/20 split. MI uses a per-subject trial tail; Sleep has no validation set.
- **Sleep preprocessing:** no 0.3–35 Hz filter.
- **MI preprocessing:** 8–30 Hz and 0–2 s, not 4–38 Hz and 0.5–3.5 s.
- **B14:** 2 classes, not 4.
- **Normalization:** per-trial or per-epoch z-score, not frozen source statistics.
- **Source training:** a fixed 20 epochs (MI) or 30 epochs (Sleep), no patience.
- **Density:** Student-t, low-rank + diagonal, floor 1e-2, not a diagonal Gaussian with floor 1e-4.
- **Sleep fitting prior:** uniform, not the empirical source proportions.
- **Regularizer:** logdet 1 plus trust-region 1/d, not a 1e-3 identity penalty.
- **Optimizer and stopping:** Adam lr 0.05, a fixed 20 × 3 steps, no [−2,2] bound (non-binding: max |ℓ| is 1.6) and no 1e-6 stopping rule, instead of L-BFGS with ≤100 iterations.
- **Joint prior update:** a Dirichlet anchor with κ = 5+1 = 6 pseudo-counts, not a responsibility average floored at 1e-4.
- **IM baselines:** 30 epochs (SPDIM) and 40 steps (Diag-IM), not 50 epochs tuned on source validation.
- **MI GEM readout:** the frozen TSMNet Linear(210,2) classifier, not the density head.

**Search scope.** I searched with `git grep` over h2cmi/ on every local and remote ref. The only L-BFGS anywhere is the Stage-2 calibration code (`fp_gem_stage2_lib.py` L51). There are no hits for patience, a variance floor, 4–38 Hz, 0.5–3.5 s, 0.3–35 Hz or a 1e-6 stopping rule. There is no `fpgem` code in `/home/infres/yinwang/AAAI_2026`. The `submission_2026-07-28` bundle cited by `EXECUTION_KICKOFF_sprint0.md` is not on the server.

**Implication.** The paper's §H describes a different implementation from the one that produced Table 1 (cf. the revision docs' "same name, different implementation" check). Any reproduction under the stated protocol needs new code (T2) and new runs. For B14 4-class and the cross-session MI split, that includes retraining. I wrote no files.

### Adversarial re-check
I re-checked all 19 flagged G13 rows and none changed status. All stay MISMATCH, each confirmed at the cited SHA and line.

**Where the paper's MI and Sleep settings come from.**
- **MI band, window and classes.** The paper's 4–38 Hz band, 0.5–3.5 s window and 4-class BNCI2014-001 exist only in the LPC-CMI/CIGL loader `cmi/data/moabb_data.py` (resample 128) and in `docs/CIGL_36_REPRODUCIBILITY_CHECKLIST.md` L39. No FP-GEM runner imports that loader.
- **FP-GEM MI loader.** FP-GEM always loads MI through `h2cmi/data/real_eeg.py`: 8–30 Hz, 0–2 s, left/right only, per-trial z-score. This file was written once (96146b6f) and is identical on every FP-GEM ref.
- **Sleep filter.** The 0.3–35 Hz filter appears only in `s2p/scripts/codebrain_isruc_s3_preprocess.py`, an unrelated ISRUC project.
- **Sleep cache spectrum.** The Sleep cache behind the Table-1 Sleep column has a flat spectrum from 30 to 50 Hz (−0.09 dB), so no 35 Hz low-pass was applied.

**No other GEM implementation.** I searched all 64 unique ref tips plus the filesystem under `H2CMI/`, `results/`, `notes/`, `~/.cache` and `AAAI_2026`. I found no GEM using L-BFGS, a diagonal-Gaussian head, early stopping (patience) or an iteration-stopping rule. Every GEM variant (`class_conditional.py`, `weighted_tta.py`, `oracles.py`) uses the same Adam loop: 20×3 steps, trust region 1/d, κ=6 anchor.

**Readout.** The only MI run that reads out through a density head is W1-repaired H2CMI, and it does not match the paper's MI GEM rows. It gives FP/Joint B14 71.35/70.22, Cho 64.0/64.1, Lee 72.2/71.7, against 73.2/71.9, 60.0/59.2 and 67.6/66.3 in the paper.

**Other confirmations.**
- Sleep source training uses all 189,997 source epochs (sum over the cache minus target 23), with no validation split.
- The Sleep fitting prior is uniform [0.2]×5, while the empirical source proportions are [.341, .111, .351, .065, .132].
- The MI split is a class-balanced half of session 0 only. Cho's adapt set is two class-blocked chunks, and 18.7% of Lee's eval trials come before the last adapt trial.

**The revision folder already agrees.** `/home/infres/yinwang/CMI_AAAI/FP-GEM/REVISION_PLAN_v2_divergent.md` L225-226 lists six paper ≠ execution items (binary B14, Student-t density, frozen-classifier MI readout, Joint κ=6, fixed-budget Adam with no stopping rule, `class_stratified_half` split).

**How definitive this is.**
- These are definitive mismatches for the cells the audited code reproduces exactly: the Sleep column, and MI Source, Recenter and SPDIM.
- For the MI FP-GEM and Joint-GEM means, the producing implementation is still unlocated. `REVISION_PLAN_TSP_TPAMI.md` L59-61 says they came from a "later round" whose outputs are local-only. The MI GEM rows are therefore mismatches against every implementation found, not proof of what produced them (the caution in v3 L761-765).
- The [−2, 2] constraint is absent from the code but never binds: max |ℓ| is 1.6 on MI and 1.26 on Sleep.

My notes are in `/tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g13r_notes.txt`.

## G14_headline_summary_claims — Abstract (p.1); Intro contributions (p.2); Fig 1 caption (p.2); §5.2 'The matched mean contrast favors FP-GEM' (p.7); Conclusion (p.7); OpenReview abstract/TL;DR

### Tracer
G14 is only partly supported by the result artifacts on this server. The Sleep-EDF part of the headline matches. All three MI gaps behind "0.8–1.9 points higher than Joint-GEM" do not match. The claim that FP-GEM is best on B14 and Cho is false in the artifacts.

**What matches**
- Sleep FP−Joint (REVIEW_P0, EEGNet/H2 encoder, commit 278fc85e) is +1.849 pts, CI [+1.27, +2.45], FP wins in 63 of 75 participants. The paper's "1.9" is the difference of the rounded table cells (65.6 − 63.7); rounding 1.849 directly gives 1.8.
- In the Sleep code the fixed fitting prior is uniform, not πsrc.
- "0.1 below Source-only" on Sleep: the unrounded gap is 0.15.
- "Trails Recenter and SPDIM on Lee": holds in the artifacts.
- Every MI Source, EA, Recenter and SPDIM cell matches P12 or the Cho cache exactly.

**What does not match: the MI FP-GEM and Joint-GEM cells**
- Sources: TSMNet P12 per-subject CSV (sha 215d32b6, identical on origin/exp/h2cmi-wave0-mechanism df47753e and origin/agent/fp-gem-stage2 04a40e4e) and the Cho cache (commit 04a40e4e).
- FP−Joint in the artifacts is B14 +0.31, Cho −0.21 and Lee +0.28, against the paper's +1.3, +0.8 and +1.3.
- The paper's cells are the artifact values shifted up by exactly one or two points, with identical s.d.: FP B14 +2.0, FP Cho +1.0, FP Lee +1.0, Joint B14 +1.0.
- A regime re-run on 07-28 (job 913011) re-fit FP-GEM and Joint-GEM and reproduced the stored bAcc in all 345 units (max difference 0).
- I found no later FP/Joint run anywhere on the server. I checked git log on all refs after 04a40e4e (07-27) and cache files newer than 07-28.
- REVISION_PLAN_TSP_TPAMI.md L59–62 says the numbers come from a "later run" held off-server (submission_2026-07-28); that run is not here.
- Other MI runs do not give the paper's gaps either: REVIEW_P0 W1 (+1.13 / −0.07 / +0.34) and the W1-repaired H2CMI run (+1.13 / −0.03 / +0.48).
- The frozen story gate at df47753e sets `fp_gem_improves_over_joint_gem_natural_transfer_supported=false`.

**Theory and simulation claims**
- The O(1)→O(t⁴) and O(t⁶)/O(t³) claims are analytic (Theorem 6). No project code produces them, but my own quadrature check reproduces the stated orders.
- For the simulation claims (R²=0.998 from 2,038 fits; variance–bias crossover), no code or output exists on the server. Supplement F.1 says they ran on a Windows i7-9750H machine.

**Other points**
- Participant-level outputs and paired CIs already exist on the server, so "descriptive only" understates what is available. The paired MI results are not significant.
- The paper describes a matched protocol (diagonal Gaussian head, L-BFGS, density readout, 4-class B14, cross-session split). The code actually uses a Student-t head, Adam 20×3, the TSMNet classifier readout, 2-class B14 and a split of session 0.
- ~/.cache/h2cmi_training_caches/FP_GEM_RESULTS_SO_FAR.md contains errors: Cho gap given as −0.3 instead of −0.2; Sleep "−0.1" is really FP−Source; the SPDIM Sleep entry 63.6 is really Diag-IM.
- Scratch notes and scripts are in /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g14/.

### Adversarial re-check
I re-checked the 10 flagged rows of G14 (headline claims). Two things change and two stay the same.

(1) The simulation headlines, R² = 0.998 / 2,038 fits / 1.37% and the crossover cell 0.198 [0.126, 0.270], are REPRODUCIBLE. An independent re-implementation, written only from the paper's protocol and the seed scheme in supp L746-751, reproduces them exactly: 2,038 local fits, 40 boundary hits, R² 0.99831, median relative error 1.3685%, and all 12 Table S3 cells to printed precision. The scripts are in the scratchpad at agents/g14r/local_response_fig2a.py, agents/g14r/crossover_cell.py and agents/g06r_full17g.py. The status stays UNTRACEABLE only because the authors' code ran on a Windows laptop and is not on the server; the claims themselves are verified. Caveat: the pooled R² comes from the shift component b1; the scale component ℓ1 alone has R² −0.71.

(2) The Theorem 6 orders are confirmed by two independent numerical methods (quadrature of the mixture density, and mpmath on the paper's own Fisher blocks, agents/g14r/thm6_blocks.out). They are UNTRACEABLE only in the sense that no project code produces them. Note that K(t) ≈ (4/3)t⁶ holds only as t → 0: at t = 0.5 the leading term overstates K by about 65%.

(3) The MI FP-GEM vs Joint-GEM headline stays MISMATCH, and so do the "best on B14/Cho" statements. Paper Table 1 is identical, cell for cell (including every s.d.), to /home/infres/yinwang/.cache/h2cmi_training_caches/FP_GEM_RESULTS_SO_FAR.md L40-45 (2026-07-28 08:04, sha f29de28e), with four exceptions. Those are GEM cells, each shifted by an exact integer while its s.d. is unchanged: B14 FP 71.2→73.2, B14 Joint 70.9→71.9, Cho FP 59.0→60.0, Lee FP 66.6→67.6. The artifact FP−Joint gaps are Sleep +1.85, B14 +0.31, Lee +0.28 and Cho −0.21, not 0.8–1.9. No artifact reproduces the edited cells. I checked:
- alternative readouts and aggregations of the Stage-2 per-trial dumps (per seed, seed ensembles, adapt set, adapt plus eval, responsibilities);
- the regime α-path, oracle-best-α and max(FP, Joint);
- Cho per seed;
- a numeric co-occurrence scan of 34,120 text files, whose only hit is the revision plan quoting the paper;
- git grep across all 120 refs.

No FP-GEM output on the server is newer than the regime job 913011 (2026-07-28 09:12). ~/.claude/history.jsonl L190 (2026-07-28 17:09 CEST) shows the table being edited on the laptop, at C:/Users/15339/Downloads/FP-GEM_AAAI2027/theoryfirst/experiment_results_table.tex. The "later round" attributed in REVISION_PLAN_TSP_TPAMI.md L59-62 cannot be verified on the server and would have to come from the laptop. Additional mismatches in the same rows: B14 is 2-class in every artifact, but supp L1187 says 4-class. The Sleep contrast is EEGNet with a uniform π_fit, while the MI results are TSMNet with a Student-t density read out through the TSMNet classifier. Frozen gate df47753e: fp_gem_improves_over_joint_gem_natural_transfer_supported=false.

Notes: /tmp/claude-34987/-home-infres-yinwang-CMI-AAAI-FP-GEM/9e6cea85-38dc-4630-9dda-0026a94b325b/scratchpad/agents/g14r/G14R_notes.txt. No repo file was modified; all writes went to the scratchpad. One command, `pip download fpgem`, would have written into /home/infres/yinwang/CMI_AAAI/FP-GEM if the package had existed; it did not exist and the folder listing is unchanged.

