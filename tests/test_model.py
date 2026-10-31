import numpy as np

from bsl.model import CspLda, binom_summary, holm, keep_mask


def test_csp_lda_separates_synthetic_variance_classes():
    rng = np.random.default_rng(0)
    n, c, t = 200, 8, 200
    y = rng.integers(0, 2, n)
    X = rng.standard_normal((n, c, t)); X[y == 0, 0] *= 3; X[y == 1, 1] *= 3
    C = np.einsum("nct,ndt->ncd", X, X) / t
    m = CspLda(2).fit(C[:150], y[:150])
    assert (m.predict(C[150:]) == y[150:]).mean() > 0.9


def test_csp_lda_near_chance_on_noise():
    rng = np.random.default_rng(1)
    X = rng.standard_normal((400, 8, 100)); y = rng.integers(0, 2, 400)
    C = np.einsum("nct,ndt->ncd", X, X) / 100
    assert abs((CspLda(4).fit(C[:300], y[:300]).predict(C[300:]) == y[300:]).mean() - 0.5) < 0.15


def test_keep_mask_drops_only_extreme():
    p2p = np.r_[np.full(99, 10.0) + np.arange(99) * 0.01, 1000.0]
    m = keep_mask(p2p)
    assert m.sum() == 99 and not m[-1]


def test_binom_and_holm():
    s = binom_summary(29, 45)
    assert s["p_binom_vs_0.5"] < 0.05 and s["ci95"][0] < s["accuracy"] < s["ci95"][1]
    assert binom_summary(28, 45)["p_binom_vs_0.5"] > 0.05
    assert holm({"a": 0.001, "b": 0.02, "c": 0.04}) == {"a": True, "b": True, "c": True}
    assert holm({"a": 0.001, "b": 0.03, "c": 0.04}) == {"a": True, "b": False, "c": False}


def test_evaluation_report_consistent():
    import json
    from pathlib import Path
    r = json.loads((Path(__file__).resolve().parents[1] / "reports/evaluation.json").read_text())
    assert sum(f["n_test_trials"] for f in r["folds"].values()) == 2245
    assert len(r["participants"]) == 50
    assert all(f["test_participants"] for f in r["folds"].values())
    accs = [f["csp_lda_acc"] for f in r["folds"].values()]
    assert abs(np.mean(accs) - r["csp_lda_fold_mean"]) < 1e-4
