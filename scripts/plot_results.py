"""Plot per-fold test accuracy (CSP+LDA, reduced EEGNet, chance baseline) from the saved reports -> docs/images/fold_accuracy.png.
Reads reports/eegnet_reduced.json only (it repeats the CSP+LDA and dummy numbers from reports/evaluation.json)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
r = json.loads((ROOT / "reports/eegnet_reduced.json").read_text())
folds = sorted(r["folds"], key=int)
series = [("CSP+LDA", "csp_lda_acc", "#1f77b4"), ("EEGNet-R (reduced variant)", "eegnet_r_acc", "#ff7f0e"), ("Chance baseline", "chance_dummy_acc", "#7f7f7f")]
x = np.arange(len(folds)); w = 0.27
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=120)
for i, (lab, key, c) in enumerate(series):
    v = [100 * r["folds"][f][key] for f in folds]
    ax.bar(x + (i - 1) * w, v, w, label=lab, color=c)
ax.axhline(50, color="black", lw=0.8, ls=":")
ax.set_xticks(x, [f"Fold {f}\n(10 unseen participants)" for f in folds], fontsize=8)
ax.set_ylim(40, 70); ax.set_ylabel("Test accuracy (%) - axis starts at 40")
ax.set_title("Left vs right fist imagery, unseen participants (PhysioNet EEGMMIDB, 50 participants)", fontsize=9)
ax.legend(fontsize=8, loc="upper right", ncol=3); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
(ROOT / "docs/images").mkdir(parents=True, exist_ok=True)
fig.savefig(ROOT / "docs/images/fold_accuracy.png", metadata={"Software": None})
print("docs/images/fold_accuracy.png")
