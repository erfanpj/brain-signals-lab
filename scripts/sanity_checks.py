"""P4.02: shapes, class counts and descriptive artifact checks for the fixed subset,
with every epoch kept tagged by participant and frozen outer fold.
Writes reports/sanity_report.json and reports/sanity_summary.md. No model is fitted."""
import json, sys
from collections import Counter, defaultdict
from pathlib import Path

import mne
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bsl.checks import LABELS, clean_name, flat_channels, fold_of, line_noise_ratio, peak_to_peak, robust_z  # noqa: E402

CFG = json.loads((ROOT / "config/subset.json").read_text())
FOLDS = json.loads((ROOT / "splits/FROZEN_participant_folds.json").read_text())["folds"]
TMIN, TMAX = 0.0, 4.0          # seconds after cue onset; every T1/T2 annotation lasts >= 4.0 s
P2P_LEVELS = (100.0, 150.0)    # µV, descriptive levels only, nothing is rejected
VAR_Z = 5.0                    # robust z of log channel variance within a run
BAND = (1.0, 40.0)             # Hz, fixed descriptive band-pass for amplitude checks (removes drift and 60 Hz)


def main():
    mne.set_log_level("ERROR")
    fold = fold_of(FOLDS)
    montage = mne.channels.make_standard_montage("standard_1005")
    per_part = defaultdict(lambda: {"fold": None, "n_runs": 0, "counts": Counter(), "p2p_uv": [], "flat": [], "high_var": [], "nan": 0})
    shapes, unmatched, line, dropped = Counter(), set(), [], Counter()
    for s in CFG["subject_ids"]:
        d = per_part[s]; d["fold"] = fold[s]
        for r in CFG["runs"]:
            raw = mne.io.read_raw_edf(ROOT / f"data/raw/S{s:03d}/S{s:03d}R{r:02d}.edf", preload=True)
            raw.rename_channels(clean_name)
            unmatched |= set(raw.ch_names) - set(montage.ch_names)
            x = raw.get_data() * 1e6
            d["nan"] += int(np.isnan(x).sum()); d["n_runs"] += 1
            d["flat"] += [raw.ch_names[i] for i in flat_channels(x)]
            z = robust_z(np.log(x.var(axis=1)))
            d["high_var"] += [raw.ch_names[i] for i in np.flatnonzero(np.abs(z) > VAR_Z)]
            psd = raw.compute_psd(fmin=1, fmax=79, n_fft=640)
            line.append(float(np.median(line_noise_ratio(psd.freqs, psd.get_data()))))
            filt = raw.copy().filter(*BAND, fir_design="firwin")
            ev, ev_id = mne.events_from_annotations(raw, event_id={"T1": 1, "T2": 2})
            ep_raw = mne.Epochs(raw, ev, ev_id, tmin=TMIN, tmax=TMAX, baseline=None, preload=True, reject=None, verbose=False)
            raw_p2p = peak_to_peak(ep_raw.get_data() * 1e6)
            dropped.update(r for log in ep_raw.drop_log for r in log)
            ep = mne.Epochs(filt, ev, ev_id, tmin=TMIN, tmax=TMAX, baseline=None, preload=True, reject=None, verbose=False)
            shapes[ep.get_data().shape[1:]] += 1
            for code, n in Counter(ep.events[:, 2]).items():
                d["counts"][LABELS["T1" if code == 1 else "T2"]] += int(n)
            d["p2p_uv"] += peak_to_peak(ep.get_data() * 1e6).tolist(); d.setdefault("raw_p2p", []).extend(raw_p2p.tolist())
    parts = {}
    for s, d in per_part.items():
        p2p = np.array(d["p2p_uv"])
        parts[s] = {"fold": d["fold"], "n_runs": d["n_runs"], "class_counts": dict(sorted(d["counts"].items())),
                    "n_epochs": int(p2p.size), "p2p_median_uv": round(float(np.median(p2p)), 1),
                    **{f"frac_epochs_p2p_over_{int(l)}uv": round(float((p2p > l).mean()), 3) for l in P2P_LEVELS},
                    "flat_channels": sorted(set(d["flat"])), "high_variance_channels": dict(Counter(d["high_var"])), "nan_samples": d["nan"]}
    fold_counts = {k: dict(sum((Counter(parts[p]["class_counts"]) for p in m), Counter())) for k, m in FOLDS.items()}
    all_p2p = np.concatenate([np.array(per_part[s]["p2p_uv"]) for s in per_part])
    rep = {"epoch_window_s": [TMIN, TMAX], "epoch_shapes_channels_x_samples": {str(k): v for k, v in shapes.items()},
           "n_epochs": int(all_p2p.size), "n_imagery_annotations": 2250, "epochs_dropped_by_reason": dict(dropped), "amplitude_band_hz": list(BAND),
           "unfiltered_p2p_uv_median": round(float(np.median(np.concatenate([np.array(per_part[s]["raw_p2p"]) for s in per_part]))), 1), "class_totals": dict(sum((Counter(p["class_counts"]) for p in parts.values()), Counter())),
           "channels_not_in_standard_1005": sorted(unmatched), "fold_class_counts": fold_counts,
           "participants_per_fold": {k: len(m) for k, m in FOLDS.items()},
           "p2p_uv_quantiles": {q: round(float(np.quantile(all_p2p, q / 100)), 1) for q in (5, 25, 50, 75, 95, 99)},
           **{f"frac_epochs_p2p_over_{int(l)}uv": round(float((all_p2p > l).mean()), 3) for l in P2P_LEVELS},
           "line_noise_ratio_60hz_median_per_run": {"min": round(min(line), 2), "median": round(float(np.median(line)), 2), "max": round(max(line), 2), "runs_over_10": sum(v > 10 for v in line), "n_runs": len(line)},
           "participants": {str(k): v for k, v in sorted(parts.items())}}
    (ROOT / "reports/sanity_report.json").write_text(json.dumps(rep, indent=1) + "\n")
    worst = sorted(parts.items(), key=lambda kv: -kv[1]["frac_epochs_p2p_over_150uv"])[:5]
    md = ["# Sanity checks (P4.02): measured on S001-S050, runs 4/8/12", "",
          "This report is generated by `scripts/sanity_checks.py`. It describes the data only: no epoch or",
          "participant is removed, and no model has been fitted. Peak-to-peak levels are descriptive",
          "thresholds, not rejection rules. Any rejection rule must later be fixed using training",
          "participants only.", "",
          f"- Epochs: {rep['n_epochs']} imagery trials, window {TMIN}-{TMAX} s after the cue; shape (channels × samples): {rep['epoch_shapes_channels_x_samples']}",
          f"- Class totals: {rep['class_totals']}",
          f"- Per outer fold (10 participants each): {fold_counts}",
          f"- Channel names not found in MNE's standard_1005 montage after cleaning: {rep['channels_not_in_standard_1005'] or 'none'}",
          f"- NaN samples: {sum(p['nan_samples'] for p in parts.values())}; flat channels (std < 0.5 µV over a run): {sorted({c for p in parts.values() for c in p['flat_channels']}) or 'none'}",
          f"- Imagery annotations: 2250; epochs kept: {rep['n_epochs']}; dropped by MNE (reason: count): {rep['epochs_dropped_by_reason'] or 'none'} (a 4 s window that runs past the end of the recording)",
          f"- Amplitude checks below use a fixed {BAND[0]:g}-{BAND[1]:g} Hz band-pass (label-free). Without it, the median peak-to-peak is {rep['unfiltered_p2p_uv_median']} µV, dominated by slow drift.",
          f"- Peak-to-peak (max over channels) per epoch, µV quantiles: {rep['p2p_uv_quantiles']}",
          f"- Epochs over 100 µV: {rep['frac_epochs_p2p_over_100uv']:.1%}; over 150 µV: {rep['frac_epochs_p2p_over_150uv']:.1%}",
          f"- 60 Hz line-noise ratio (median over channels, per run): {rep['line_noise_ratio_60hz_median_per_run']}",
          f"- Runs whose median 60 Hz ratio is over 10: {rep['line_noise_ratio_60hz_median_per_run']['runs_over_10']} of {len(line)} (mains noise is common, so later models should stay below 60 Hz or notch it)",
          "- Participants with the most epochs over 150 µV: " + "; ".join(f"S{s:03d} {v['frac_epochs_p2p_over_150uv']:.0%} (fold {v['fold']})" for s, v in worst),
          "", "Engineering takeaway: EDF units are µV (checked in the file headers), but these recordings have large amplitudes,",
          "and frontal channels (Fp1, AF7, Fpz) lead in S001. The usual fixed 100 or 150 µV rejection levels would discard most",
          "epochs. Any rejection or robust scaling therefore has to be chosen on training participants inside each",
          "outer fold. These are data-handling observations, not neurophysiological findings.",
          "", "The per-participant details are in `reports/sanity_report.json`."]
    (ROOT / "reports/sanity_summary.md").write_text("\n".join(md) + "\n")
    print("\n".join(md[7:]))


if __name__ == "__main__":
    main()
