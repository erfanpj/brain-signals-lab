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

## Reproduce (CPU only)

```
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/fetch_data.py      # 150 EDF files, about 385 MB, checksum-verified
.venv/bin/python scripts/inventory.py       # -> reports/data_inventory.json (P4.01)
.venv/bin/python scripts/sanity_checks.py   # -> reports/sanity_report.json, reports/sanity_summary.md (P4.02)
.venv/bin/python -m pytest -q
```

The participant-level outer folds were frozen in `splits/FROZEN_participant_folds.json`
(commit "Freeze participant-level outer folds…") before any modelling code existed.
`scripts/make_splits.py` refuses to produce a different split.

## How this was made

Erfan Pirjahandideh wrote this code with AI assistance (Grok Bot), and every reported number
comes from running the scripts above.
