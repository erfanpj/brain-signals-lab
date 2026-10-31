# Results viewer (read-only)

Static pages that load saved JSON from `reports/` and `splits/`. They do not run
`evaluate.py`, download PhysioNet EDF files, or load PyTorch.

## Run locally

From the repository root (parent of `viewer/`):

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/viewer/

Serving only the `viewer/` folder will fail because `fetch()` needs `../reports/`.

## Sections

| Tab | Source files |
|---|---|
| Protocol | `splits/FROZEN_participant_folds.json`, fields from `reports/evaluation.json` |
| Evaluation | `reports/evaluation.json`, `reports/eegnet_reduced.json` |
| Participants | `reports/evaluation.json` → `participants` |
| Signal metadata | `reports/data_inventory.json` (channels, 160 Hz). No waveforms without local `fetch_data.py` |
| Limits | Fixed copy aligned with `README.md` |

Every number in the UI should match the cited JSON field. If they diverge, treat the JSON as authoritative.
