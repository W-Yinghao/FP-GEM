# W2 Appendum A2 — S2/S3 operational definitions (committed before S2/S3 run)

Date: 2026-09-28. No S2/S3 output exists yet. S1 is running under A1.

## S2

1. **Ground-truth geometry.** The target subject already carries its own natural shift, so the injected
   (a₀, b₀) alone is not the transform that maps the batch to the source model. Ground truth is defined as
   T* = T_orc ∘ T₀⁻¹.
   - T_orc: the labelled (oracle) coordinatewise affine fit on the un-injected adaptation batch, i.e. the
     maximiser of Σ_i log N(T z_i; μ_{y_i}, σ²_{y_i}) + n Σ log a with the same |log a| ≤ 2 bound.
   - T₀: the injected shift.
   - This gives a* = a_orc ⊙ a₀ and b* = a_orc ⊙ b₀ + b_orc.
   - Labels enter only this evaluation target, never an estimator.
   - E = ‖(log â − log a*, b̂ − b*)‖ / ‖(log a₀, b₀)‖.
2. **Scope: MI only** (B14-c2, B14-c4, Lee-c2), where the pooled adaptation proportions are uniform and all
   trials of the session are used. Sleep is excluded: its natural proportions are non-uniform with rare
   classes, so the three designs cannot hold the pooled sample fixed.
3. **Designs** (B = 4 batches, equal size, whose union is the whole adaptation session):
   - `balanced`: every row uniform.
   - `blocked`:
     - K = 2: rows (0.85, 0.15), (0.15, 0.85), repeated.
     - K = 4: row k = 0.7 on class k and 0.1 on each other class.
   - `random`: one Dirichlet(1) row r plus its cyclic permutations (K = 4), or r and its reverse twice
     (K = 2), so the batch mean stays uniform.
   - Per-batch counts are rounded; the remainders go to the largest fractional parts under the class totals.
4. **Draws.** s ∈ {0.5, 1} × 5 draws per unit, seeded by (unit seed, target, draw, s). The same draws are
   used for every design and estimator, so contrasts are paired.

## S3

1. **Resampled prior shift.** "Minority fraction q" means class 0's odds are multiplied by q/(1−q) through
   down-sampling class 0 (5 draws per q). For K = 2, class 0's share is then exactly q. For K = 4, class 0's
   share is q/(q + 3(1−q)).
2. **Parametric bootstrap.** Each resample draws n features from the fitted FP model under H0 in its
   transformed space, maps them back with the fitted transform, and re-runs the full procedure (FP fit, then
   prior-only EM, then the LR statistic). This propagates geometry-fitting uncertainty into the null.
3. **Secondary moment test.** Covariance: Ledoit–Wolf shrinkage of the pooled within-class source-train
   covariance in the W-projected space. Reference: χ² with rank(W) degrees of freedom. Reported as
   pre-registered; its calibration is itself an S3 outcome.
EOF
cd /home/infres/yinwang/CMI_AAAI/FP-GEM && git add prereg/W2_APPENDUM_A2_S2S3_definitions.md && git commit -q -m "W2 appendum A2: S2 ground truth + MI scope + designs; S3 resampling and bootstrap definitions

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q origin main && git log --oneline -1