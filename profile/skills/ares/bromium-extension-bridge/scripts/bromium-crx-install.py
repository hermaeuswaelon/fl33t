#!/usr/bin/env python3
"""
Bromium CRX Installer — unpacks CRX3 files into the extensions directory.

CRX3 format:
  [0-3]   Magic    "Cr24"        — 4 bytes
  [4-7]   Version  3 (LE u32)    — 4 bytes
  [8-11]  HdrLen   header len    — 4 bytes LE
  [12+]   Signed header data     — HdrLen bytes
  After   ZIP data

Usage:
  python3 bromium-crx-install.py <crx_path> <extensions_dir>

Writes result to /tmp/bromium-crx-install-result.json:
  {"status":"ok","name":"Extension Name","dir":"ext-dir-name"}
  {"status":"error","error":"message"}

See references/chrome-webstore-install-fix.md for the full pipeline.
"""

import json
import os
import struct
import sys
import tempfile
import zipfile


def extract_crx(crx_path: str, extensions_dir: str) -> dict:
    """Extract a CRX3 file into the extensions directory."""
    if not os.path.isfile(crx_path):
        return {"status": "error", "error": f"File not found: {crx_path}"}

    with open(crx_path, "rb") as f:
        magic = f.read(4)
        if magic != b"Cr24":
            return {"status": "error", "error": f"Invalid CRX magic: {magic!r}"}

        ver = struct.unpack("<I", f.read(4))[0]
        hdr_len = struct.unpack("<I", f.read(4))[0]

        # Skip the signed header data
        f.read(hdr_len)

        # Remaining data is ZIP
        zip_data = f.read()

    # Determine extension directory name from CRX filename
    ext_dir_name = os.path.splitext(os.path.basename(crx_path))[0]
    ext_dir = os.path.join(extensions_dir, ext_dir_name)

    # Remove old version if exists
    if os.path.isdir(ext_dir):
        import shutil
        shutil.rmtree(ext_dir)

    # Extract with temp file (zipfile can't read from bytes in older Python)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    try:
        tmp.write(zip_data)
        tmp.close()

        with zipfile.ZipFile(tmp.name, "r") as zf:
            zf.extractall(ext_dir)
    finally:
        os.unlink(tmp.name)

    # Read extension name from manifest
    manifest_path = os.path.join(ext_dir, "manifest.json")
    display_name = ext_dir_name
    if os.path.isfile(manifest_path):
        with open(manifest_path, "r") as mf:
            manifest = json.load(mf)
            display_name = manifest.get("name", ext_dir_name)

    return {
        "status": "ok",
        "name": display_name,
        "dir": ext_dir_name,
        "path": ext_dir,
    }


def main():
    if len(sys.argv) < 3:
        result = {"status": "error", "error": "Usage: bromium-crx-install.py <crx_path> <extensions_dir>"}
    else:
        crx_path = sys.argv[1]
        extensions_dir = sys.argv[2]
        result = extract_crx(crx_path, extensions_dir)

    # Write result to temp file (Pascal reads this)
    result_path = "/tmp/bromium-crx-install-result.json"
    with open(result_path, "w") as f:
        json.dump(result, f)

    if result["status"] != "ok":
        sys.exit(1)


if __name__ == "__main__":
    main()
