# W1 Appendum A2 — pre-fleet review fixes (committed before the fleet)

Date: 2026-09-27. Source: independent code review of the W1 implementation (leakage/protocol and MI-data
lenses; Sleep, training-numerics and ops lenses reported separately). All items below take effect for the
fleet; no target number motivated any of them.

1. **B14-c2 definition (made explicit).** B14-c2 is a label-defined sub-task that emulates a 2-class
   left/right recording: its training, validation, TSMNet re-centring and sanity scoring use only trials whose
   cue (= class) is left or right, for sources *and* for the target. This uses the cue type to define which
   trials the emulated recording contains (equivalent to a 2-class balanced cue schedule); it gives no
   per-trial label to any adapter. In addition, the c2 dumps now contain **all** trials of every subject:
   feet/tongue trials pass through the frozen 2-class network with `y = -1`, `in_label_set = False` and their
   4-class label in `y_orig`, for later unmodeled-class/contamination analyses. They never enter training,
   selection, or the re-centring behind the dumped `z`/`logits`.
2. **Onset.** MI caches store the cue onset of every trial (`onset_s`, seconds from run start), taken from the
   raw stim channel and checked to reproduce the epoch label sequence run by run; Sleep uses
   `record_index × 30 s`. MI caches are rebuilt; their signal arrays are byte-identical to the previous build
   (verified on B14 subject 1). Lee epochs sit ≈2 ms later than the nominal −2.0 s (MNE resampling phase and
   MOABB stim placement); timing analyses below 10 ms must not assume sample-exact cue alignment.
3. **Gate 3 in-process for every unit and row.** TSMNet logits and latents are recomputed on CPU from the
   dumped artifacts alone (checkpoint + per-domain statistics + pre-BN SPD matrices) for all rows;
   EEGNet/Chambon logits are replayed from dumped features for all rows; max abs error ≤ 1e-5 or the unit
   fails. Loaded row counts must equal the cached row counts per subject.
4. **Cache provenance.** Each unit verifies the sha256 of every cache file it reads against `MANIFEST.json`
   and records the hashes in `DONE.json`; manifests refuse incomplete or in-progress caches; cache files
   record their build commit and library versions; builders use unique temporary files; expected protocol
   trial counts are asserted at build time; the frozen config is asserted equal to the data-module constants.
5. **Target-side values out of sight.** The target sanity value is written only to `sanity_target.json`
   (not to logs, `metrics.json` or `DONE.json`) and is read only by `scripts/summarize_w1.py` after the fleet.
6. **Patience semantics (documenting the implementation).** Patience counts epochs since the last
   improvement of the selection key at any epoch; stopping is allowed only once epoch + 1 ≥ 30.
7. **Failure records.** Any exception writes a reason-coded `FAILED_<n>.json`; Sleep loaders raise on a
   missing night; a target with an empty adaptation or evaluation part fails the unit.

The probe units are re-run under A2 before the fleet (W1probeA2).
