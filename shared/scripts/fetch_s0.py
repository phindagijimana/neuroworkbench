#!/usr/bin/env python3.11
"""Print the S0 OpenNeuro URL and destination. Do not download unless flagged.

bytes_in_git stays false. Tests call this script without
``--i-accept-public-data`` and assert no download.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

import yaml

SHARED = Path(__file__).resolve().parents[1]
MANIFEST = SHARED / "data" / "manifests" / "ds000003.yaml"
PINS = SHARED / "pins.yaml"
DEFAULT_DEST = SHARED / "data" / "external" / "ds000003"
ACCEPT_FLAG = "--i-accept-public-data"


def load_manifest(path: Path = MANIFEST) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"manifest must be a mapping: {path}")
    return data


def load_pins(path: Path = PINS) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"pins must be a mapping: {path}")
    return data


def openneuro_url(manifest: dict[str, Any]) -> str:
    return str(manifest.get("url") or "https://openneuro.org/datasets/ds000003")


def listed_files(manifest: dict[str, Any]) -> list[str]:
    files = manifest.get("files") or []
    paths: list[str] = []
    for item in files:
        if isinstance(item, dict) and item.get("path"):
            paths.append(str(item["path"]))
    return paths


def fetch_public_bytes(manifest: dict[str, Any], dest: Path) -> None:
    """Download listed public files. Called only after the accept flag."""
    import urllib.request

    dest.mkdir(parents=True, exist_ok=True)
    github = str(manifest.get("github") or "").rstrip("/")
    if not github:
        github = "https://github.com/OpenNeuroDatasets/ds000003"
    for rel in listed_files(manifest):
        url = f"{github}/raw/master/{rel}"
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, target)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch the S0 OpenNeuro T1w snapshot (opt-in only).",
    )
    parser.add_argument(
        ACCEPT_FLAG,
        dest="accept_public_data",
        action="store_true",
        help="Required to download public OpenNeuro bytes. Tests must omit this.",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DEST,
        help="Destination directory (NIfTI stays outside git).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=MANIFEST,
        help="Path to the ds000003 manifest.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    manifest = load_manifest(args.manifest)
    pins = load_pins()
    dest = Path(args.dest)
    url = openneuro_url(manifest)
    bytes_flag = bool(manifest.get("bytes_in_git", True))
    pins_bytes = bool((pins.get("dataset") or {}).get("bytes_in_git", True))

    print(f"url: {url}")
    print(f"destination: {dest}")
    print("bytes_in_git: false")

    if bytes_flag or pins_bytes:
        print("refusing: bytes_in_git must stay false", file=sys.stderr)
        return 2

    if not args.accept_public_data:
        print(
            f"download refused: pass {ACCEPT_FLAG} to fetch public OpenNeuro bytes",
            file=sys.stderr,
        )
        return 2

    fetch_public_bytes(manifest, dest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
