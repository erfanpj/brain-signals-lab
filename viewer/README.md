# Results viewer (read-only)

Static pages that load saved JSON from `reports/` and `splits/`. They do not run
`evaluate.py`, download PhysioNet EDF files, or load PyTorch.

## Public demo

GitHub Pages serves the **repository root** so `../reports/*.json` resolves correctly.
The live URL is added here after signed-out verification (expected path: `/viewer/` on
`erfanpj.github.io/brain-signals-lab`).

## Run locally

From the repository root (parent of `viewer/`):

```powershell
python -m http.server 8765 --bind 127.0.0.1
```

Open http://127.0.0.1:8765/viewer/

Serving only the `viewer/` folder will fail because `fetch()` needs `../reports/`. No Python
package install is required for the viewer.

## Sections

| Tab | Source files |
|---|---|
| Protocol | `splits/FROZEN_participant_folds.json`, fields from `reports/evaluation.json` |
| Evaluation | `reports/evaluation.json`, `reports/eegnet_reduced.json` |
| Participants | `reports/evaluation.json` → `participants` (one-sided lower bounds) |
| Signal metadata | `reports/data_inventory.json` (channels, 160 Hz). No waveforms without local `fetch_data.py` |
| Limits | Fixed copy aligned with `README.md` |

Evidence screenshots: `docs/evidence/viewer-*.png` (participants file is a bounded table excerpt).

Every number in the UI should match the cited JSON field. If they diverge, treat the JSON as authoritative.

## Accessibility note

Horizontal scroll regions are focusable for narrow layouts. Native OS keyboard scrolling of
overflow regions was not fully verified in automated browser harnesses; use pointer/touch scroll
or tab to the labelled scroll regions on small screens.
