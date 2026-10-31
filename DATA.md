# Data: PhysioNet EEG Motor Movement/Imagery Dataset (v1.0.0)

## Source, access and licence

| | |
|---|---|
| Dataset | EEG Motor Movement/Imagery Dataset, version 1.0.0, published 9 Sep 2009 |
| Contributor | Gerwin Schalk and colleagues, BCI R&D Program, Wadsworth Center, New York State Department of Health (recorded with BCI2000) |
| DOI | [10.13026/C28G6P](https://doi.org/10.13026/C28G6P) |
| Page | https://physionet.org/content/eegmmidb/1.0.0/ |
| Access | Open access: "Anyone can access the files, as long as they conform to the terms of the specified license." No registration or data use agreement is needed. |
| Licence | [Open Data Commons Attribution License v1.0 (ODC-By 1.0)](https://opendatacommons.org/licenses/by/1-0/). Public use and derived results are allowed if the dataset is attributed. |
| Redistribution here | None. Raw files stay in `data/raw/`, which is git-ignored. This repository commits only code, the subset definition, the SHA-256 list of the subset files, and derived summary statistics. |

The licence and access terms were read from the dataset page on 31 Oct 2026.

### Citation

Cite the dataset:

> Schalk, G. (2009). *EEG Motor Movement/Imagery Dataset* (version 1.0.0). PhysioNet. https://doi.org/10.13026/C28G6P

The dataset page also asks users to cite PhysioNet. The platform citation it currently shows is:

> Pollard, T., Moody, B. E., Lehman, L. H., Gow, B. J., Fernandes, C., Xie, C., Johnson, A., Mark, R. G., & Heldt, T. (2026). PhysioNet as a global platform for biomedical research. *Nature Health*, 1(8), 792–795. https://doi.org/10.1038/s44360-026-00096-z

The recording system is described in Schalk, G., McFarland, D. J., Hinterberger, T., Birbaumer, N., & Wolpaw, J. R. (2004). BCI2000: A general-purpose brain-computer interface (BCI) system. *IEEE Transactions on Biomedical Engineering*, 51(6), 1034–1043.

## What the full dataset contains (from the dataset page)

- 109 participants. Each did 14 runs: one minute of eyes-open baseline, one minute of
  eyes-closed baseline, then three repetitions of four two-minute task types (real or
  imagined, unilateral fists or bilateral fists/feet).
- 64 EEG channels on the international 10-10 system. Nz, F9, F10, FT9, FT10, A1, A2, TP9,
  TP10, P9 and P10 are excluded. The sampling rate is 160 Hz. The files are EDF+ with an
  annotation channel.
- Event codes: `T0` = rest. In the unilateral runs, `T1` and `T2` = onset of left-fist and
  right-fist movement or imagery. In the bilateral runs, `T1` and `T2` mean both fists and
  both feet. **The meaning of `T1` and `T2` depends on the run number.**
- The page does not give demographics, handedness, recording dates or the number of
  recording days. This project assumes nothing about them. Each participant is treated as
  one group of recordings and is never split across training and test.

## Subset used here (fixed before download)

The subset was fixed in [config/subset.json](config/subset.json) before any file was
fetched: **participants S001–S050** (the first 50 IDs, with no selection by data quality)
and **runs 4, 8 and 12** (imagined opening and closing of the left or right fist). In these
runs, `T0` = rest, `T1` = imagined left fist and `T2` = imagined right fist. That gives 150
EDF files totalling 384,539,520 bytes. `scripts/fetch_data.py` downloads them and checks
each one against PhysioNet's `SHA256SUMS.txt`. The 150 expected hashes are also in
[config/subset_sha256.txt](config/subset_sha256.txt). physionet.org kept resetting TLS
connections from the build machine, so the script downloads from PhysioNet's official
open-data mirror on AWS (`physionet-open`). The checksums still come from physionet.org.

## Measured structure of the subset

These figures come from `scripts/inventory.py` and are saved in
[reports/data_inventory.json](reports/data_inventory.json).

| Property | Measured |
|---|---|
| Recordings | 150 (50 participants × 3 runs) |
| Channels | 64 EEG in every file, one identical channel list (EDF labels are padded with dots, e.g. `Fc5.`) |
| Sampling rate | 160.0 Hz in every file |
| Run length | 123.0–125.0 s |
| Annotations | 2250 `T0` (rest), 1134 `T1` (left-fist imagery), 1116 `T2` (right-fist imagery) |
| Per run | 15 rest + 15 imagery cues (8/7 or 7/8 left/right), each about 4.0–4.3 s long |
| Per participant | 45 imagery trials (about 22–23 per class) |

## Evaluation unit

The participant is the unit of evaluation. The outer folds are frozen in
`splits/FROZEN_participant_folds.json`. A participant's three runs always fall in the
same fold. Model selection may use only training-fold participants.
