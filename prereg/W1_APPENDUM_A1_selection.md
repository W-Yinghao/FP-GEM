# W1 Appendum A1 — model-selection rule (committed before the fleet)

Date: 2026-09-27. Applies to all W1 units. Supersedes §4 "best-validation-loss weights are restored" and
the config key `training.selection: min_val_loss`.

## Change

Model selection and early stopping use **validation balanced accuracy** (participant-level validation
subjects, i.e. source data only): the restored epoch is the one with the highest validation bAcc; ties are
broken by lower validation loss. Early stopping: patience 20 epochs without improvement of this key, after
min 30 epochs, max 100. Everything else in W1 is unchanged.

## Why (source-side evidence only)

Probe unit `B14-c4-eegnet-t01-s0` (commit e2ef68e): the validation cross-entropy on the two held-out
**source** subjects reached its minimum at epoch 3 (1.376, i.e. the 4-class chance level ln 4 = 1.386) and
then rose because of over-confident errors on unseen subjects, while validation bAcc kept rising
(0.346 at epoch 3 → 0.398 at epoch 27). The frozen rule therefore restored a nearly untrained network. The
TSMNet probe `B14-c4-tsmnet-t01-s0` showed the same shape in milder form (val-loss minimum at epoch 6,
bAcc 0.477; later epochs reach 0.497). Cross-subject cross-entropy is dominated by calibration, whereas the
downstream quantity is balanced accuracy.

## Disclosure

While diagnosing, the two probe units' descriptive target sanity numbers were displayed (EEGNet 0.253,
TSMNet 0.722, both from the old rule). The change is justified by the validation curves above, which use
source subjects only; it was not chosen to change these target numbers, and no other target number has
been seen. Both probe units are re-run under A1 before the fleet; their W1probe outputs under the old rule
are kept in `W1probe/` for the record and are not part of W1.
