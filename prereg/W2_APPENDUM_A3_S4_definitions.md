# W2 Appendum A3 — S4 operational definitions (committed before S4 runs)

Date: 2026-09-28. No S4 output exists yet.

1. **EA with rank-deficient covariances.** Re-referencing to the mean of 3 channels removes one dimension, so
   the covariance is singular. EA uses the pseudo-inverse square root of the adaptation-session mean
   covariance: eigenvalues below 1e-8 × the largest are dropped. The source reference covariance is the
   arithmetic mean of the per-subject, per-session mean covariances of all non-target subjects, computed from
   the clean signals in the model window.
2. **Sleep re-reference.** Sleep has two bipolar EEG channels. Subtracting their mean would leave a rank-1
   signal, so the Sleep re-reference subtracts 0.5 × one randomly chosen channel from both channels. MI keeps
   the pre-registered mean-of-3-channels reference.
3. **Rows.** Readout 1 uses every labelled target row of the label set (both sessions). Readout 2 fits on the
   injected adaptation batch and scores the injected evaluation session. The same injection is applied to
   both sessions.
