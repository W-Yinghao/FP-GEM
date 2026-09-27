# FP-GEM paper: extraction, reviews, and paper-to-artifact spot-checks

**Paper.** "When Priors Push Geometry: Fixed-Prior Geometry EM for EEG Test-Time Adaptation". AAAI-27 submission #26843, forum `BmRiAtL7yI`. Authors: Yinghao WANG, Ziyu Jia (France, China). Primary topic: HAI Emotional Intelligence & Brain-Sensing. Secondary topic: ML Transfer, Domain Adaptation & Continual Learning.

- The submission included a technical supplement (9 pp.) and a "Code and Data Supplement" zip. The zip is not in `/home/infres/yinwang/CMI_AAAI/FP-GEM`.
- **Decision: Reject (24 Sep 2026).** The paper did not advance to Phase 2.
- Sources:
  - Main PDF (9 pp.): `/home/infres/yinwang/CMI_AAAI/FP-GEM/26843_When_Priors_Push_Geometr (2).pdf`
  - Supplement: `.../26843_When_Priors_Push_Geometr_Technical Supplement.pdf`
- I rendered page 7 (Table 1 and Fig. 2) and supplement page 7 (Tables S2–S4) to images and confirmed the text extraction digit for digit.

## 1. Method

**Three class-weight roles** (Section 3.1):

| Symbol | Name | Role |
|---|---|---|
| ρT | true target proportions | generates the batch |
| πfit | fitting prior | used to estimate geometry |
| πdec | decision weights | used for prediction |

**Model.**
- Transform family: positive-diagonal affine, T_{ℓ,b}(u) = diag(e^ℓ)u + b (Eq. 3). Identity is ℓ = b = 0.
- Target density: q_{θ,y}(u) = J_θ(u)·p_y(T_θ u) (Eq. 1).
- Mixture: m_{θ,π} = Σ_y π_y q_{θ,y} (Eq. 2).

**Estimators (Eqs. 8–11).**
- Objective: L̂_A(θ, πfit) = (1/nA) Σ_i log m(u_i) − λR(θ).
- E-step (Eq. 9): standard responsibilities.
- Generalized-EM geometry M-step (Eq. 10): argmax over θ of Σ r log q − λR.
- The only difference is the prior M-step (Eq. 11):
  - **Joint-GEM:** π_fit^{(j+1)} = mean of the responsibilities.
  - **FP-GEM:** π_fit^{(j+1)} = π_src.

**Algorithm 1.** Initialize θ(0) = 0 with πfit = πsrc, then iterate until the declared stopping rule is met.

**Prediction (Eq. 12).** ŷ = argmax_y πdec,y · q_{θ̂,y}(u) with **πdec = Unif** (justified by Lemma S9).

**Deployment setting.** Source-data-free: only the frozen representation map, the stored class-conditional densities and πsrc are available at target time.

## 2. Theory (main-text numbers ↔ supplement)

