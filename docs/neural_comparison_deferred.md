# Neural-network comparison: deferred (P4.05)

Decided on 31 Oct 2026: **no neural network was trained, and this repository claims no neural
result.**

Reasons:
1. The classical baseline comes first. CSP+LDA on unseen participants is the reference that any
   neural model would have to beat under the same frozen folds and the same protocol.
2. Compute discipline. The baseline's first evaluation run went far over its logged CPU budget
   and was stopped (see the deviation log in `docs/evaluation_protocol.md`). A neural comparison
   on CPU would cost much more again, so it will not be started without a budget based on a
   timed single fit.

How to revisit: use the same frozen participant folds, the same 0.5–3.5 s window and the same
training-only selection rules, with a compact model (for example an EEGNet-style network). First
time one training fit on one outer fold, log a budget from that measurement, and then report
every fold next to the CSP+LDA and chance results.
