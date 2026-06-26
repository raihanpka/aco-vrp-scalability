"""
Download Solomon VRPTW benchmark instances from SINTEF.

Downloads the 100-customer instance set (solomon-100.zip) and extracts
all .txt files into data/solomon/. Safe to re-run: skips files that
already exist unless --force is passed.

Usage:
    uv run python scripts/download_solomon.py
    uv run python scripts/download_solomon.py --force
"""

import argparse
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

SOLOMON_ZIP_URL = "https://www.sintef.no/globalassets/project/top/vrptw/solomon/solomon-100.zip"
DEST_DIR = Path("data/solomon")


def download_solomon(force: bool = False) -> None:
    DEST_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {SOLOMON_ZIP_URL} ...")
    try:
        req = urllib.request.Request(
            SOLOMON_ZIP_URL,
            headers={"User-Agent": "Mozilla/5.0 (research-download)"},
        )
        """
        Header User-Agent ditambahkan karena server SINTEF memblokir request yang tidak terlihat seperti browser. 
        Kalau download gagal, script langsung berhenti dengan pesan error.
        """

        with urllib.request.urlopen(req, timeout=30) as response:
            zip_bytes = response.read()
        """
        ZIP dibuka di memory (tidak disimpan ke disk dulu), lalu semua file .txt di dalamnya diekstrak ke data/solomon/. 
        Kalau file sudah ada dan tidak pakai --force, file tersebut dilewati (skip) supaya tidak menimpa yang sudah ada.
        """
    except Exception as exc:
        print(f"ERROR: Download failed: {exc}", file=sys.stderr)
        sys.exit(1)

    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        txt_members = [m for m in zf.namelist() if m.lower().endswith(".txt")]
        if not txt_members:
            print("ERROR: No .txt files found in archive.", file=sys.stderr)
            sys.exit(1)
        """
        zipfile.ZipFile(io.BytesIO(zip_bytes)) membuka zip file dari bytes
        .namelist() mendapatkan daftar semua file dalam zip
        m.lower().endswith(".txt") memfilter hanya file .txt
        """

        extracted = 0
        skipped = 0
        for member in txt_members:
            filename = Path(member).name
            dest = DEST_DIR / filename
            if dest.exists() and not force:
                skipped += 1
                continue
            dest.write_bytes(zf.read(member))
            extracted += 1

    print(f"Extracted {extracted} file(s) to {DEST_DIR}/  (skipped {skipped} existing)")

    rc101 = DEST_DIR / "RC101.txt"
    if not rc101.exists():
        print("WARNING: RC101.txt not found in archive.", file=sys.stderr)
        sys.exit(1)

    text = rc101.read_text().splitlines() 
    in_customer_section = False
    customer_rows = []
    for line in text:
        if line.strip() == "CUSTOMER":
            in_customer_section = True
            continue
        if in_customer_section:
            parts = line.split()
            if len(parts) >= 7 and parts[0].isdigit() and int(parts[0]) > 0:
                customer_rows.append(line)
    print(f"Verified RC101.txt: {len(customer_rows)} customers found (expected 100).")
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download Solomon VRPTW benchmark instances.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()
    download_solomon(force=args.force)
    