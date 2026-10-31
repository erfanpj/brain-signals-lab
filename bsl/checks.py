"""Label-free signal checks. These describe the data; they reject nothing and never look at
model results. Amplitudes are in microvolts (µV)."""
import numpy as np

LABELS = {"T1": "left_fist_imagery", "T2": "right_fist_imagery"}


def clean_name(ch: str) -> str:
    """EDF labels look like 'Fc5.' or 'C5..' -> 'FC5', 'C5' (10-10 names, as in MNE's eegbci)."""
    n = ch.strip(".").upper()
    return n.replace("Z", "z").replace("FP", "Fp")


def flat_channels(data_uv: np.ndarray, thresh_uv: float = 0.5) -> list[int]:
    """Indices of channels whose whole-run standard deviation is below thresh_uv."""
    return [int(i) for i in np.flatnonzero(data_uv.std(axis=1) < thresh_uv)]


def peak_to_peak(epochs_uv: np.ndarray) -> np.ndarray:
    """Per-epoch maximum over channels of the peak-to-peak amplitude (n_epochs,)."""
    return np.ptp(epochs_uv, axis=2).max(axis=1)


def robust_z(x: np.ndarray) -> np.ndarray:
    med = np.median(x)
    mad = np.median(np.abs(x - med)) * 1.4826
    return (x - med) / mad if mad > 0 else np.zeros_like(x, dtype=float)


def line_noise_ratio(freqs: np.ndarray, psd: np.ndarray, f0: float = 60.0) -> np.ndarray:
    """Per-channel power at the mains frequency divided by the median power at 50-70 Hz
    excluding 58-62 Hz. Recorded in the US, so mains is 60 Hz."""
    peak = psd[:, np.argmin(np.abs(freqs - f0))]
    side = (freqs >= f0 - 10) & (freqs <= f0 + 10) & (np.abs(freqs - f0) > 2)
    return peak / np.median(psd[:, side], axis=1)


def fold_of(folds: dict) -> dict:
    """participant -> outer fold; raises if any participant is in more than one fold."""
    out = {}
    for k, members in folds.items():
        for p in members:
            if p in out:
                raise ValueError(f"participant {p} in folds {out[p]} and {k}")
            out[p] = int(k)
    return out
