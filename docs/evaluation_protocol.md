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

## Protocol addition: EEGNet-style comparison (P4.05). Committed before any NN code or run.
Requested by the project coordinator on 31 Oct 2026, 02:15 CET. This supersedes the deferral note.
The same frozen outer folds, the same 0.5–3.5 s window, and the same "training participants only"
rule apply.
- **Inputs (fixed, label-free):** each continuous run is zero-phase FIR band-passed at 4–38 Hz
  and epoched 0–4 s like P4.02. The 5 too-short trials are excluded as before. The epochs are
  cropped to 0.5–3.5 s and resampled to 80 Hz, giving 64 × 241 per trial. Amplitudes are
  divided by one scalar, the standard deviation of the retained training trials of that fold.
- **Training-only rejection:** the same Q3 + 3·IQR peak-to-peak rule, computed on these
  inputs over training trials only. Test trials are never rejected.
- **Model:** EEGNet-style (Lawhern et al., 2018): temporal conv F1 = 8 with kernel 40
  (0.5 s), depthwise spatial conv D = 2, average-pool 4, separable conv F2 = 16 with
  kernel 16, average-pool 8, linear classifier. ELU and batch norm. Adam (lr 1e-3), batch
  size 64, cross-entropy, at most 30 epochs.
- **Hyperparameters, chosen on training participants only:** dropout ∈ {0.25, 0.5} and
  the number of epochs (1–30). In each outer fold, 8 of the 40 training participants
  (seeded) are held out as inner validation. Each dropout value is trained on the other 32
  and scored on the validation participants after every epoch. The dropout and epoch count
  with the best validation accuracy are kept (ties go to the earlier epoch and to dropout
  0.25). The model is then refit on all 40 training participants with those settings and
  scores each test trial once.
- **Seeds:** torch, numpy and the shuffling use seed 20261031 + fold, and deterministic
  algorithms are enabled. Threads = 2.
- **Compute rule:** first, time ONE fit (fold 0, one dropout value, inner train →
  inner validation; no test data). Project 5 folds × (2 inner fits + 1 refit at about 1.25×
  the data). Launch only if the projection is ≤ 20 CPU-minutes. The code aborts the run,
  writing no results, if process CPU time passes 20 minutes. Run exactly once.
- **Statistics:** per fold and per participant accuracy, next to CSP+LDA and the dummy
  baseline. Per participant: exact binomial test against 0.5 with a 95% Clopper–Pearson
  interval and Holm correction (as for CSP+LDA). **Difference:** a 100× permutation refit of
  the NN would cost about 100× the run, so the per-fold chance reference for the NN is an
  exact one-sided binomial test of the fold's pooled test trials against 0.5. That test
  ignores the clustering of trials within participants, so the per-participant results
  carry more weight. NN vs CSP+LDA: per-fold differences, plus a two-sided Wilcoxon
  signed-rank test on the 50 paired participant accuracies, labelled exploratory.

## Protocol addition 2: reduced EEGNet variant ("EEGNet-R"). Committed before any new fit.
The coordinator decided on 31 Oct 2026 at 02:21 CET not to run the 45 CPU-minute protocol
above. This is a **cheaper, pre-registered variant, not the original protocol**, and it is
reported as such.
- Everything is as in addition 1 (inputs, rejection, architecture, optimiser, seeds,
  threads, 8 inner-validation participants per fold, statistics) except:
  - **dropout is fixed at 0.25**, with no dropout search. The value is chosen a priori as
    the smaller grid value; the timing fit's validation scores were never looked at;
  - **at most 15 epochs**. The epoch count (1–15) is chosen as the best accuracy on the
    inner-validation participants, with ties going to the earlier epoch. Then the model is
    refit on all 40 training participants for that many epochs.
- **Compute rule:** re-time ONE fold first (fold 0: the inner fit for 15 epochs plus a
  15-epoch refit on all training participants, with no test prediction). Project ×5.
  Launch the full run once only if the projection is ≤ 20 CPU-minutes. The cap is enforced
  in code: the run aborts and writes no results past 20 CPU-minutes of process time.
