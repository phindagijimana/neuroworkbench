"""S0 pin and fixture contract. No NIfTI in git."""

from __future__ import annotations

from pathlib import Path

import yaml

SHARED = Path(__file__).resolve().parents[1]
INVALID = (
    "missing_space",
    "dk_as_dkt",
    "labels_t1w_on_dwi",
    "digest_swap",
)


def test_pins_parse_and_bytes_flag() -> None:
    pins = yaml.safe_load((SHARED / "pins.yaml").read_text(encoding="utf-8"))
    assert pins["schema_version"] == 0.1 or pins["schema_version"] == "0.1"
    assert pins["dataset"]["bytes_in_git"] is False
    assert pins["dataset"]["accession"] == "ds000003"
    assert pins["dataset"]["doi"] == "10.18112/openneuro.ds000003.v1.0.0"


def test_invalid_fixture_directories_exist() -> None:
    for name in INVALID:
        path = SHARED / "fixtures" / "invalid" / name
        assert path.is_dir(), path
        assert (path / "README.md").is_file()
        assert (path / "instance.json").is_file()


def test_no_nifti_under_shared() -> None:
    forbidden = {".nii", ".nii.gz"}
    hits = [
        p
        for p in SHARED.rglob("*")
        if p.is_file()
        and (
            p.suffix.lower() == ".nii"
            or "".join(p.suffixes[-2:]).lower() == ".nii.gz"
            or p.name.lower().endswith(".nii.gz")
        )
    ]
    assert hits == [], f"NIfTI must not be in git: {hits}"
    del forbidden
