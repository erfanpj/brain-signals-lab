"""CSP+LDA baseline and helpers (covariance-based CSP; see the deviation note in docs/evaluation_protocol.md). Every fitted choice (rejection threshold, CSP, LDA,
band and number of components) uses training participants only."""
import json
from pathlib import Path

import mne
import numpy as np
from scipy.linalg import eigh
from scipy.stats import binomtest
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.model_selection import GroupKFold

from bsl.checks import clean_name

BANDS = [(8.0, 13.0), (13.0, 30.0), (8.0, 30.0)]
N_COMPONENTS = [4, 6]
WINDOW = (0.5, 3.5)


def load_band(root: Path, cfg: dict, band):
    """Band-pass each continuous run (label-free), epoch 0-4 s like P4.02, crop to WINDOW."""
    mne.set_log_level("ERROR")
    X, y, g = [], [], []
    for s in cfg["subject_ids"]:
        for r in cfg["runs"]:
            raw = mne.io.read_raw_edf(root / f"data/raw/S{s:03d}/S{s:03d}R{r:02d}.edf", preload=True)
            raw.rename_channels(clean_name)
            raw.filter(*band, fir_design="firwin")
            ev, ev_id = mne.events_from_annotations(raw, event_id={"T1": 1, "T2": 2})
            ep = mne.Epochs(raw, ev, ev_id, tmin=0.0, tmax=4.0, baseline=None, preload=True, reject=None)
            ep.crop(*WINDOW)
            x = ep.get_data()
            x = x - x.mean(axis=2, keepdims=True)
            X.append((np.einsum("nct,ndt->ncd", x, x) / x.shape[2], np.ptp(x, axis=2).max(axis=1)))
            y.append(ep.events[:, 2] - 1)          # 0 = left, 1 = right
            g.append(np.full(len(ep), s))
    covs = np.concatenate([c for c, _ in X]); p2p = np.concatenate([p for _, p in X])
    return {"cov": covs, "p2p": p2p}, np.concatenate(y), np.concatenate(g)


def keep_mask(p2p: np.ndarray) -> np.ndarray:
    """Training-only rejection: drop trials with max-channel peak-to-peak > Q3 + 3*IQR."""
    q1, q3 = np.percentile(p2p, [25, 75])
    return p2p <= q3 + 3 * (q3 - q1)


class CspLda:
    """Standard CSP on trial covariance matrices (class means of trace-normalised covariances,
    generalised eigenproblem Ca w = l (Ca + Cb) w, n/2 filters from each end), log-variance
    features, then LDA."""

    def __init__(self, n_components):
        self.n = n_components

    def _feat(self, C):
        v = np.einsum("ck,ncd,dk->nk", self.W, C, self.W)
        return np.log(v)

    def fit(self, C, y):
        Cn = C / np.trace(C, axis1=1, axis2=2)[:, None, None]
        Ca, Cb = Cn[y == 0].mean(0), Cn[y == 1].mean(0)
        _, V = eigh(Ca, Ca + Cb)
        h = self.n // 2
        self.W = np.concatenate([V[:, :h], V[:, -h:]], axis=1)
        self.lda = LinearDiscriminantAnalysis().fit(self._feat(C), y)
        return self

    def predict(self, C):
        return self.lda.predict(self._feat(C))


def fit(D, idx, y, n_components):
    m = keep_mask(D["p2p"][idx])
    return CspLda(n_components).fit(D["cov"][idx][m], y[m]), int((~m).sum())


def predict(clf, D, idx):
    return clf.predict(D["cov"][idx])


def select_config(data: dict, tr_idx: np.ndarray, y, g, n_inner=5):
    """Inner GroupKFold over training participants only. Returns best (band, ncomp) and the grid."""
    grid = {}
    for band in BANDS:
        X = data[band]
        for nc in N_COMPONENTS:
            accs = []
            for itr, iva in GroupKFold(n_splits=n_inner).split(tr_idx, groups=g[tr_idx]):
                a, b = tr_idx[itr], tr_idx[iva]
                clf, _ = fit(X, a, y[a], nc)
                accs.append(float((predict(clf, X, b) == y[b]).mean()))
            grid[f"{band[0]:g}-{band[1]:g}Hz/csp{nc}"] = (float(np.mean(accs)), band, nc)
    key = max(grid, key=lambda k: grid[k][0])     # ties -> first in grid order
    return grid[key][1], grid[key][2], {k: round(v[0], 4) for k, v in grid.items()}


def binom_summary(correct: int, n: int):
    t = binomtest(correct, n, 0.5, alternative="greater")
    ci = t.proportion_ci(confidence_level=0.95, method="exact")
    return {"n": n, "correct": correct, "accuracy": round(correct / n, 4), "p_binom_vs_0.5": float(t.pvalue),
            "ci95": [round(ci.low, 4), round(ci.high, 4)]}


def holm(pvals: dict, alpha=0.05) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1]); m = len(items); out = {}; stop = False
    for i, (k, p) in enumerate(items):
        stop = stop or p > alpha / (m - i)
        out[k] = not stop
    return out
