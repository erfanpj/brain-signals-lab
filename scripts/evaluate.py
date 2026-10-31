"""P4.03/P4.04: run the pre-registered protocol (docs/evaluation_protocol.md) once.
Writes reports/evaluation.json and reports/evaluation_summary.md."""
import json, sys, time
from pathlib import Path

import numpy as np
from sklearn.dummy import DummyClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bsl.checks import fold_of  # noqa: E402
from bsl.model import BANDS, WINDOW, binom_summary, fit, holm, load_band, predict, select_config  # noqa: E402

N_PERM, SEED = 100, 20261031


def main():
    t0 = time.process_time()
    cfg = json.loads((ROOT / "config/subset.json").read_text())
    folds = json.loads((ROOT / "splits/FROZEN_participant_folds.json").read_text())["folds"]
    data = {}
    for band in BANDS:
        X, y, g = load_band(ROOT, cfg, band)
        data[band] = X
    assert set(fold_of(folds)) == set(np.unique(g).tolist())
    rng = np.random.default_rng(SEED)
    res, per_part = {"folds": {}}, {}
    for k in sorted(folds, key=int):
        te_mask = np.isin(g, folds[k]); tr, te = np.flatnonzero(~te_mask), np.flatnonzero(te_mask)
        band, nc, grid = select_config(data, tr, y, g)
        clf, n_rej = fit(data[band], tr, y[tr], nc)
        pred = predict(clf, data[band], te)
        dummy = DummyClassifier(strategy="most_frequent").fit(np.zeros((len(tr), 1)), y[tr])
        dpred = dummy.predict(np.zeros((len(te), 1)))
        acc = float((pred == y[te]).mean()); dacc = float((dpred == y[te]).mean())
        null = []
        for _ in range(N_PERM):                      # permute labels within each training participant
            yp = y.copy()
            for p in np.unique(g[tr]):
                i = np.flatnonzero(g == p); yp[i] = rng.permutation(yp[i])
            c, _ = fit(data[band], tr, yp[tr], nc)
            null.append(float((predict(c, data[band], te) == y[te]).mean()))
        res["folds"][k] = {"test_participants": folds[k], "n_train_trials": int(len(tr)), "n_train_rejected": n_rej,
                           "n_test_trials": int(len(te)), "selected": {"band_hz": list(band), "csp_components": nc},
                           "inner_cv_grid_mean_acc": grid, "csp_lda_acc": round(acc, 4), "chance_dummy_acc": round(dacc, 4),
                           "perm_null_mean": round(float(np.mean(null)), 4), "perm_null_95pct": round(float(np.percentile(null, 95)), 4),
                           "perm_p": round((sum(n >= acc for n in null) + 1) / (N_PERM + 1), 4)}
        for p in folds[k]:
            i = g[te] == p
            per_part[p] = {"fold": int(k), **binom_summary(int((pred[i] == y[te][i]).sum()), int(i.sum())),
                           "chance_dummy_acc": round(float((dpred[i] == y[te][i]).mean()), 4)}
        print(k, res["folds"][k]["selected"], acc, dacc, res["folds"][k]["perm_p"], flush=True)
    accs = [f["csp_lda_acc"] for f in res["folds"].values()]; daccs = [f["chance_dummy_acc"] for f in res["folds"].values()]
    hp = holm({p: v["p_binom_vs_0.5"] for p, v in per_part.items()})
    for p in per_part: per_part[p]["above_chance_holm"] = hp[p]
    pa = np.array([v["accuracy"] for v in per_part.values()])
    res.update({"protocol": "docs/evaluation_protocol.md", "window_s": list(WINDOW), "n_permutations": N_PERM, "seed": SEED,
                "csp_lda_fold_mean": round(float(np.mean(accs)), 4), "csp_lda_fold_sd": round(float(np.std(accs, ddof=1)), 4),
                "chance_dummy_fold_mean": round(float(np.mean(daccs)), 4), "chance_dummy_fold_sd": round(float(np.std(daccs, ddof=1)), 4),
                "participant_acc": {"median": round(float(np.median(pa)), 4), "min": round(float(pa.min()), 4), "max": round(float(pa.max()), 4),
                                    "n_above_chance_uncorrected_p05": int(sum(v["p_binom_vs_0.5"] < 0.05 for v in per_part.values())),
                                    "n_above_chance_holm": int(sum(hp.values())), "n_participants": len(per_part)},
                "participants": {str(p): per_part[p] for p in sorted(per_part)},
                "cpu_seconds": round(time.process_time() - t0, 1)})
    (ROOT / "reports/evaluation.json").write_text(json.dumps(res, indent=1) + "\n")
    print({k: v for k, v in res.items() if k not in ("folds", "participants")})


if __name__ == "__main__":
    main()
