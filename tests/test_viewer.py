import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
VIEWER = ROOT / "viewer"
MANIFEST = json.loads((VIEWER / "data-manifest.json").read_text(encoding="utf-8"))


def _load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def test_viewer_manifest_files_exist():
    for key, rel in MANIFEST["artifacts"].items():
        path = ROOT / rel
        assert path.is_file(), f"missing artifact for {key}: {rel}"


def test_viewer_signal_policy_no_edf_bundled():
    assert MANIFEST["signal_viewer"]["enabled"] is False
    data_root = ROOT / "data"
    assert not data_root.exists() or not any(data_root.rglob("*.edf"))


def test_viewer_numbers_match_evaluation_json():
    ev = _load(MANIFEST["artifacts"]["evaluation"])
    assert ev["csp_lda_fold_mean"] == pytest.approx(0.6182, abs=1e-4)
    assert ev["participant_acc"]["min"] == pytest.approx(0.4444, abs=1e-4)
    s003 = ev["participants"]["3"]
    assert s003["accuracy"] == pytest.approx(0.4444, abs=1e-4)
    assert s003["correct"] == 20 and s003["n"] == 45


def test_frozen_folds_disjoint_and_complete():
    frozen = _load(MANIFEST["artifacts"]["frozen_folds"])
    seen = []
    for fold_ids in frozen["folds"].values():
        seen.extend(fold_ids)
    assert len(seen) == 50
    assert len(set(seen)) == 50


def test_viewer_html_references_saved_artifacts_only():
    html = (VIEWER / "index.html").read_text(encoding="utf-8")
    assert "evaluation.json" in html
    assert "does not train" in html
    assert "EEGNet-R" in html


def test_eegnet_reduced_worse_than_csp_on_mean():
    nn = _load(MANIFEST["artifacts"]["eegnet_reduced"])
    ev = _load(MANIFEST["artifacts"]["evaluation"])
    assert nn["eegnet_r_fold_mean"] < ev["csp_lda_fold_mean"]
    assert "NOT the original EEGNet protocol" in nn["variant"]


def test_viewer_fold_chart_uses_zero_to_one_accuracy_scale():
    """Regression: Grok T4 — chart must not use a hidden 40% baseline."""
    js = (VIEWER / "app.js").read_text(encoding="utf-8")
    assert "- 0.4) * 300" not in js
    assert "CHART_PLOT_H" in js
    assert "accuracyBarHeight" in js


def test_participant_ci_upper_is_one_in_saved_reports():
    ev = _load(MANIFEST["artifacts"]["evaluation"])
    for p in ev["participants"].values():
        assert p["ci95"][1] == 1.0
