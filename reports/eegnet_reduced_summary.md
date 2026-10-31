# Reduced EEGNet variant vs CSP+LDA vs chance (unseen participants)

**This is a reduced, pre-registered variant (dropout fixed at 0.25, at most 15 epochs; protocol addition 2 in
`docs/evaluation_protocol.md`), not the original EEGNet protocol, which was never run.** It uses the same frozen
folds as CSP+LDA, and the epoch count was chosen on inner-validation training participants. It ran once, with
11.2 CPU-minutes against a 20-minute cap. These are engineering results only.

| Outer fold | Epochs (chosen on validation) | Test trials | EEGNet-R | CSP+LDA | Difference | Chance (dummy) | Pooled binomial p (vs 0.5) |
|---|---|---|---|---|---|---|---|
| 0 | 15 | 449 | 55.9% | 61.5% | -5.6 pts | 50.8% | 0.007 |
| 1 | 11 | 450 | 53.1% | 64.2% | -11.1 pts | 49.6% | 0.1 |
| 2 | 9 | 450 | 54.2% | 64.7% | -10.4 pts | 51.1% | 0.041 |
| 3 | 12 | 448 | 54.2% | 58.5% | -4.2 pts | 50.0% | 0.04 |
| 4 | 7 | 448 | 52.2% | 60.3% | -8.0 pts | 50.7% | 0.18 |
| **Mean ± SD** | | 2245 | **53.9% ± 1.4%** | 61.8% ± 2.6% | | 50.4% | |

The per-fold chance reference for EEGNet-R is an exact binomial test on the fold's pooled test trials. That test
ignores the clustering of trials within participants, which makes it optimistic. A 100× permutation refit, as used
for CSP+LDA, was too expensive.

Per participant (n = 50): median 54.4% (range 40.0%–71.1%); 4 above chance at p < 0.05 uncorrected, 0 after Holm.

Paired against CSP+LDA (exploratory): median per-participant difference -6.7 pts; EEGNet-R better for 12, CSP+LDA better for 33, tied for 5; two-sided Wilcoxon signed-rank p = 0.00015.

| Participant | Fold | Trials | EEGNet-R correct | EEGNet-R | 95% CI | p (binomial) | Holm | CSP+LDA |
|---|---|---|---|---|---|---|---|---|
| S001 | 2 | 45 | 28 | 62.2% | 48.9%–100.0% | 0.0676 | no | 71.1% |
| S002 | 2 | 45 | 21 | 46.7% | 33.8%–100.0% | 0.724 | no | 77.8% |
| S003 | 4 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 44.4% |
| S004 | 2 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no | 48.9% |
| S005 | 3 | 45 | 21 | 46.7% | 33.8%–100.0% | 0.724 | no | 46.7% |
| S006 | 0 | 45 | 29 | 64.4% | 51.1%–100.0% | 0.0362 | no | 48.9% |
| S007 | 1 | 45 | 27 | 60.0% | 46.7%–100.0% | 0.116 | no | 97.8% |
| S008 | 2 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no | 57.8% |
| S009 | 0 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 51.1% |
| S010 | 4 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 53.3% |
| S011 | 1 | 45 | 22 | 48.9% | 35.9%–100.0% | 0.617 | no | 57.8% |
| S012 | 3 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 51.1% |
| S013 | 1 | 45 | 20 | 44.4% | 31.7%–100.0% | 0.814 | no | 73.3% |
| S014 | 3 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 66.7% |
| S015 | 2 | 45 | 22 | 48.9% | 35.9%–100.0% | 0.617 | no | 66.7% |
| S016 | 0 | 45 | 30 | 66.7% | 53.4%–100.0% | 0.0178 | no | 51.1% |
| S017 | 4 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no | 51.1% |
| S018 | 0 | 45 | 24 | 53.3% | 40.1%–100.0% | 0.383 | no | 51.1% |
| S019 | 0 | 45 | 21 | 46.7% | 33.8%–100.0% | 0.724 | no | 62.2% |
| S020 | 3 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no | 57.8% |
| S021 | 4 | 45 | 24 | 53.3% | 40.1%–100.0% | 0.383 | no | 51.1% |
| S022 | 3 | 45 | 20 | 44.4% | 31.7%–100.0% | 0.814 | no | 62.2% |
| S023 | 4 | 45 | 22 | 48.9% | 35.9%–100.0% | 0.617 | no | 62.2% |
| S024 | 1 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no | 51.1% |
| S025 | 1 | 45 | 24 | 53.3% | 40.1%–100.0% | 0.383 | no | 57.8% |
| S026 | 2 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no | 64.4% |
| S027 | 2 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no | 48.9% |
| S028 | 4 | 45 | 20 | 44.4% | 31.7%–100.0% | 0.814 | no | 44.4% |
| S029 | 4 | 45 | 21 | 46.7% | 33.8%–100.0% | 0.724 | no | 73.3% |
| S030 | 3 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 75.6% |
| S031 | 0 | 45 | 32 | 71.1% | 58.0%–100.0% | 0.0033 | no | 80.0% |
| S032 | 1 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 64.4% |
| S033 | 1 | 45 | 32 | 71.1% | 58.0%–100.0% | 0.0033 | no | 73.3% |
| S034 | 4 | 43 | 24 | 55.8% | 42.2%–100.0% | 0.271 | no | 86.1% |
| S035 | 4 | 45 | 27 | 60.0% | 46.7%–100.0% | 0.116 | no | 73.3% |
| S036 | 0 | 45 | 22 | 48.9% | 35.9%–100.0% | 0.617 | no | 57.8% |
| S037 | 3 | 43 | 21 | 48.8% | 35.5%–100.0% | 0.62 | no | 51.2% |
| S038 | 2 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 57.8% |
| S039 | 1 | 45 | 24 | 53.3% | 40.1%–100.0% | 0.383 | no | 55.6% |
| S040 | 1 | 45 | 18 | 40.0% | 27.7%–100.0% | 0.932 | no | 55.6% |
| S041 | 0 | 44 | 22 | 50.0% | 36.8%–100.0% | 0.56 | no | 68.2% |
| S042 | 2 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 91.1% |
| S043 | 0 | 45 | 21 | 46.7% | 33.8%–100.0% | 0.724 | no | 80.0% |
| S044 | 1 | 45 | 24 | 53.3% | 40.1%–100.0% | 0.383 | no | 55.6% |
| S045 | 3 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no | 53.3% |
| S046 | 3 | 45 | 28 | 62.2% | 48.9%–100.0% | 0.0676 | no | 68.9% |
| S047 | 2 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 62.2% |
| S048 | 0 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no | 64.4% |
| S049 | 4 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no | 64.4% |
| S050 | 3 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no | 51.1% |

Limits: this is a reduced variant with a single seed per fold and no dropout search. In fold 0 the best
validation epoch was the maximum (15), so that fold may be under-trained. Only 5 folds, so the spread estimates are
rough. The paired test is exploratory and was not a pre-registered hypothesis test.
