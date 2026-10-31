# Evaluation on unseen participants (P4.03 / P4.04)

These are engineering results for one pipeline on one public subset: PhysioNet eegmmidb, S001–S050,
runs 4/8/12, imagined left vs right fist. They show how well this CSP+LDA pipeline transfers to new
participants. They are not a claim about brain function or about how well motor imagery can be
decoded in general. The protocol was fixed beforehand (`docs/evaluation_protocol.md`), including the
logged implementation deviation. The script ran once and was not tuned on test folds.

**CSP+LDA: 61.8% ± 2.6%** (mean ± SD over 5 outer folds). Most-frequent-class baseline: 50.4% ± 0.6%. Every fold beats its own label-permutation null (100 permutations; p = 1/101 ≈ 0.0099 is the smallest p-value this test can give).

| Outer fold | Test participants | Selected on training only | Train trials (rejected) | Test trials | CSP+LDA | Chance (dummy) | Permutation null mean / 95th pct | p |
|---|---|---|---|---|---|---|---|---|
| 0 | S006, S009, S016, S018, S019, S031, S036, S041, S043, S048 | 13–30 Hz, 4 CSP | 1796 (29) | 449 | 61.5% | 50.8% | 50.0% / 51.9% | 0.0099 |
| 1 | S007, S011, S013, S024, S025, S032, S033, S039, S040, S044 | 13–30 Hz, 4 CSP | 1795 (10) | 450 | 64.2% | 49.6% | 50.0% / 52.9% | 0.0099 |
| 2 | S001, S002, S004, S008, S015, S026, S027, S038, S042, S047 | 8–13 Hz, 4 CSP | 1795 (24) | 450 | 64.7% | 51.1% | 50.1% / 53.3% | 0.0099 |
| 3 | S005, S012, S014, S020, S022, S030, S037, S045, S046, S050 | 8–13 Hz, 4 CSP | 1797 (24) | 448 | 58.5% | 50.0% | 50.1% / 52.5% | 0.0099 |
| 4 | S003, S010, S017, S021, S023, S028, S029, S034, S035, S049 | 8–30 Hz, 6 CSP | 1797 (20) | 448 | 60.3% | 50.7% | 50.4% / 54.3% | 0.0099 |

Per test participant (n = 50): median accuracy 57.8% (range 44.4%–97.8%). 20 participants are above 50% by a one-sided exact binomial test at p < 0.05 (uncorrected), and 7 remain after Holm correction across 50 participants. With about 45 trials per participant, an accuracy must reach about 64–65% (29 of 45 correct) before it is above chance at p < 0.05, so many individual results cannot be told apart from guessing.

