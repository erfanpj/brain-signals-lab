"""Render reports/evaluation.json as reports/evaluation_summary.md (no recomputation)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
r = json.loads((ROOT / "reports/evaluation.json").read_text())
pa = r["participant_acc"]
L = ["# Evaluation on unseen participants (P4.03 / P4.04)", "",
     "These are engineering results for one pipeline on one public subset: PhysioNet eegmmidb, S001–S050,",
     "runs 4/8/12, imagined left vs right fist. They show how well this CSP+LDA pipeline transfers to new",
     "participants. They are not a claim about brain function or about how well motor imagery can be",
     "decoded in general. The protocol was fixed beforehand (`docs/evaluation_protocol.md`), including the",
     "logged implementation deviation. The script ran once and was not tuned on test folds.", "",
     f"**CSP+LDA: {r['csp_lda_fold_mean']:.1%} ± {r['csp_lda_fold_sd']:.1%}** (mean ± SD over 5 outer folds). Most-frequent-class baseline: "
     f"{r['chance_dummy_fold_mean']:.1%} ± {r['chance_dummy_fold_sd']:.1%}. Every fold beats its own label-permutation null "
     f"({r['n_permutations']} permutations; p = 1/101 ≈ 0.0099 is the smallest p-value this test can give).", "",
     "| Outer fold | Test participants | Selected on training only | Train trials (rejected) | Test trials | CSP+LDA | Chance (dummy) | Permutation null mean / 95th pct | p |",
     "|---|---|---|---|---|---|---|---|---|"]
for k, f in r["folds"].items():
    s = f["selected"]
    L.append(f"| {k} | {', '.join(f'S{p:03d}' for p in f['test_participants'])} | {s['band_hz'][0]:g}–{s['band_hz'][1]:g} Hz, {s['csp_components']} CSP | "
             f"{f['n_train_trials']} ({f['n_train_rejected']}) | {f['n_test_trials']} | {f['csp_lda_acc']:.1%} | {f['chance_dummy_acc']:.1%} | "
             f"{f['perm_null_mean']:.1%} / {f['perm_null_95pct']:.1%} | {f['perm_p']:.4f} |")
L += ["", f"Per test participant (n = {pa['n_participants']}): median accuracy {pa['median']:.1%} (range {pa['min']:.1%}–{pa['max']:.1%}). "
      f"{pa['n_above_chance_uncorrected_p05']} participants are above 50% by a one-sided exact binomial test at p < 0.05 (uncorrected), and "
      f"{pa['n_above_chance_holm']} remain after Holm correction across 50 participants. With about 45 trials per participant, an accuracy "
      "must reach about 64–65% (29 of 45 correct) before it is above chance at p < 0.05, so many individual results cannot be told apart from guessing.", "",
      "| Participant | Fold | Trials | Correct | Accuracy | 95% CI (Clopper–Pearson) | p (binomial, >0.5) | Above chance (Holm) |",
      "|---|---|---|---|---|---|---|---|"]
for p, v in r["participants"].items():
    L.append(f"| S{int(p):03d} | {v['fold']} | {v['n']} | {v['correct']} | {v['accuracy']:.1%} | {v['ci95'][0]:.1%}–{v['ci95'][1]:.1%} | {v['p_binom_vs_0.5']:.3g} | {'yes' if v['above_chance_holm'] else 'no'} |")
L += ["", "## Limits", "",
      "- 50 of 109 participants and 3 runs each. One public dataset, so results may not carry over to other recordings or equipment.",
      "- One train/test protocol. The SD comes from only 5 folds. The inner grid scores are close together (about 58–65%), so the band choice matters little here.",
      "- Test trials are not cleaned, and the training-only rejection removed 10–29 trials per fold.",
      "- This is a classical baseline. No neural network was trained (P4.05 decides on that separately).",
      f"- Compute: {r['cpu_seconds'] / 60:.1f} CPU-minutes for the final run (see the budget note in the repository history).", ""]
(ROOT / "reports/evaluation_summary.md").write_text("\n".join(L))
print("\n".join(L[:12]))
