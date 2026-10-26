"""fetch_s0.py prints URL and destination. No download without the accept flag."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

SHARED = Path(__file__).resolve().parents[1]
SCRIPT = SHARED / "scripts" / "fetch_s0.py"
MANIFEST = SHARED / "data" / "manifests" / "ds000003.yaml"
PINS = SHARED / "pins.yaml"


def _load_fetch_s0():
    spec = importlib.util.spec_from_file_location("fetch_s0", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bytes_in_git_stays_false() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    pins = yaml.safe_load(PINS.read_text(encoding="utf-8"))
    assert manifest["bytes_in_git"] is False
    assert pins["dataset"]["bytes_in_git"] is False


def test_fetch_s0_without_flag_exits_2_and_does_not_download(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    dest = tmp_path / "ds000003"
    fetch_s0 = _load_fetch_s0()

    def boom(*_args, **_kwargs):
        raise AssertionError("fetch_public_bytes must not run without the flag")

    monkeypatch.setattr(fetch_s0, "fetch_public_bytes", boom)
    code = fetch_s0.main(["--dest", str(dest)])
    assert code == 2
    assert not dest.exists()


def test_fetch_s0_subprocess_no_download(tmp_path: Path) -> None:
    dest = tmp_path / "ds000003"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--dest", str(dest)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "openneuro.org" in proc.stdout.lower()
    assert str(dest) in proc.stdout
    assert "bytes_in_git: false" in proc.stdout
    assert "--i-accept-public-data" in proc.stderr
    assert not dest.exists()
    nii_hits = list(tmp_path.rglob("*.nii")) + list(tmp_path.rglob("*.nii.gz"))
    assert nii_hits == []


def test_fetch_s0_source_does_not_download_before_flag() -> None:
    text = SCRIPT.read_text(encoding="utf-8")
    assert "--i-accept-public-data" in text
    assert "urlretrieve" in text
    accept_idx = text.index("if not args.accept_public_data")
    fetch_idx = text.index("fetch_public_bytes(manifest, dest)")
    assert accept_idx < fetch_idx
