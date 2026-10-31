"""P4.05 EEGNet-style comparison under the frozen protocol (docs/evaluation_protocol.md, addition).
  --time-one-fit : time ONE fit (fold 0, dropout 0.25, inner train -> inner validation; no test data)
  --run          : the full 5-fold evaluation, run once, aborted (no results written) past 20 CPU-min.
Runs with a torch-capable Python (envs/lec); inputs from scripts/prepare_nn_inputs.py."""
import json, sys, time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bsl.eegnet import BudgetExceeded, predict, train  # noqa: E402

SEED, MAX_EPOCHS, DROPOUTS, N_VAL, CAP_S = 20261031, 30, (0.25, 0.5), 8, 20 * 60
torch.set_num_threads(2)


def keep_mask(p2p):
    q1, q3 = np.percentile(p2p, [25, 75]); return p2p <= q3 + 3 * (q3 - q1)


def fold_data(X, y, g, folds, k):
    te = np.isin(g, folds[k]); tr = np.flatnonzero(~te); te = np.flatnonzero(te)
    rng = np.random.default_rng(SEED + int(k))
    val_p = rng.permutation(np.unique(g[tr]))[:N_VAL]
    return tr, te, val_p


def scaled(X, idx_fit, *idxs):
    m = keep_mask(np.ptp(X[idx_fit], axis=2).max(axis=1)); fit = idx_fit[m]
    s = float(X[fit].std())
    return fit, int((~m).sum()), [X[i] / s for i in (fit, *idxs)]


def main(mode):
    d = np.load(ROOT / "data/derived/nn_inputs.npz"); X, y, g = d["X"], d["y"], d["g"]
    folds = json.loads((ROOT / "splits/FROZEN_participant_folds.json").read_text())["folds"]
    t0 = time.process_time()
    if mode == "--time-one-fit":
        tr, _, val_p = fold_data(X, y, g, folds, "0")
        inner_tr, inner_va = tr[~np.isin(g[tr], val_p)], tr[np.isin(g[tr], val_p)]
        fit, _, (Xf, Xv) = scaled(X, inner_tr, inner_va)
        w0 = time.time(); train(Xf, y[fit], 0.25, MAX_EPOCHS, SEED, Xv, y[inner_va]); one = time.process_time() - t0
        n_inner = len(fit); n_full = int(len(tr) * 0.985)
        proj = 5 * (2 * one + one * n_full / n_inner)
        out = {"one_fit_cpu_s": round(one, 1), "one_fit_wall_s": round(time.time() - w0, 1), "inner_train_trials": n_inner,
               "epochs": MAX_EPOCHS, "projection": "5 folds x (2 inner fits + 1 refit scaled by trials)",
               "projected_full_run_cpu_s": round(proj, 1), "cap_cpu_s": CAP_S, "launch": proj <= CAP_S}
        (ROOT / "reports/eegnet_timing.json").write_text(json.dumps(out, indent=1) + "\n"); print(out); return
    res = {"folds": {}, "participants": {}}
    for k in sorted(folds, key=int):
        tr, te, val_p = fold_data(X, y, g, folds, k)
        inner_tr, inner_va = tr[~np.isin(g[tr], val_p)], tr[np.isin(g[tr], val_p)]
        fit, _, (Xf, Xv) = scaled(X, inner_tr, inner_va)
        curves = {dp: train(Xf, y[fit], dp, MAX_EPOCHS, SEED + int(k), Xv, y[inner_va], t0 + CAP_S)[1] for dp in DROPOUTS}
        best = max(((acc, -ep, -i) for i, dp in enumerate(DROPOUTS) for ep, acc in enumerate(curves[dp], 1)))
        dp, n_ep = DROPOUTS[-best[2]], -best[1]
        fit, n_rej, (Xf, Xt) = scaled(X, tr, te)
        model, _ = train(Xf, y[fit], dp, n_ep, SEED + int(k), cpu_deadline=t0 + CAP_S)
        pred = predict(model, Xt)
        res["folds"][k] = {"validation_participants": sorted(int(p) for p in val_p), "selected": {"dropout": dp, "epochs": n_ep},
                           "inner_val_best_acc": round(best[0], 4), "inner_val_curves": {str(a): [round(v, 4) for v in c] for a, c in curves.items()},
                           "n_train_trials": int(len(tr)), "n_train_rejected": n_rej, "n_test_trials": int(len(te)),
                           "correct": int((pred == y[te]).sum())}
        for p in folds[k]:
            i = g[te] == p
            res["participants"][str(p)] = {"fold": int(k), "n": int(i.sum()), "correct": int((pred[i] == y[te][i]).sum())}
        print(k, res["folds"][k]["selected"], round(time.process_time() - t0), "cpu-s", flush=True)
    res.update({"protocol": "docs/evaluation_protocol.md (EEGNet addition)", "seed": SEED, "torch": torch.__version__,
                "threads": 2, "cpu_seconds": round(time.process_time() - t0, 1)})
    (ROOT / "reports/eegnet_raw.json").write_text(json.dumps(res, indent=1) + "\n")
    print("done", res["cpu_seconds"])


if __name__ == "__main__":
    main(sys.argv[1])