**Stabilizer (Section 3.1, Theorem S2, Corollary S3).**
- G_src = {S : S#P_y = P_y ∀y}.
- T and T0 induce the same class-conditional laws iff T∘T0⁻¹ ∈ G_src.
- For positive-diagonal affine maps, G_src is trivial when one class has a finite mean and a finite, nonzero variance.

**Theorem 1 / S4 (exact ambiguity).**
- Setup: g = J_T f(T·) and r = g/f, with r_low ≤ r ≤ r_high. Choose β < α with β/α ≤ r_low and r_high ≤ (1−β)/(1−α).
- Construction: p1 = [(1−β)f − (1−α)g]/(α−β) and p2 = [αg − βf]/(α−β).
- The two worlds produce the same unlabeled density g:
  - W_P: T0 = Id, ρT = (β, 1−β).
  - W_G: T0 = T, ρT = (α, 1−α).
- **Witness (Corollary S5):**
  - Student-t3 density f(u) = (2/(π√3))(1 + u²/3)⁻², with T(u) = 1.1u (d = 11/10).
  - g/f ∈ [(1.1)⁻³, 1.1] in the main text; the supplement writes (d⁻³, d].
  - α = 3/5, β = 2/5. Checks: 2/3 ≤ (10/11)³ and 11/10 ≤ 3/2.
  - p1 = 3f − 2g ≤ 3f and p2 = 3g − 2f ≤ 3g.
  - Var_f = 3, Var_g = 3/d², Var p1 = 489/121, Var p2 = 174/121.

**Proposition 2 / Corollary S6 (no target-only resolution).**
- Any selector based only on the target sample has regret ≥ γ/2 for every n.
- The general minimax regret is g0·g1/(g0 + g1).

**Proposition 3 / S7 (local fitting-prior response).**
- ∂θ̂/∂η = −H_θθ⁻¹ · E[r(1−r)(s1 − s2)].
- Multiclass form: ∂θ̂/∂η_k = −H_θθ⁻¹ · E[r_k(s_k − s̄)].

**Proposition 4 / S8 (profile information).**
- I_θ|η = I_θθ − I_θη I_ηη⁻¹ I_ηθ, and I_θ|η⁻¹ ⪰ I_θθ⁻¹.
- The supplement restricts this to the unpenalized MLE (or penalties whose derivatives vanish).

**Proposition 5 / S13 (responsibility-error bias).**
- B_r = E Σ_y (r_y − τ_y) s_y.
- ‖θ†_r − θ0‖ ≤ ‖B_r‖/κ ≤ (1/κ)·E[S(U)‖r − τ‖₁], where κ is the strong-concavity constant.

**Theorem 6 / S15 (Gaussian weak identification).** Model: X|Y ~ N(yt, 1); m_{a,η} is the two-component mixture with π_η = (1 + e^{−η})⁻¹.
- Information:
  - I_aa = 1 − t²S(t) = 1 − t² + O(t⁴).
  - I_a|η = 1 − t²S/(1 − S) = (2/3)t⁴ − 2t⁶ + O(t⁸).
- Blocks: I_aη = −(1/2)tS and I_ηη = (1/4)(1 − S).
- Scores: s_a = −z + tH(z) and s_η = H/2, with H = tanh(tz).
- Local coefficients, with η_δ = log[(1+2δ)/(1−2δ)] and a⋆ = A(t)δ:
  - KL(P_{0,η_δ} ‖ P_{a⋆,0}) = K(t)δ².
  - BER cost = B(t)δ².
- Closed forms:
  - A(t) = −2tS/(1 − t²S)
  - K(t) = 2[1 − (1+t²)S]/(1 − t²S)
  - B(t) = 2t³φ(t)S²/(1 − t²S)²
- Small-t expansions: A = −2t + O(t⁷), K = (4/3)t⁶ + O(t⁸), B = 2t³φ(t) + O(t⁹).
- Series used:
  - S(t) = 1 − t² + t⁴ − (5/3)t⁶ + (13/3)t⁸ + O(t¹⁰)
  - sech²x = 1 − x² + (2/3)x⁴ − (17/45)x⁶ + (62/315)x⁸
  - Moments: EW² = t² + t⁴; EW⁴ = 3t⁴ + 6t⁶ + t⁸; EW⁶ = 15t⁶ + 45t⁸; EW⁸ = 105t⁸
  - S/(1 − t²S) = 1 − (2/3)t⁶
- Iterated limits: −2, 4/3, and 2φ(0).
- Pinsker: TV ≤ √((n/2)·K(t)δ²). Evidence scales as nδ²t⁶; cost scales as δ²t³.
- **I re-derived the leading orders of I_a|η, K, A and B by hand and they check.**

**Other supplement results.**
- Theorem S11: pooled-moment alignment bias. A_pool = D·diag(σ(π∗)/σ(ρT)).
- Theorem S12: the oracle class-conditional objective is invariant to class proportions.
- Theorem S14: one-shot fixed-prior bias.
  - b† = (2ρ − 1)µ(κ(t) − 1), with κ(t) = E_{N(µ,σ²)} tanh(µX/σ²) ∈ (0, 1).
  - |b_fixed| / |b_pool| = 1 − κ(t).
- Lemma S9 (uniform decision weights maximize balanced accuracy) and Corollary S10 (a correct transform transfers the balanced Bayes rule).

## 3. Controlled Gaussian study (Section 5.1, Figure 2, Supplement F, Tables S1–S4)

**Design.**
- Z|Y ~ N(y·t·e1, I4), πsrc = (1/2, 1/2), U = T_{θ0}⁻¹(Z).
- True parameters: ℓ0 = (log 1.25, log 0.8, 0, 0) and b0 = (0.5, −0.25, 0, 0).
- Joint-GEM estimates the positive-class weight; FP-GEM fixes it at 1/2.
- Direct observed-likelihood maximization: analytic gradients, deterministic multistart, **λ = 0**.
- Each cell has 200 paired batches.
- Metric: MSE_θ = ‖ℓ̂ − ℓ0‖² + ‖b̂ − b0‖².
- Contrasts: Δθ = E[MSE_FP − MSE_Joint] (negative favors FP-GEM) and ΔBA (positive favors FP-GEM), with paired Student-t intervals.

**Grids.**

| Grid | t | nA | ρT,+ | Batches |
|---|---|---|---|---|
| Source-matched | {0.35, 0.50, 0.75, 1.50} | {100, 200, 500, 1000, 2000} | 0.50 | 20 cells × 200 = 4,000 |
| Mismatch | {0.35, 0.50, 0.75, 1.50} | 500 | {0.50, 0.70, 0.92} | 12 cells × 200 |

**Optimizer and numerical protocol (Table S1).**
- Local-response fits: η ∈ {−0.1, 0, +0.1}, compared with d_η = −H_θθ⁻¹ G_θη.
- Optimizer: L-BFGS-B, ≤2,000 iterations, ≤50 line-search steps, ftol 1e−13, pgtol 1e−7.
- Bounds: a1 ∈ [−4, 4], b1 ∈ [−8, 8], η ∈ [−10, 10]. A value within 1e−7 of a bound counts as a boundary hit. Coordinates 2–4 are solved in closed form.
- Multistart:
  - Fixed-logit fits: identity and moment-matching starts.
  - Joint-GEM: moment-matching starts at η ∈ {−8, −4, −1, 0, 1, 4, 8}, plus an FP warm start at η = 0 and the identity at η = 0.
  - Selection: best objective among starts with projected-gradient ∞-norm ≤ 1e−7.
- Strict generalized EM: ≤10,000 iterations; convergence needs 3 successive iterations with movement < 1e−8 and relative objective change < 1e−10.

**Seeds, checks and environment.**
- Master seed 20270728. Each batch's seed is the first 8 bytes (little-endian) of SHA256("20270728|nA|t|ρT,+|s"), fed to NumPy `default_rng`. The strict-EM verification uses base seed 930000 with 200 replicates per cell.
- Finite-difference check: step 1e−6 on a batch with t = 0.75, nA = 173, seed 913731. Maximum errors: 2.0e−10 (gradients), 1.4e−10 (Hessian), 6.5e−11 (cross-derivative).
- A pseudoinverse (cutoff 1e−12) is used only if the condition number exceeds 1e12.
- **Environment: a Windows host, i7-9750H (6/12 cores, 31.7 GiB), Python 3.8.8, NumPy 1.22.2, SciPy 1.10.1.** 8 workers; the 4,000-batch run took 195.6 s; strict EM took 890.3 s with 6 workers.

**Figure 2A: local response.**
- Centered refits match the derivative in all 4,000 fits: minimum cosine 0.9999999, median relative error 0.080%, maximum 0.357%.
- The FP-GEM Hessian is negative definite in all 4,000 fits.
- On the 2,038 fits with |η̂_Joint| ≤ 0.4, the prediction (∂θ̂/∂η)·η̂_Joint explains the Joint-minus-FP displacement with **R² = 0.998** (99.83%) and median vector relative error **1.37%**.

**Figure 2B and Table S2: transform MSE at matched proportions.** Values are FP / Joint, with 95% intervals.

| nA | t = 0.50 FP | t = 0.50 Joint | t = 1.50 FP | t = 1.50 Joint |
|---|---|---|---|---|
| 100 | .06805 [.06319, .07290] | .13462 [.12281, .14643] | .06879 [.06309, .07450] | .15054 [.08564, .21545] |
| 200 | .03183 [.02938, .03427] | .09445 [.08433, .10456] | .03617 [.03311, .03924] | .04736 [.02838, .06634] |
| 500 | .01276 [.01168, .01384] | .07992 [.06887, .09098] | .01379 [.01252, .01506] | .01496 [.01323, .01669] |
| 1000 | .00686 [.00626, .00745] | .06429 [.05371, .07488] | .00673 [.00624, .00722] | .00706 [.00656, .00757] |
| 2000 | .00316 [.00291, .00341] | .06759 [.05483, .08035] | .00321 [.00296, .00346] | .00347 [.00319, .00375] |

- Fitted Joint-logit SD: 1.48 (nA = 100) → 2.21 (nA = 2000) at t = 0.5; 1.65 → 0.050 at t = 1.5.
- Main-text restatement: FP 0.0680 → 0.00316; Joint 0.1346 → 0.0676; both ≈0.003 at t = 1.5.
- The t = 1.5 curve in Fig. 2B starts at nA = 500 because the nA = 100 and 200 cells are boundary-sensitive.
- Approximate values read from the plot:
  - t = 0.35: about −0.033 to −0.039, flat.
  - t = 0.75: about −0.125, −0.117, −0.072, −0.064, −0.032 across nA.

**Figure 2C and Table S3: paired FP − Joint at nA = 500.**

| t | ρT,+ | ΔMSE_θ [95% CI] | ΔBA, pp [95% CI] |
|---|---|---|---|
| .35 | .50 | −.0332 [−.0378, −.0286] | +.221 [.192, .251] |
| .50 | .50 | −.0672 [−.0780, −.0564] | +.632 [.529, .735] |
| .75 | .50 | −.0719 [−.0942, −.0496] | +.945 [.651, 1.239] |
| 1.50 | .50 | −.0012 [−.0021, −.0002] | +.011 [.002, .020] |
| .35 | .70 | −.0252 [−.0335, −.0168] | +.156 [.104, .208] |
| .50 | .70 | −.0274 [−.0429, −.0118] | +.235 [.107, .362] |
| .75 | .70 | +.0089 [−.0201, .0379] | −.025 [−.331, .280] |
| 1.50 | .70 | +.0512 [.0467, .0558] | −.513 [−.557, −.468] |
| .35 | .92 | −.0258 [−.0431, −.0085] | +.126 [.022, .231] |
| .50 | .92 | +.0108 [−.0214, .0430] | −.181 [−.421, .060] |
| .75 | .92 | +.1980 [.1261, .2699] | −1.944 [−2.541, −1.346] |
| 1.50 | .92 | +1.1287 [1.0784, 1.1790] | −7.548 [−7.793, −7.303] |

- Main text restates −0.0672, +0.632, −0.00117 (t = 1.5) and 0.198 at (0.92, 0.75).
- The ρ = 0.50 rows agree with the Table S2 differences at nA = 500 (for example 0.01276 − 0.07992 = −0.0672).

**Optimizer checks (Section 5.1, F.2).**
- All 4,000 fits pass the projected-gradient check (1e−7) and the finite-difference check (2.0e−10).
- **40 Joint-GEM fits (1.0%) hit |η| = 10**, i.e. a mixture weight within 4.6e−5 of the simplex boundary. Excluding them keeps FP-GEM ahead in every cell with t ≤ 0.75.
- The mean at t = 1.5, nA = 100 is boundary-sensitive.

**Table S4: identity-started strict EM at ρ = 0.5, nA = 500.**
- FP-GEM converges in all 2,400 runs. Direct and EM solutions agree to about 1e−8. The objective is nondecreasing on every trajectory.

| t | Joint converged | Joint mean iterations | ΔMSE [95% CI] | ΔBA, pp [95% CI] |
|---|---|---|---|---|
| .35 | 167/200 | 6074.3 | −.0315 [−.0357, −.0273] | +.215 [.187, .243] |
| .50 | 198/200 | 2216.9 | −.0550 [−.0652, −.0448] | +.499 [.410, .588] |
| .75 | 200/200 | 596.2 | −.0406 [−.0550, −.0262] | +.511 [.328, .695] |
| 1.50 | 200/200 | 41.1 | −.0011 [−.0016, −.0006] | +.011 [.006, .016] |

- Joint-GEM convergence rates for t = (.35, .5, .75, 1.5): (83.0, 96.5, 100, 100)% at ρ = 0.70 and (77.0, 98.0, 100, 100)% at ρ = 0.92.

## 4. EEG experiments (Section 5.2, Supplement H)

**Datasets.**

| Dataset | Participants | Task | Backbone |
|---|---|---|---|
| Sleep-EDF | 75 | 5 stages: W, N1, N2, N3 (stages 3+4 merged), REM; movement and unscored epochs dropped | EEGNet |
| BNCI2014-001 ("B14") | 9 | **4 MI classes, retained** | TSMNet with domain-specific SPD BN (SPDDSBN) |
| Cho2017 | 52 | left vs right hand | TSMNet with SPDDSBN |
| Lee2019-MI | 54 | left vs right hand | TSMNet with SPDDSBN |

**Preprocessing.**
- Sleep: Fpz–Cz and Pz–Oz, 0.3–35 Hz, 100 Hz, 30-s epochs (3,000 samples).
- MI: all task EEG channels, 4–38 Hz, 250 Hz, 0.5–3.5 s after the cue.
- Channel normalization is fitted on source-train only, then frozen.

**Protocol.**
- Outer leave-one-subject-out. Source participants are split 80/20 train/validation by participant identity.
- Sleep: the earlier night is the adaptation set A, the later night is the evaluation set E.
- MI: an earlier session adapts and a later session evaluates; single-session data use a fixed chronological run split.
- Label firewall: labels are revealed only after predictions are written. One-pass evaluation.
- Seeds 0, 1, 2 share folds and checkpoints. Sleep has 225 participant–seed predictions per method.
- Aggregation: sessions/runs are averaged within participant and seed, then seeds within participant. Participants are the reporting units. MI cells report mean (s.d.); Sleep reports means only.

**Hyperparameters.**
- Encoders: Adam, lr 1e−3, weight decay 1e−4, batch 64, ≤100 epochs, patience 15 on source-validation balanced accuracy.
- Density head: class-wise **diagonal Gaussian** with variance floor 1e−4 and empirical πsrc. It sits on the EEGNet latent for Sleep and the TSMNet pre-head tangent vector for MI.
- GEM (both variants):
  - identity-centered penalty 1e−3
  - **L-BFGS** geometry step
  - log-scales in [−2, 2]
  - ≤100 generalized-EM iterations
  - stop after 5 consecutive relative objective changes < 1e−6
- Joint-GEM floors weights at 1e−4, then renormalizes.
- On MI the affine map acts after Recenter, in tangent coordinates.
- Information-maximization baselines: 50 target epochs, hyperparameters fixed on source validation.

**Baselines, with the names used in the paper.**
- **Source** ("Source-only"): the frozen checkpoint, no adaptation.
- **EA** (Euclidean alignment, He & Wu 2020): uses a stored source Euclidean reference.
- **Recenter** (MI only): re-fits the target SPD BN statistics. It is the common base for SPDIM and both GEM variants.
- **SPDIM** (Li, Kawanabe & Kobler 2025; MI only).
- **Diag-IM** (Sleep only): a diagonal latent-space information-maximization analogue.
- **Joint-GEM** and **FP-GEM** share the readout: the Gaussian head with uniform decision weights.
- Only the FP-GEM vs Joint-GEM comparison is readout-matched.

**Table 1: balanced accuracy (%).** Bold marks the best displayed mean in a column; underline in the paper marks the second best.

| Method | Sleep | B14 | Cho | Lee |
|---|---|---|---|---|
| Source | **65.7** | 61.0 (10.8) | 52.3 (3.1) | 54.9 (4.9) |
| EA | 65.3 | 60.1 (11.3) | 52.2 (2.9) | 54.4 (4.3) |
| Recenter | — | 72.7 (12.8), 2nd | 59.8 (7.6) | **68.2 (10.0)** |
| SPDIM | — | 72.7 (12.9), 2nd | 59.7 (7.6) | 67.7 (9.8), 2nd |
| Diag-IM | 63.6 | — | — | — |
| Joint-GEM | 63.7 | 71.9 (11.3) | 59.2 (7.1) | 66.3 (9.2) |
| FP-GEM | 65.6, 2nd | **73.2 (11.5)** | **60.0 (7.1)** | 67.6 (9.3) |

- Stated FP − Joint gaps: **+1.9 (Sleep), +1.3 (B14), +0.8 (Cho), +1.3 (Lee)**. These give the "0.8–1.9 points" headline.
- Other stated claims: FP-GEM is best on B14 and Cho; it is 0.1 below Source on Sleep; it trails Recenter and SPDIM on Lee.
- The paper also calls these "descriptive aggregate contrasts" and says participant-level outputs would be needed for paired uncertainty.

## 5. OpenReview (Reject; Phase 1)

**yczf — rating 5 (marginally below), confidence 4.**
- Evidence is weak: Table 1 gives means only, Sleep has no s.d., and there are no paired CIs, per-subject win counts, tests or bootstrap for a 0.8–1.9 point gain.
- The protocol-supported-proportion assumption is not validated on real data, and Sleep proportions vary.
- FP-GEM does not dominate: it trails Recenter/SPDIM on Lee and is below Source on Sleep.
- Questions asked:
  - Paired CIs or tests per dataset.
  - Empirical target proportions once labels are revealed, and whether gains track source–target proportion similarity.
  - Sensitivity to a slightly wrong prior.
  - Is FP-GEM a controlled correction to Joint-GEM, or a competitive full pipeline?

**hTrM — rating 5, confidence 5.**
- The method is narrow: it assumes target ≈ source proportions, and the advantage reverses under mismatch.
- The setup is simplified: a frozen encoder with diagonal Gaussian heads.
- The comparison is uneven: baselines use different pipelines and readouts.
- Questions asked:
  - How to use FP-GEM when proportions are unknown or different.
  - How to detect when the fixed-prior assumption fails.
  - Why prefer it over label-shift or mixed-shift TTA methods.
  - How much of the gain comes from fixing the prior versus the affine Gaussian setup.
  - Whether the effect carries over to a nonlinear adapter.

**AI Reviewer — no score.**
- No matched no-GEM baseline: FP-GEM vs Source is 65.6 vs 65.7 on Sleep; vs Recenter it is 73.2/72.7, 60.0/59.8 and 67.6/68.2, so the net value of GEM geometry is not established.
- No paired participant-level uncertainty.
- No mechanism diagnostics: proportion mismatch, Joint prior displacement, responsibility uncertainty, geometry displacement, or their link to gains.
- Missing baselines: CMMN (Gnassounou et al. 2023) for Sleep and BTTA-DG (Luo et al. 2026) for MI.
- The longitudinal adapt/evaluate split adds temporal drift that the estimator analysis does not cover.
- Suggestions: a decision criterion for uncertain protocol knowledge; a multiclass weak-identification analysis; a roadmap for Section 3.
- Minor points:
  - Proposition 4 needs λ = 0 or λn → 0.
  - Eq. 10 writes argmax although the method is generalized EM.
  - Define the D·η̂_Joint term in Fig. 2A.
  - Reword "should not" as "should not trigger a geometry correction".
  - Cite RAINCOAT and RLSbench.

## 6. Paper vs artifact spot-checks

These go beyond the extraction task. They are read-only checks meant to steer the code-mapping step, not final conclusions.

**1. Table 1 non-GEM cells match artifacts exactly, means and s.d.**
- **P12 TSMNet (B14 and Lee).** Recenter = `rct`, SPDIM = **`spdim_geodesic`** (not `spdim_bias`), Source = `source_only_tsmnet`.
  - Per-subject file: `/home/infres/yinwang/CMI_AAAI/H2CMI/.codex_p12_launch_5b71ee8/h2cmi/results/fp_gem_main/fp_gem_per_subject.csv`.
  - Committed at 3bba1d0b on origin/exp/h2cmi-wave0-mechanism. Result CSV sha256 f3e4ca69….
- **Cho.** 156 unit JSONs at `/home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_cho/cho_target*_seed*.json`, runner `h2cmi/run_fp_gem_cho.py` (4be89b0d / 1b89a32d / 04a40e4e).
- **EA.** `/home/infres/yinwang/.cache/h2cmi_training_caches/fp_gem_ea/ea_*.json` (runner `run_ea_b14_lee.py` @ ab03bd7a): B14 60.13 (11.31), Lee 54.37 (4.31).
- **Sleep.** Matches REVIEW_P0 W2 primary on origin/exp/h2cmi-review-p0-corrections (tip 5bc9bf07), `h2cmi/results/REVIEW_P0_RESULTS.md` lines 66–92:

| Paper row | REVIEW_P0 key | Value |
|---|---|---|
| Source | `identity_uniform` | 0.657 |
| EA | `source_recolored_ea` | 0.653 |
| Diag-IM | `latent_im_diag_uniform` | 0.636 |
| Joint-GEM | `joint_geometry_uniform` | 0.637 |
| FP-GEM | `fixed_iterative_geometry_uniform` | 0.656 |

- The Sleep FP − Joint gap is +0.0185 [+0.0127, +0.0245].

**2. Four MI GEM cells do not match any artifact I found.** Artifact means (s.d.) vs the paper:

| Cell | Artifact | Paper | Difference |
|---|---|---|---|
| B14 Joint-GEM | 70.94 (11.34) | 71.9 | +1.0 |
| B14 FP-GEM | 71.24 (11.48) | 73.2 | +2.0 |
| Cho FP-GEM | 58.98 (7.14) | 60.0 | +1.0 |
| Lee FP-GEM | 66.56 (9.35) | 67.6 | +1.0 |

- **The s.d. values match to one decimal while the means are offset by whole points.** Cho Joint 59.19 and Lee Joint 66.27 do match.
- On the artifacts, FP − Joint is **B14 +0.30 [+0.05, +0.51], Cho −0.21, Lee +0.28 [−0.09, +0.67]**, and the P12 subject-weighted gap is +0.29 [−0.03, +0.62] (inconclusive).
- Using the artifact values also flips "FP-GEM is best on B14 and Cho": FP − Recenter is −1.49 on B14 and −0.77 on Cho.
- The July-28 consolidated table in `/home/infres/yinwang/.cache/h2cmi_training_caches/FP_GEM_RESULTS_SO_FAR.md` has FP 71.2 / 59.0 / 66.6 and Joint 70.9 / 59.2 / 66.3.
- The regime re-derivation in `.../regime_analysis_20260728T064406/out/regime_analysis_dataset_summary.csv` gives Δ = +0.0031, −0.0021, +0.0028.
- `/home/infres/yinwang/CMI_AAAI/FP-GEM/REVISION_PLAN_TSP_TPAMI.md` (around lines 50–62) says the FP/Joint numbers came from "a later run" whose subject-level outputs are not local. No such run was found on this server.

**3. Implementation mismatches between code and the paper's description.** Code checked: P12 config (`fp_gem_config.json` geometry_em and source_density), `h2cmi/tta/class_conditional.py` lines 230–246 at origin/agent/fp-gem-stage2, and `h2cmi/config.py` TTAConfig lines 98–113 at review-p0.

| Aspect | Code | Paper |
|---|---|---|
| Density | Student-t, df = 8, low-rank-4 + diagonal | diagonal Gaussian |
| Optimizer | Adam, lr 0.05, 20 outer iterations × 3 steps, fixed | L-BFGS, ≤100 iterations, 5×1e−6 stopping rule |
| Penalty | log-det weight 1 and trust regions of 1 | 1e−3 identity-centered penalty |
| Joint prior M-step | **Dirichlet anchor (dirichlet 5 + prior_anchor_strength 1 = κ 6 pseudo-counts)·πsrc** | plain mean of responsibilities with a 1e−4 floor |
| MI readout | frozen TSMNet `Linear(210, 2)` | Gaussian head with uniform decision weights |
| MI split | `class_stratified_half` within a session (B14 72/72 [36, 36]; Lee 50/50; Cho 100/100) | earlier → later session; chronological run split |
| B14 classes | 2 | 4 |

- `REVISION_PLAN_v4_positive_claims.md` line 21 confirms κ = 6 in the published code.

**4. Sleep omits stronger operators that exist in REVIEW_P0.** `fixed_reference_oneshot` scores 0.695 and `pooled` scores 0.660, both above FP-GEM's 0.656.

**5. The controlled-simulation code is not on this server.** Searching all 121 refs for seeds 20270728, 913731 and 930000 found nothing relevant. The revision plan lists local folders `convergence_sim/`, `mechanism_sim/`, `multiclass_sim/`, `optimal_sim/`, `version_b_optimal/` and an `fpgem` package on the Windows host.

**6. Minor notation inconsistencies in the paper.**
- Table S1 calls the log-scale "a", while Theorem 6 uses "a" for translation.
- The main text gives the ratio range as [(1.1)⁻³, 1.1]; the supplement gives (d⁻³, d].
- The main text says Algorithm 1 is identity-initialized, but the simulation uses multistart.