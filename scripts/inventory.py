"""P4.01: record the structure of the downloaded subset from the EDF files themselves
(channels, sampling rate, durations, annotation counts). Writes reports/data_inventory.json."""
import json
from collections import Counter
from pathlib import Path

import mne

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/subset.json").read_text())


def main():
    mne.set_log_level("ERROR")
    recs, chsets = [], Counter()
    for s in CFG["subject_ids"]:
        for r in CFG["runs"]:
            raw = mne.io.read_raw_edf(ROOT / f"data/raw/S{s:03d}/S{s:03d}R{r:02d}.edf", preload=False)
            ann = Counter(raw.annotations.description)
            chsets[tuple(raw.ch_names)] += 1
            recs.append({"subject": s, "run": r, "n_channels": len(raw.ch_names), "sfreq": float(raw.info["sfreq"]),
                         "n_samples": int(raw.n_times), "duration_s": round(int(raw.n_times) / raw.info["sfreq"], 3),
                         "annotations": dict(sorted(ann.items())),
                         "annotation_durations_s": sorted({round(float(d), 3) for d in raw.annotations.duration})})
    names = list(chsets.most_common(1)[0][0])
    out = {"dataset": CFG["dataset"], "doi": CFG["doi"], "n_recordings": len(recs),
           "n_subjects": len({x["subject"] for x in recs}), "runs": CFG["runs"],
           "distinct_channel_sets": len(chsets), "channel_names": names,
           "sfreq_values": sorted({x["sfreq"] for x in recs}),
           "duration_s_range": [min(x["duration_s"] for x in recs), max(x["duration_s"] for x in recs)],
           "annotation_totals": dict(sorted(sum((Counter(x["annotations"]) for x in recs), Counter()).items())),
           "recordings": recs}
    (ROOT / "reports").mkdir(exist_ok=True)
    (ROOT / "reports/data_inventory.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k not in ("recordings", "channel_names")})


if __name__ == "__main__":
    main()
