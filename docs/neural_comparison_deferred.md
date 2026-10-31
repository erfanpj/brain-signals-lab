# Neural-network comparison (P4.05): timed and still deferred

**Status: no neural-network result exists, and this repository does not claim one.**

History:
1. **First decision (31 Oct 2026):** defer the comparison. The classical baseline comes first,
   and a CPU budget based on a timed single fit is needed beforehand, because the baseline's
   first evaluation run went far over its budget (see the deviation log).
2. **Timed attempt (31 Oct 2026, superseding the first note):** an EEGNet-style protocol was
   added to `docs/evaluation_protocol.md` before any NN code was written. It uses the same
   frozen folds, with dropout and epoch count chosen on training participants only and fixed
   seeds. Then ONE fit was timed. This was the only network ever trained: fold 0, dropout 0.25, 1436 inner-training trials, 30 epochs,
   2 CPU threads, inner validation only and no test data
   ([reports/eegnet_timing.json](../reports/eegnet_timing.json)).
   - One fit took **167 CPU-seconds** (86 s wall).
   - The full run needs 5 folds × (2 selection fits + 1 refit). That projects to **about 45
     CPU-minutes**, more than the 20 CPU-minute cap.
   - Following the pre-registered rule, **the full run was not launched**. No test fold was ever
     scored by the network.

To revisit, two routes stay within the same protocol spirit: (a) agree a larger budget (about
45 CPU-minutes) for the protocol exactly as written, or (b) pre-register a cheaper variant (for
example fewer epochs or one dropout value), time it again, and launch only if it fits.
`scripts/eval_eegnet.py --run` already enforces the cap in code.

Implementation note: the inputs are 64 × 240 samples per trial, not the 241 stated in the
protocol addition (0.5–3.5 s at 160 Hz resampled to 80 Hz gives 240 samples in MNE).
