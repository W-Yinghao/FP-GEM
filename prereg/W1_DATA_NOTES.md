# W1 data notes (facts found by the pre-fleet review; no design change)

- **SC4362F0 (Sleep subject 36, night 2; source-only).** Its EDF data records are 60 s long with a 16-bit
  range (all other recordings: 30-s records, 12-bit), and its hypnogram extends ~4.2 h past the 18.9-h PSG.
  The cache uses a 30-s grid from the PSG start, so "30-s epochs on the EDF record grid" (pre-reg §3) holds
  for every recording except this one, where it is the 30-s grid from the PSG start. Labels and signal were
  verified against independent re-reads.
- **Truncated evaluation windows.** SC4492G0 and SC4592G0 (night 2 of subjects 49 and 59) end before
  lights-off + 9 h (1030 and 1002 epochs). The last ~5.5 s of their final epoch depends on the FIR filter's
  edge handling. The rows carry `truncated_night = True`.
- **Nights without N3.** 18 of the 150 paired nights have no N3 epoch in the window (night 2 of subjects 20,
  33, 34, 64, 71, 72, 73, 74, 76, and several night-1 windows). Balanced accuracy then averages over the
  classes present; `sanity_target.json` stores per-class recall and the number of classes present.
- **Unscored epochs.** 282 epochs inside all windows are `Sleep stage ?`/`Movement time` (label −1); subject
  76 night 2 has 144. They stay in adaptation batches and are excluded from training and scoring.
- **Lee timing.** Cached Lee epochs sit ≈2 ms later than the nominal −2.0 s (resampling phase and MOABB stim
  placement); B14 is exact.
- **Verification performed.** All 153 Sleep recordings: crop recomputed from lights-off + EDF header, labels
  equal to an independent annotation map (0 mismatches); 5 recordings: signal equal to an independent EDF
  read + filter (≤ 6e-8 µV). B14 subject 1: rebuilt cache byte-identical in `X`/`y`; onsets 3.0, 11.0, 18.7 s.

## Notes for later waves (from the training-code review)

- **Use `domain_stats.npz`, not checkpoint BN buffers, for TSMNet domain statistics.** Upstream's
  `eta_test` convention leaves each training domain's `running_mean_test`/`running_var_test` in `ckpt.pt`
  close to its last training batch. W1 re-centres every domain on its own data before dumping; later waves
  must take source statistics from `domain_stats.npz` (or re-centre from the dumped `S`).
- **Initialisation.** Every unit seeds with `torch.manual_seed(seed)`, so units with the same seed start
  from identical weights regardless of target; they differ through their training data and validation split
  (drawn with `rng([seed, target])`). This is a deliberate, disclosed design choice.
- **Batching is per subject.** Feature extraction batches every subject from its own first row, so a
  subject's dumped features do not depend on which other subjects were processed with it; later waves that
  re-infer features should use `fpgem.models.group_chunks` with the same batch sizes (TSMNet 256,
  braindecode 512) to reproduce the dumps bit-exactly on the same GPU/CPU type.
- **CPU dependence of `S`.** TSMNet's SPD layers run in float64 on CPU (eigh). `DONE.json` records the CPU
  model and thread count; bit-exact replays of `S` are only guaranteed on the same CPU model and threads.
