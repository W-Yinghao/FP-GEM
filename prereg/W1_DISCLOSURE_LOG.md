# W1 disclosure log

Chronological record of every occasion on which target-side numbers were displayed before the W1 fleet,
and of what (if anything) followed from them. Target numbers must not drive W1 design decisions.

| When (2026-09-27) | What was displayed | Why | Consequence |
|---|---|---|---|
| probe, commit e2ef68e | target sanity bAcc of `B14-c4-eegnet-t01-s0` (0.253) and `B14-c4-tsmnet-t01-s0` (0.722), old min-val-loss rule | end-of-unit log line printed by the runner | Appendum A1 (selection on validation bAcc) was derived from the **validation** curves only; see A1 |
| probe, commit 8910c17 | target sanity bAcc of the same two units under A1 (EEGNet 0.545, TSMNet 0.778) | smoke test of `scripts/summarize_w1.py` on the probe directory | none; no design change follows from these values |
| probe, commit 8910c17 | target sanity bAcc of `Lee-c2-eegnet-t01-s0` (0.840) and `Sleep-c5-chambon-t00-s0` (0.760) | end-of-unit log line (the runner change that stops printing it was not yet committed when these probes launched) | none |

From here on, runner log lines and probe checks report validation metrics and QC flags only; target
sanity values are read only by `scripts/summarize_w1.py` after the fleet completes.
