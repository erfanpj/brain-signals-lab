import json
from pathlib import Path

import numpy as np
import pytest

from bsl.checks import clean_name, flat_channels, fold_of, line_noise_ratio, peak_to_peak, robust_z

ROOT = Path(__file__).resolve().parents[1]
FROZEN = json.loads((ROOT / "splits/FROZEN_participant_folds.json").read_text())
CFG = json.loads((ROOT / "config/subset.json").read_text())


def test_clean_name():
    assert [clean_name(c) for c in ["Fc5.", "Fcz.", "C5..", "Fp1.", "Fpz.", "Afz.", "T10."]] == ["FC5", "FCz", "C5", "Fp1", "Fpz", "AFz", "T10"]


def test_flat_and_p2p():
    x = np.vstack([np.zeros(100), np.sin(np.linspace(0, 6, 100)) * 10])
    assert flat_channels(x) == [0]
    ep = np.stack([x, 2 * x])
    assert np.allclose(peak_to_peak(ep), [np.ptp(x[1]), 2 * np.ptp(x[1])])


def test_robust_z_constant_is_zero():
    assert np.all(robust_z(np.ones(5)) == 0)


def test_line_noise_ratio_detects_peak():
    f = np.arange(0, 80.25, 0.25)
    psd = np.ones((2, f.size)); psd[1, f == 60] = 100
    assert np.allclose(line_noise_ratio(f, psd), [1, 100])


def test_frozen_folds_disjoint_complete_and_tied_to_config():
    import hashlib
    m = fold_of(FROZEN["folds"])
    assert sorted(m) == CFG["subject_ids"] and len(m) == 50
    assert all(len(v) == 10 for v in FROZEN["folds"].values())
    assert FROZEN["subset_config_sha256"] == hashlib.sha256((ROOT / "config/subset.json").read_bytes()).hexdigest()


def test_fold_of_rejects_overlap():
    with pytest.raises(ValueError):
        fold_of({"0": [1, 2], "1": [2]})


def test_reports_consistent():
    inv = json.loads((ROOT / "reports/data_inventory.json").read_text())
    rep = json.loads((ROOT / "reports/sanity_report.json").read_text())
    assert inv["n_recordings"] == 150 and inv["sfreq_values"] == [160.0] and inv["distinct_channel_sets"] == 1
    assert inv["annotation_totals"]["T1"] + inv["annotation_totals"]["T2"] == rep["n_imagery_annotations"]
    assert rep["n_epochs"] + sum(rep["epochs_dropped_by_reason"].values()) == rep["n_imagery_annotations"]
    assert sum(sum(c.values()) for c in rep["fold_class_counts"].values()) == rep["n_epochs"]
    assert all(p["fold"] == fold_of(FROZEN["folds"])[int(s)] for s, p in rep["participants"].items())
