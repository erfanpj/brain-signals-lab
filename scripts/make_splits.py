"""Freeze the participant-level outer folds. Uses only participant IDs: no EEG data,
labels or model results are read. Run once; the output is committed and must not change."""
import hashlib, json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED, N_FOLDS = 20261031, 5
OUT = ROOT / "splits/FROZEN_participant_folds.json"


def main():
    cfg_bytes = (ROOT / "config/subset.json").read_bytes()
    ids = json.loads(cfg_bytes)["subject_ids"]
    perm = np.random.default_rng(SEED).permutation(ids).tolist()
    folds = [sorted(perm[i::N_FOLDS]) for i in range(N_FOLDS)]
    out = {"protocol": "outer K-fold over participants (leave-participants-out); every run of a participant stays in one fold",
           "seed": SEED, "n_folds": N_FOLDS, "generator": "numpy.random.default_rng(seed).permutation(subject_ids); fold k = perm[k::5]",
           "subset_config_sha256": hashlib.sha256(cfg_bytes).hexdigest(),
           "folds": {str(k): f for k, f in enumerate(folds)},
           "rules": ["For outer fold k, test = folds[k], train = all other participants.",
                     "Preprocessing, feature and hyper-parameter choices are fit or tuned only on training participants (inner GroupKFold by participant).",
                     "Report every outer fold and every test participant; no fold is dropped or re-drawn."]}
    if OUT.exists():
        assert json.loads(OUT.read_text()) == out, "frozen split differs - do not regenerate"
        print("unchanged"); return
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(folds)


if __name__ == "__main__":
    main()
