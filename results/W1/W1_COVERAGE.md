# W1 coverage and source-model sanity (descriptive; not endpoints)

units done: 657/657; missing: 0

| dataset | labels | backbone | units | subjects | eval bAcc mean (subject-level SD) | val bAcc mean | best epoch median | best epoch >= 95 | minutes median | GPUs |
|---|---|---|---|---|---|---|---|---|---|---|
| B14 | c2 | eegnet | 27 | 9 | 66.6 (12.9) | 67.9 | 28 | 0/27 | 0.4 | Tesla V100-PCIE-16GB, Tesla V100S-PCIE-32GB |
| B14 | c2 | tsmnet | 27 | 9 | 72.9 (14.1) | 72.8 | 18 | 0/27 | 1.7 | Tesla V100-PCIE-16GB, Tesla V100-PCIE-32GB, Tesla V100S-PCIE-32GB |
| B14 | c4 | eegnet | 27 | 9 | 42.8 (14.7) | 42.2 | 31 | 0/27 | 0.6 | Tesla V100-PCIE-16GB, Tesla V100-PCIE-32GB, Tesla V100S-PCIE-32GB |
| B14 | c4 | tsmnet | 27 | 9 | 53.3 (17.6) | 50.3 | 14 | 0/27 | 3.2 | Tesla V100-PCIE-16GB, Tesla V100-PCIE-32GB, Tesla V100S-PCIE-32GB |
| Lee | c2 | eegnet | 162 | 54 | 73.2 (14.8) | 72.7 | 38 | 1/162 | 3.1 | Tesla V100-PCIE-16GB, Tesla V100-PCIE-32GB, Tesla V100S-PCIE-32GB |
| Lee | c2 | tsmnet | 162 | 54 | 76.9 (14.9) | 76.1 | 13 | 1/162 | 16.0 | Tesla V100-PCIE-16GB, Tesla V100-PCIE-32GB, Tesla V100S-PCIE-32GB |
| Sleep | c5 | chambon | 225 | 75 | 72.6 (9.1) | 75.1 | 35 | 2/225 | 9.0 | NVIDIA A40, Tesla V100-PCIE-16GB, Tesla V100-PCIE-32GB, Tesla V100S-PCIE-32GB |

`best epoch >= 95`: units whose selected epoch is at the 100-epoch cap (validation bAcc still rising; possible under-training, reported as a QC diagnostic, not acted on).

Sanity eval bAcc: EEGNet/Chambon = eval-mode network with source normalisation; TSMNet = each target session re-centred on its own label-set trials (standard TSMNet inference).