| Participant | Fold | Trials | Correct | Accuracy | 95% CI (Clopper–Pearson) | p (binomial, >0.5) | Above chance (Holm) |
|---|---|---|---|---|---|---|---|
| S001 | 2 | 45 | 32 | 71.1% | 58.0%–100.0% | 0.0033 | no |
| S002 | 2 | 45 | 35 | 77.8% | 65.2%–100.0% | 0.000124 | yes |
| S003 | 4 | 45 | 20 | 44.4% | 31.7%–100.0% | 0.814 | no |
| S004 | 2 | 45 | 22 | 48.9% | 35.9%–100.0% | 0.617 | no |
| S005 | 3 | 45 | 21 | 46.7% | 33.8%–100.0% | 0.724 | no |
| S006 | 0 | 45 | 22 | 48.9% | 35.9%–100.0% | 0.617 | no |
| S007 | 1 | 45 | 44 | 97.8% | 89.9%–100.0% | 1.31e-12 | yes |
| S008 | 2 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no |
| S009 | 0 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |
| S010 | 4 | 45 | 24 | 53.3% | 40.1%–100.0% | 0.383 | no |
| S011 | 1 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no |
| S012 | 3 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |
| S013 | 1 | 45 | 33 | 73.3% | 60.4%–100.0% | 0.00123 | no |
| S014 | 3 | 45 | 30 | 66.7% | 53.4%–100.0% | 0.0178 | no |
| S015 | 2 | 45 | 30 | 66.7% | 53.4%–100.0% | 0.0178 | no |
| S016 | 0 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |
| S017 | 4 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |
| S018 | 0 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |
| S019 | 0 | 45 | 28 | 62.2% | 48.9%–100.0% | 0.0676 | no |
| S020 | 3 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no |
| S021 | 4 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |
| S022 | 3 | 45 | 28 | 62.2% | 48.9%–100.0% | 0.0676 | no |
| S023 | 4 | 45 | 28 | 62.2% | 48.9%–100.0% | 0.0676 | no |
| S024 | 1 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |
| S025 | 1 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no |
| S026 | 2 | 45 | 29 | 64.4% | 51.1%–100.0% | 0.0362 | no |
| S027 | 2 | 45 | 22 | 48.9% | 35.9%–100.0% | 0.617 | no |
| S028 | 4 | 45 | 20 | 44.4% | 31.7%–100.0% | 0.814 | no |
| S029 | 4 | 45 | 33 | 73.3% | 60.4%–100.0% | 0.00123 | no |
| S030 | 3 | 45 | 34 | 75.6% | 62.8%–100.0% | 0.000412 | yes |
| S031 | 0 | 45 | 36 | 80.0% | 67.7%–100.0% | 3.29e-05 | yes |
| S032 | 1 | 45 | 29 | 64.4% | 51.1%–100.0% | 0.0362 | no |
| S033 | 1 | 45 | 33 | 73.3% | 60.4%–100.0% | 0.00123 | no |
| S034 | 4 | 43 | 37 | 86.1% | 74.3%–100.0% | 8.18e-07 | yes |
| S035 | 4 | 45 | 33 | 73.3% | 60.4%–100.0% | 0.00123 | no |
| S036 | 0 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no |
| S037 | 3 | 43 | 22 | 51.2% | 37.7%–100.0% | 0.5 | no |
| S038 | 2 | 45 | 26 | 57.8% | 44.5%–100.0% | 0.186 | no |
| S039 | 1 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no |
| S040 | 1 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no |
| S041 | 0 | 44 | 30 | 68.2% | 54.8%–100.0% | 0.0113 | no |
| S042 | 2 | 45 | 41 | 91.1% | 80.8%–100.0% | 4.67e-09 | yes |
| S043 | 0 | 45 | 36 | 80.0% | 67.7%–100.0% | 3.29e-05 | yes |
| S044 | 1 | 45 | 25 | 55.6% | 42.3%–100.0% | 0.276 | no |
| S045 | 3 | 45 | 24 | 53.3% | 40.1%–100.0% | 0.383 | no |
| S046 | 3 | 45 | 31 | 68.9% | 55.7%–100.0% | 0.00805 | no |
| S047 | 2 | 45 | 28 | 62.2% | 48.9%–100.0% | 0.0676 | no |
| S048 | 0 | 45 | 29 | 64.4% | 51.1%–100.0% | 0.0362 | no |
| S049 | 4 | 45 | 29 | 64.4% | 51.1%–100.0% | 0.0362 | no |
| S050 | 3 | 45 | 23 | 51.1% | 38.0%–100.0% | 0.5 | no |

## Limits

- 50 of 109 participants and 3 runs each. One public dataset, so results may not carry over to other recordings or equipment.
- One train/test protocol. The SD comes from only 5 folds. The inner grid scores are close together (about 58–65%), so the band choice matters little here.
- Test trials are not cleaned, and the training-only rejection removed 10–29 trials per fold.
- This is a classical baseline. A reduced EEGNet variant was compared under the same folds afterwards (reports/eegnet_reduced_summary.md); the original EEGNet protocol was not run.
- Compute: 2.5 CPU-minutes for the final run (see the budget note in the repository history).
