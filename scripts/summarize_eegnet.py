"""Statistics for the reduced EEGNet variant next to CSP+LDA and chance (protocol addition 2).
Reads reports/eegnet_reduced_raw.json + reports/evaluation.json; writes reports/eegnet_reduced.json
and reports/eegnet_reduced_summary.md. No model is fitted."""
import json, sys
from pathlib import Path

import numpy as np
from scipy.stats import binomtest, wilcoxon

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bsl.model import binom_summary, holm  # noqa: E402

nn = json.loads((ROOT / "reports/eegnet_reduced_raw.json").read_text())
cl = json.loads((ROOT / "reports/evaluation.json").read_text())
folds = {}
for k, f in nn["folds"].items():
    acc = f["correct"] / f["n_test_trials"]
    folds[k] = {"selected": f["selected"], "n_test_trials": f["n_test_trials"], "eegnet_r_acc": round(acc, 4),
                "csp_lda_acc": cl["folds"][k]["csp_lda_acc"], "chance_dummy_acc": cl["folds"][k]["chance_dummy_acc"],
                "diff_vs_csp_lda": round(acc - cl["folds"][k]["csp_lda_acc"], 4),
                "p_binom_pooled_vs_0.5": float(binomtest(f["correct"], f["n_test_trials"], 0.5, alternative="greater").pvalue)}
parts = {p: {"fold": v["fold"], **binom_summary(v["correct"], v["n"]), "csp_lda_accuracy": cl["participants"][p]["accuracy"]}
         for p, v in nn["participants"].items()}
hp = holm({p: v["p_binom_vs_0.5"] for p, v in parts.items()})
for p in parts: parts[p]["above_chance_holm"] = hp[p]
a = np.array([v["accuracy"] for v in parts.values()]); b = np.array([v["csp_lda_accuracy"] for v in parts.values()])
w = wilcoxon(a, b, alternative="two-sided")
accs = [f["eegnet_r_acc"] for f in folds.values()]
out = {"variant": "reduced (protocol addition 2: dropout 0.25, max 15 epochs) - NOT the original EEGNet protocol",
       "eegnet_r_fold_mean": round(float(np.mean(accs)), 4), "eegnet_r_fold_sd": round(float(np.std(accs, ddof=1)), 4),
       "csp_lda_fold_mean": cl["csp_lda_fold_mean"], "csp_lda_fold_sd": cl["csp_lda_fold_sd"],
       "chance_dummy_fold_mean": cl["chance_dummy_fold_mean"],
       "participant_acc": {"median": round(float(np.median(a)), 4), "min": round(float(a.min()), 4), "max": round(float(a.max()), 4),
                           "n_above_chance_uncorrected_p05": int(sum(v["p_binom_vs_0.5"] < 0.05 for v in parts.values())),
                           "n_above_chance_holm": int(sum(hp.values())), "n_participants": len(parts)},
       "paired_vs_csp_lda_exploratory": {"median_diff": round(float(np.median(a - b)), 4), "n_nn_better": int((a > b).sum()),
                                          "n_csp_better": int((a < b).sum()), "n_tied": int((a == b).sum()),
                                          "wilcoxon_two_sided_p": float(w.pvalue)},
       "cpu_seconds": nn["cpu_seconds"], "torch": nn["torch"], "folds": folds, "participants": parts}
(ROOT / "reports/eegnet_reduced.json").write_text(json.dumps(out, indent=1) + "\n")
pa, pv = out["participant_acc"], out["paired_vs_csp_lda_exploratory"]
L = ["# Reduced EEGNet variant vs CSP+LDA vs chance (unseen participants)", "",
     "**This is a reduced, pre-registered variant (dropout fixed at 0.25, at most 15 epochs; protocol addition 2 in",
     "`docs/evaluation_protocol.md`), not the original EEGNet protocol, which was never run.** It uses the same frozen",
     "folds as CSP+LDA, and the epoch count was chosen on inner-validation training participants. It ran once, with",
     f"{out['cpu_seconds'] / 60:.1f} CPU-minutes against a 20-minute cap. These are engineering results only.", "",
     "| Outer fold | Epochs (chosen on validation) | Test trials | EEGNet-R | CSP+LDA | Difference | Chance (dummy) | Pooled binomial p (vs 0.5) |",
     "|---|---|---|---|---|---|---|---|"]
for k, f in folds.items():
    L.append(f"| {k} | {f['selected']['epochs']} | {f['n_test_trials']} | {f['eegnet_r_acc']:.1%} | {f['csp_lda_acc']:.1%} | {f['diff_vs_csp_lda']*100:+.1f} pts | {f['chance_dummy_acc']:.1%} | {f['p_binom_pooled_vs_0.5']:.2g} |")
L += [f"| **Mean ± SD** | | 2245 | **{out['eegnet_r_fold_mean']:.1%} ± {out['eegnet_r_fold_sd']:.1%}** | {out['csp_lda_fold_mean']:.1%} ± {out['csp_lda_fold_sd']:.1%} | | {out['chance_dummy_fold_mean']:.1%} | |", "",
      "The per-fold chance reference for EEGNet-R is an exact binomial test on the fold's pooled test trials. That test",
      "ignores the clustering of trials within participants, which makes it optimistic. A 100× permutation refit, as used",
      "for CSP+LDA, was too expensive.", "",
      f"Per participant (n = {pa['n_participants']}): median {pa['median']:.1%} (range {pa['min']:.1%}–{pa['max']:.1%}); "
      f"{pa['n_above_chance_uncorrected_p05']} above chance at p < 0.05 uncorrected, {pa['n_above_chance_holm']} after Holm.", "",
      f"Paired against CSP+LDA (exploratory): median per-participant difference {pv['median_diff']*100:+.1f} pts; "
      f"EEGNet-R better for {pv['n_nn_better']}, CSP+LDA better for {pv['n_csp_better']}, tied for {pv['n_tied']}; "
      f"two-sided Wilcoxon signed-rank p = {pv['wilcoxon_two_sided_p']:.2g}.", "",
      "| Participant | Fold | Trials | EEGNet-R correct | EEGNet-R | 95% CI | p (binomial) | Holm | CSP+LDA |", "|---|---|---|---|---|---|---|---|---|"]
for p, v in sorted(parts.items(), key=lambda kv: int(kv[0])):
    L.append(f"| S{int(p):03d} | {v['fold']} | {v['n']} | {v['correct']} | {v['accuracy']:.1%} | {v['ci95'][0]:.1%}–{v['ci95'][1]:.1%} | {v['p_binom_vs_0.5']:.3g} | {'yes' if v['above_chance_holm'] else 'no'} | {v['csp_lda_accuracy']:.1%} |")
L += ["", "Limits: this is a reduced variant with a single seed per fold and no dropout search. In fold 0 the best",
      "validation epoch was the maximum (15), so that fold may be under-trained. Only 5 folds, so the spread estimates are",
      "rough. The paired test is exploratory and was not a pre-registered hypothesis test.", ""]
(ROOT / "reports/eegnet_reduced_summary.md").write_text("\n".join(L))
print("\n".join(L[7:24]))
