# Evaluation protocol (P4.03 / P4.04). Fixed before any modelling code.

Task: classify imagined **left vs right fist** trials (runs 4, 8, 12) for participants who
were never seen during training. These are engineering results about one pipeline on one
public dataset subset. They are not claims about brain function.

## Frozen pieces
- Outer folds: `splits/FROZEN_participant_folds.json` (5 folds × 10 participants). For
  fold k, the 10 participants in fold k are the test set and the other 40 are training.
  A participant's runs are never split.
- Epoch window: **0.5–3.5 s after the cue**. This is fixed and not tuned. It skips the
  visual-cue onset response, and every cue lasts at least 4.0 s. The 5 cues whose window
  runs past the end of the recording are excluded, as in P4.02.

## Pipelines
1. **Chance baseline**: `DummyClassifier(strategy="most_frequent")` fitted on the
   training participants.
2. **CSP + LDA**: band-pass filter → CSP (log-variance features) → LDA, with
   scikit-learn and MNE defaults otherwise.

## Choices fitted on training participants only (every outer fold)
- Band and number of CSP components are picked from a fixed grid: bands {8–13, 13–30,
  8–30} Hz × components {4, 6} (6 configurations). The pick is the best mean accuracy
  in an inner 5-fold `GroupKFold` grouped by participant, over the 40 training
  participants only. Filtering is zero-phase FIR on continuous runs, which uses no
  labels, so it can be precomputed per band.
- Trial rejection, for training trials only: drop a training trial if its peak-to-peak
  amplitude (maximum over channels, in the chosen band) is above Q3 + 3·IQR, with the
  quartiles computed on training trials only. **Test trials are never rejected.** Every
  test trial is scored.
- The CSP filters and LDA weights are fitted on the retained training trials.

## Reporting
- Accuracy for every outer fold and every test participant, for both pipelines, plus the
  mean and SD across the 5 folds.
- Chance references:
  - **Per participant**: an exact binomial test against p = 0.5 (one-sided) and a 95%
    Clopper–Pearson interval, with n = that participant's scored trials. The count of
    participants above chance is reported uncorrected and with Holm correction across
    50 participants.
  - **Per fold**: a label-permutation test. With the configuration chosen for that fold
    held fixed, the training labels are permuted within each training participant
    100 times and the model is refit. p = (k + 1) / (100 + 1).
- Nothing is changed after the test results are seen. If something has to change, it
  will be logged as a deviation, with the original result kept.

## Deviation log
- **2026-10-31 02:07 CET, before any result was seen.** The first run used MNE's `CSP`
  inside an sklearn pipeline and refit it on the raw epochs about 650 times (150 inner
  fits and 500 permutation fits). It went far over the compute budget and was stopped.
  No fold or test number had been printed or saved. Nothing else changed: same folds,
  window, grid, rejection rule, LDA and permutation scheme. Per-trial covariance matrices
  are now precomputed for each band, and CSP is solved directly as the generalised
  eigenproblem on the class-mean trace-normalised covariances (`bsl/model.py`,
  `CspLda`), taking n/2 filters from each end. The features are log-variances without
  further normalisation. This is standard CSP, but it is not numerically identical to
  MNE's defaults (MNE estimates covariances by concatenating trials and orders
  components by mutual information).
