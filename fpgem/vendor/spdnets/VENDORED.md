# Vendored: spdnets (TSMNet)

Source: https://github.com/rkobler/TSMNet, commit 90293b9 ("Update README.md"), files taken with
`git show HEAD:<path>` (not from any locally modified working tree).
License: BSD 3-Clause, Copyright (c) 2022, rkobler — see `LICENSE` in this directory.
Reference: R. Kobler, J. Hirayama, Q. Zhao, M. Kawanabe. "SPD domain-specific batch normalization to crack
interpretable unsupervised domain adaptation in EEG." NeurIPS 2022.

Files: `__init__.py`, `batchnorm.py`, `functionals.py`, `manifolds.py`, `modules.py`, `models/base.py`,
`models/tsmnet.py`, `models/__init__.py`.

Changes made for FP-GEM (everything else is byte-identical to upstream):
1. `batchnorm.py`: the `skorch` imports are replaced by a minimal local `Callback` stand-in and
   `NeuralNet = object`; scheduler logic is unchanged (including upstream's `eta_test` convention).
2. `models/tsmnet.py`: absolute `spdnets.*` imports changed to relative imports.
3. `models/__init__.py`: exports only `BaseModel`, the domain-adapt base classes and `TSMNet`
   (EEGNet/ShallowConvNet/DANN modules of upstream are not vendored).
4. `__init__.py`: emptied (upstream file is empty as well).
