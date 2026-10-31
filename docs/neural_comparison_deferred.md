# Neural-network comparison (P4.05): history

**Current status:** the original EEGNet-style protocol was **never run**. A **reduced,
pre-registered variant** (EEGNet-R) was run once. Its results are in
[reports/eegnet_reduced_summary.md](../reports/eegnet_reduced_summary.md).

1. **Deferred** (31 Oct 2026). The classical baseline came first, and compute discipline was
   needed after the CSP+LDA run went over budget.
2. **Original protocol timed, not launched.** Protocol addition 1 was committed before any NN
   code. Then one fit was timed: fold 0, dropout 0.25, 1436 inner-training trials, 30 epochs,
   inner validation only, no test data. It took 167 CPU-s, which projects the full run to about
   45 CPU-min, over the 20 CPU-min cap, so it was not launched
   ([reports/eegnet_timing.json](../reports/eegnet_timing.json)).
3. **Reduced variant, pre-registered and run once.** Protocol addition 2 fixed dropout at 0.25
   and capped training at 15 epochs, with the epoch count chosen on validation participants. It
   was committed before any new fit. Fold 0 was re-timed at 172 CPU-s, a projection of 14.3
   CPU-min, so the full run was launched once and took 11.2 CPU-min
   ([reports/eegnet_reduced_timing.json](../reports/eegnet_reduced_timing.json)). Result:
   53.9% ± 1.4% over folds, against 61.8% ± 2.6% for CSP+LDA and about 50% chance.

The original protocol could still be run with an agreed budget of about 45 CPU-minutes.

Implementation note: the inputs are 64 × 240 samples per trial, not the 241 stated in
protocol addition 1, because MNE resamples 0.5–3.5 s at 160 Hz to 240 samples at 80 Hz.
