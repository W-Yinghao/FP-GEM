# W2 — Prior–geometry adaptation studies on the W1 models (FROZEN)

Status: FROZEN at the commit that adds this file. Owner go: 2026-09-28 ("都做吧": all four studies).
Inputs: the 657 frozen W1 units (`results/W1`, launch a97e9d6); no retraining. S1–S3 run on CPU from the
dumps; S4 re-runs inference on GPU (V100, QOS runfill). Numbers from the AAAI submission or any earlier
project run are not used, targeted or compared.

## 0. Common definitions

**Feature space and head (per unit).**
- EEGNet / Chambon: `z` = dumped pre-classifier feature; head = the unit's own final layer.
- TSMNet: `z = LogEig(rescale(M_ref^{-1/2} S M_ref^{-1/2}))` with the unit's classifier, where `(M_ref, v_ref)`
  are a reference Karcher mean/dispersion. *Source reference*: pooled Karcher mean/dispersion of all
  source-train `S`. This defines the TSMNet "identity" (no target statistics).

**Class-conditional model.** Diagonal Gaussians `N(μ_y, diag σ²_y)` fitted on source-train features (MLE,
variance floor 1e-4 × mean variance); source prior `π_src` = source-train class frequencies.

**Transform family.** Coordinatewise affine `T(z) = a ⊙ z + b`, `a > 0`, applied to target features before
the head.

**GEM estimators** (generalized EM on the unlabeled adaptation batch; exact per-coordinate M-step for
(a, b); identity start; stop at relative log-likelihood change < 1e-8 or 1000 iterations; iteration count and
convergence flag recorded):
- `FP` — prior fixed at `π_src` (κ = ∞).
- `Joint` — prior re-estimated each iteration (κ = 0).
- `K6` — Dirichlet MAP prior with pseudo-count 6·π_src (legacy constant, ablation only).
- `Kstar` — Dirichlet MAP with κ* = 1 / (Ī_{η|θ} · r²):
  - `Ī_{η|θ}` is the per-sample profile Fisher information for the prior logits given (a, b), computed on the
    source-validation features at the identity (average over the K−1 logit directions).
  - `r²` is the protocol uncertainty of the adaptation batch's class-logit vector:
    - MI (balanced cue schedule, no rejection in W1): `r² = 0`, so κ* = ∞ = FP. This is reported as such,
      not as an independent win.
    - Sleep (no quota): the between-source-subject variance of night stage-logits, averaged over logit
      directions.

**Baselines.**
- `Identity`.
- `Pooled`: per-coordinate mean/std matching of the target marginal to the source marginal.
- `Recenter` (TSMNet only): the adaptation session's own Karcher mean/dispersion, TSMNet's standard SFUDA.

**Protocol.**
- Primary is inductive: fit on the target adaptation session/night (all rows, label-free), apply to the
  evaluation session/night.
- Secondary is transductive: fit on the evaluation data itself.

**Readouts.**
- Primary: head argmax.
- Secondary: density argmax with uniform decision weights.

**Metric and statistics.**
- Metric: balanced accuracy on scored evaluation rows of the label set.
- Aggregation: average the 3 seeds within subject, then paired cluster bootstrap over subjects (10,000
  resamples, percentile 95% CI), per dataset × label set × backbone.
- Multiplicity: Holm over the primary contrasts within each study.

## S1 — Estimator family under natural shift (kickoff κ* / FP vs Joint)

**Primary contrasts:** FP − Joint, Kstar − FP, Kstar − Joint.
**Secondary contrasts:** FP − Identity, Pooled − Identity, Recenter − FP (TSMNet), K6 − FP.
**Also reported:**
- fitted prior movement ‖π̂ − π_src‖₁;
- transform size ‖log a‖, ‖b‖;
- iterations and convergence.

**Interpretation grid:**
- **FP − Joint CI > 0.** Fixing the fitting prior helps in that cell.
- **FP − Joint CI contains 0.** No evidence of a difference. Check whether Joint's π̂ moved: if it stayed near
  π_src, the two coincide by weak identification. This is reported as such, not as a win.
- **FP − Joint CI < 0.** Re-estimating the prior helps (expected where true proportions shift and are
  identifiable, e.g. Sleep K = 5).
- **Kstar.** It is only claimed "calibrated" if Kstar − FP ≥ 0 and Kstar − Joint ≥ 0 hold together in cells
  where r > 0 (Sleep). On MI, Kstar ≡ FP by construction.

## S2 — Multi-batch known proportions (kickoff A1)

**Setting.** Controlled geometry recovery on real features.
- For each unit's target adaptation session, inject a known latent affine shift (a₀, b₀).
- `log a₀` and `b₀` are drawn per coordinate from N(0, s²·v), where v is the between-source-subject variance
  of per-subject feature means (for b) and of log-SDs (for a), with s ∈ {0.5, 1}; 5 draws per unit.
