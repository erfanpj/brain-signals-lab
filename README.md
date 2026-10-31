# brain-signals-lab

A small, CPU-only EEG engineering project. The goal is a reproducible motor-imagery
(left vs right fist) classification pipeline, evaluated only on **participants it has never
seen**, with every fold reported.

Status: work in progress. So far there is a data inventory (P4.01) and signal and label
sanity checks (P4.02). No model has been trained yet, so this repository makes no
classification or neuroscience claims.

- Data: PhysioNet EEG Motor Movement/Imagery Dataset v1.0.0 (ODC-By 1.0). See
  [DATA.md](DATA.md). The data is **not** included or redistributed here; run
  `python scripts/fetch_data.py` to download the fixed subset and verify it against
  PhysioNet's checksums.
- Licence: the code is MIT ([LICENSE](LICENSE)). The licence does not cover the dataset,
  which stays under its own ODC-By 1.0 licence and must be cited (see DATA.md).
