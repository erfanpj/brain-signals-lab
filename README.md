# brain-signals-lab

A small, CPU-only EEG engineering project. The goal is a reproducible motor-imagery
(left vs right fist) classification pipeline, evaluated only on **participants it has never
seen**, with every fold reported.

Status: work in progress. Done so far: the data inventory (P4.01), signal and label sanity
checks (P4.02), and a classical CSP+LDA baseline evaluated on unseen participants
(P4.03/P4.04).

**Result (engineering, not a neuroscience claim):** in 5 participant-level outer folds,
CSP+LDA reaches **61.8% ± 2.6%** accuracy on participants it never saw. A
most-frequent-class baseline gets 50.4% ± 0.6%. Every fold is above its label-permutation
null (p ≈ 0.01, the smallest this 100-permutation test can give). Per participant, results
range from 44% to 98%: 20 of 50 are above chance at p < 0.05 uncorrected, and 7 after Holm
correction. The fold and participant tables, the chance references and the limits are in
[reports/evaluation_summary.md](reports/evaluation_summary.md). The protocol, fixed
beforehand, and its deviation log are in
[docs/evaluation_protocol.md](docs/evaluation_protocol.md).

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
.venv/bin/python scripts/evaluate.py        # -> reports/evaluation.json (P4.03/P4.04, about 2.5 CPU-min with 2 threads)
.venv/bin/python scripts/summarize.py       # -> reports/evaluation_summary.md
.venv/bin/python -m pytest -q
```

The participant-level outer folds were frozen in `splits/FROZEN_participant_folds.json`
(commit "Freeze participant-level outer folds…") before any modelling code existed.
`scripts/make_splits.py` refuses to produce a different split.

## How this was made

Erfan Pirjahandideh wrote this code with AI assistance (Grok Bot), and every reported number
comes from running the scripts above.
