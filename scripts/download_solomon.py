"""Verify and optionally fetch the Solomon RC101 benchmark text file.

Checks that data/solomon/RC101.txt exists and attempts to download it
from known mirrors if missing.

Usage:
    python scripts/download_solomon.py
"""

import sys
import urllib.request
from pathlib import Path

RC101_URLS = [
    "https://people.idsia.ch/~luca/macs-vrptw/problems/rc101.txt",
    "https://raw.githubusercontent.com/nicholas-leonard/solomon-vrptw/master/RC101.txt",
]

DEST_DIR = Path("data/solomon")
DEST_FILE = DEST_DIR / "RC101.txt"


def main() -> None:
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    if DEST_FILE.exists():
        print(f"RC101 already exists at {DEST_FILE}")
        return

    for url in RC101_URLS:
        try:
            with urllib.request.urlopen(url, timeout=30) as resp:
                DEST_FILE.write_text(resp.read().decode("utf-8"), encoding="utf-8")
                print(f"RC101 downloaded to {DEST_FILE}")
                return
        except Exception:
            continue

    print(
        "ERROR: Could not download RC101. Place the file manually at "
        f"{DEST_FILE}.",
        file=sys.stderr,
    )
    sys.exit(1)


if __name__ == "__main__":
    main()