- Split the adaptation rows into B = 4 batches of equal size by label-stratified sampling with a designed
  proportion matrix Π. The labels are used only to emulate a recording whose per-block cue schedule is
  known; this is disclosed as the protocol-information condition under study.
- Proportion designs:
  - `balanced`: every batch has the pooled proportions; Π has rank 1.
  - `random`: Dirichlet(1) rows rescaled so the pooled proportions are unchanged.
  - `blocked`: each batch dominated by one class (0.7 / rest shared), pooled proportions unchanged.
- The pooled sample is identical in total size and proportions across designs.

**Estimators** (geometry shared across batches):
- Pooled and FP on the union.
- `MB-known`: per-batch priors fixed at Π's rows.
- `MB-unknown`: per-batch priors re-estimated.
- `MB-interval`: per-batch priors constrained to ±0.1 around Π's rows (projected M-step).

**Endpoints.**
- Primary: normalized geometry error E = ‖(log â − log a₀, b̂ − b₀)‖ / ‖(log a₀, b₀)‖, with MB-known vs
  FP-union contrasted per design.
- Secondary: evaluation bAcc when the same (a₀, b₀) is applied to the evaluation session and undone with the
  estimate. Also reported against σ_min(Π).

**Interpretation grid:**
- MB-known beats FP-union only under non-degenerate Π (`random`/`blocked`) and not under `balanced`: batch
  composition carries geometry information.
- No gain under any design: multi-batch structure does not help at these n.
- MB-unknown ≈ MB-known: the known proportions are not what matters.

## S3 — Detecting fixed-prior mismatch (kickoff B1)

**Test.** After the FP fit on the adaptation batch, estimate target proportions with the geometry held fixed
(EM on π only). Test H0: π_target = π_src with the likelihood-ratio statistic, calibrated by a parametric
bootstrap (500 resamples) from the fitted FP model; α = 0.05.

**Cells:**
- MI, where H0 holds by design because the W1 adaptation sessions are exactly balanced: this gives the size.
- MI resampled: label-stratified resampling of the adaptation session to minority fraction q ∈ {0.3, 0.2}
  (and 4-class analogues), which gives power under a known prior shift.
- Sleep natural nights: descriptive power, with the TV distance of true vs source proportions reported
  alongside.
- **Secondary:** the prior-invariant moment test of v5 B1. The source class-mean differences are projected
  out, W ⊥ span{μ_y − μ_K}. Test that the projected target mean equals W μ_K by Hotelling T² with source
  covariance; it is sensitive to geometry, not prior.

**Endpoints:** rejection rate (size, power) with Wilson 95% CIs.

**Interpretation grid:**
- Size ≤ 0.075 and power ≥ 0.5 at q = 0.2: a usable diagnostic.
- Size inflated: miscalibrated, not usable.
- Power low while size is fine: prior mismatch undetectable at these separations (weak identification).

## S4 — Where is the shared acquisition change shared? (kickoff C1; GPU)

**Injections.** Known signal-level changes on the target's cached signals (both sessions):
- per-channel gains, log g_c ~ N(0, 0.3²);
- re-referencing to the mean of 3 random channels;
- channel mixing (I + ε E, ε = 0.1, E Gaussian with unit-norm rows).
There are 3 draws each per unit. MI covers B14-c2/c4 and Lee with TSMNet and EEGNet; Sleep uses Chambon
with gain and re-reference only.

**Readout 1: class-dependence of the latent response.**
- Δz_i = z(injected x_i) − z(x_i).
- Statistic: F = between-class / within-class dispersion of Δz, with a permutation p-value (label shuffle,
  1,000 permutations).
- Also reported: the relative norm of the class-mean differences of Δz.

**Readout 2: recovery.** Evaluation bAcc under injection for:
- Identity, Pooled, FP, Joint;
- Recenter (TSMNet);
- EA at signal level, i.e. whitening by the adaptation-session mean covariance followed by re-colouring to
  the source mean covariance, computed on the injected signals.

Recovery ratio = (bAcc_method − bAcc_injected-identity) / (bAcc_clean-identity − bAcc_injected-identity).

**Interpretation grid:**
- Readout 1 significant for TSMNet and EEGNet under gains/re-reference while signal-level EA recovers:
  a physically shared change becomes class-dependent in latent space, supporting v5 C1.
- Readout 1 not significant: the change stays shared, and latent GEM's failures must have other causes.

## Forbidden

- Using target labels in any estimator. The label-built batch/resampling constructions in S2/S3 are
  protocol emulations, labelled as such.
- Changing definitions after seeing any aggregate. The probe may lead to an appendum, frozen before
  aggregates are viewed.
- Tuning κ, iterations or floors on target data.
- Comparing to AAAI or earlier numbers.
