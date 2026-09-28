# W2 Appendum A1 — scale bounds (committed before the W2 fleet)

Date: 2026-09-28. Applies to S1–S4.

**Change.** The affine scale is bounded, |log a_d| ≤ 2, for every GEM estimator and for Pooled. In the GEM
M-step the per-coordinate closed-form maximiser is clipped to [e^-2, e^2] and b is re-solved given the clipped
a. Because the profile objective is concave in a, this is the exact constrained maximiser, so every EM step
still increases the objective. In Pooled, coordinates with (near-)zero standard deviation in either the target
batch or the source keep the identity (a = 1, b = 0).

**Why (QC fields only).** In the S1 probe (`Sleep-c5-chambon-t00-s0`), some Chambon feature coordinates are
constant (dead ReLU/max-pool units) in the adaptation batch. Their scale is unidentifiable, so Pooled returned
‖log a‖ = ∞ and the GEM fits ≈ 101. Only transform-size and convergence fields were inspected; no
balanced-accuracy value from the probe was displayed.
