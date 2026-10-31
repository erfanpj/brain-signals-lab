"""P4.05 inputs (label-free, fixed): 4-38 Hz band-pass, epoch 0-4 s (as P4.02), crop 0.5-3.5 s,
resample to 80 Hz -> data/derived/nn_inputs.npz (git-ignored; derived from the dataset)."""
import json, sys
from pathlib import Path

import mne
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bsl.checks import clean_name  # noqa: E402


def main():
    mne.set_log_level("ERROR")
    cfg = json.loads((ROOT / "config/subset.json").read_text())
    X, y, g = [], [], []
    for s in cfg["subject_ids"]:
        for r in cfg["runs"]:
            raw = mne.io.read_raw_edf(ROOT / f"data/raw/S{s:03d}/S{s:03d}R{r:02d}.edf", preload=True)
            raw.rename_channels(clean_name)
            raw.filter(4.0, 38.0, fir_design="firwin")
            ev, ev_id = mne.events_from_annotations(raw, event_id={"T1": 1, "T2": 2})
            ep = mne.Epochs(raw, ev, ev_id, tmin=0.0, tmax=4.0, baseline=None, preload=True, reject=None)
            ep.crop(0.5, 3.5).resample(80.0)
            X.append(ep.get_data().astype(np.float32)); y.append(ep.events[:, 2] - 1); g.append(np.full(len(ep), s))
    X, y, g = np.concatenate(X), np.concatenate(y), np.concatenate(g)
    out = ROOT / "data/derived/nn_inputs.npz"; out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, X=X, y=y, g=g)
    print(X.shape, np.bincount(y), len(np.unique(g)))


if __name__ == "__main__":
    main()
