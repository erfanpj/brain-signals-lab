"""Download the fixed subset (config/subset.json) from PhysioNet (or its official AWS open-data mirror) and verify each file
against PhysioNet's published SHA256SUMS.txt. Files go to data/raw/ (git-ignored).
The data is not redistributed by this repository."""
import hashlib, json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config/subset.json").read_text())
RAW = ROOT / "data/raw"
SUMS = ROOT / "data/SHA256SUMS.txt"


def get(url, tries=6):
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r:
                return r.read()
        except Exception as e:  # PhysioNet TLS resets happen; back off and retry
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def main():
    if not SUMS.exists():
        SUMS.write_bytes(get(CFG["base_url"] + "SHA256SUMS.txt"))
    sums = dict(reversed(l.split()) for l in SUMS.read_text().splitlines() if l.strip())
    total = fetched = 0
    for s in CFG["subject_ids"]:
        for r in CFG["runs"]:
            rel = f"S{s:03d}/S{s:03d}R{r:02d}.edf"
            out = RAW / rel
            if not (out.exists() and hashlib.sha256(out.read_bytes()).hexdigest() == sums[rel]):
                data = get(CFG.get("mirror_url", CFG["base_url"]) + rel)
                if hashlib.sha256(data).hexdigest() != sums[rel]:
                    sys.exit(f"checksum mismatch: {rel}")
                out.parent.mkdir(parents=True, exist_ok=True)
                out.write_bytes(data)
                fetched += len(data)
            total += out.stat().st_size
    print(f"files={len(CFG['subject_ids']) * len(CFG['runs'])} verified_bytes={total} fetched_this_run={fetched}")


if __name__ == "__main__":
    main()
