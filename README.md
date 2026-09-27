# FP-GEM — prior–geometry identification for EEG test-time adaptation

Research code for a restarted study of unlabeled EEG adaptation under mixed shift: when class proportions
and the feature/acquisition geometry change together, which observations, structure and estimators make the
adaptation decision identifiable, estimable and useful? Fixed-Prior Geometry EM (FP-GEM) is one constrained
answer and a reference point, not a presupposed winner (see `docs/plans/`).

The project is run as pre-registered waves. Every wave is frozen in `prereg/` before compute; configs in
`configs/` are the single source of truth; results are reported neutrally.

| Wave | Content | Status |
|---|---|---|
| W1 | Source retraining (LOSO) + complete per-trial dumps for B14 (4- and 2-class), Lee2019-MI, Sleep-EDF; TSMNet / EEGNet / Chambon backbones | frozen: `prereg/W1_SOURCE_RETRAIN_FROZEN.md` |

## Layout

```
fpgem/            package: data caches (MOABB, Sleep-EDF), backbones, training units, provenance
fpgem/vendor/     third-party code vendored under its license (TSMNet/spdnets, BSD-3; see VENDORED.md)
scripts/          CLIs: build_cache, make_units, run_unit
slurm/            cache / unit sbatch scripts and the capped self-healing driver
configs/          frozen wave configs and unit lists
prereg/           frozen pre-registrations and appenda
docs/plans/       revision/direction plans v1–v5 and the Sprint-0 kickoff (history)
docs/sprint0_audit/  audit of the previous implementation (history; its numbers are not reused)
```

Large artifacts (caches, checkpoints, dumps, logs) live outside the repository under `$FPGEM_STORE`
(default `/home/infres/yinwang/fpgem_store`).

## Reproducing W1

```bash
# 1. caches (CPU)
sbatch -J fpg-cache-B14 slurm/cache.sbatch B14 1-9         # needs FPGEM_REPO / FPGEM_LAUNCH_SHA exported
python -m scripts.build_cache --dataset B14 --manifest
# 2. units (GPU), capped at 8 concurrent SLURM tasks
python -m scripts.make_units
sbatch -p CPU -c 1 --mem=1G --time=4-00:00:00 -J fpg-drv-W1 --wrap "bash slurm/driver.sh W1 configs/units_W1.txt"
```

Environment: Python 3.9, torch 2.8, braindecode 0.8, moabb 1.2, mne 1.8, geoopt 0.5.1.
Data: BNCI2014-001 and Lee2019-MI through MOABB; Sleep-EDF Expanded (sleep-cassette) from PhysioNet, with
lights-off times from PhysioNet's `SC-subjects.xls` (copied to `fpgem/data/sc_subjects.csv`).
