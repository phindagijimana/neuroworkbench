"""Point a dry-run at ds000003 when those bytes already exist. Never download."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from kernel.external import (
    EXTERNAL_TOKEN,
    _is_git_annex_pointer,
    _is_real_nifti_bytes,
    external_s0_status,
    find_ds000003_t1w,
    request_for_external_s0,
)
from kernel.submit import submit
from neuroworkbench.cli import main

ROOT = Path(__file__).resolve().parents[1]
DS000003 = ROOT / "examples" / "requests" / "t1w_ds000003.yaml"
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"


def test_external_s0_does_not_download_or_commit_nii() -> None:
    status = external_s0_status()
    assert status["bytes_in_git"] is False
    assert status["download_in_pytest"] is False
    assert status["accession"] == "ds000003"
    assert status["present"] is (find_ds000003_t1w() is not None)
    nii = list(ROOT.rglob("*.nii")) + list(ROOT.rglob("*.nii.gz"))
    assert nii == []


def test_ds000003_token_dry_run(tmp_path: Path) -> None:
    result = submit(DS000003, approve=True, store=tmp_path)
    assert result["status"] == "accepted"
    assert result["receipt"]["dry_run"] is True
    assert result["score"]["execution_reported_complete"] is False
    assert result["score"]["platform_silent_success"] is False
    status = result["external_s0"]
    assert status["present"] is (find_ds000003_t1w() is not None)
    assert status["bytes_in_git"] is False
    t1w_hash = result["receipt"]["input_hashes"]["t1w"]
    if status["present"]:
        assert result["receipt"]["bids_identities"]["t1w"] == status["path"]
        assert t1w_hash.startswith("sha256:")
        assert t1w_hash != "bytes_unavailable"
        assert "ds000003" in (status["path"] or "")
    else:
        assert result["receipt"]["bids_identities"]["t1w"] == EXTERNAL_TOKEN
        assert t1w_hash == "bytes_unavailable"
    scicap = result["preflight"]["scicap"]
    sciguard = result["preflight"]["sciguard"]
    assert scicap.get("decision") != "PASS"
    assert sciguard.get("status") != "PASS"


def test_cli_external_s0_flag_does_not_invent_bytes(tmp_path: Path) -> None:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "submit",
                str(HUMAN),
                "--approve",
                "--external-s0",
                "--store",
                str(tmp_path),
            ]
        )
    payload = json.loads(buf.getvalue())
    assert code == 0
    assert payload["status"] == "accepted"
    assert payload["receipt"]["dry_run"] is True
    status = payload["external_s0"]
    assert status["download_in_pytest"] is False
    if status["present"]:
        assert payload["receipt"]["input_hashes"]["t1w"].startswith("sha256:")
    else:
        assert payload["receipt"]["input_hashes"]["t1w"] == "bytes_unavailable"


def test_request_helper_rewrites_only_when_present() -> None:
    job = request_for_external_s0()
    status = job["external_s0"]
    if status["present"]:
        assert job["inputs"]["t1w"] == status["path"]
    else:
        assert job["inputs"]["t1w"] == EXTERNAL_TOKEN


def test_git_annex_pointer_is_absent(tmp_path: Path) -> None:
    pointer = tmp_path / "sub-01_T1w.nii.gz"
    pointer.write_text(
        "../.git/annex/objects/aa/bb/SHA256E-s140--deadbeef/SHA256E-s140--deadbeef\n"
    )
    assert pointer.stat().st_size < 1024
    assert pointer.read_bytes().startswith(b"..")
    assert _is_git_annex_pointer(pointer) is True
    assert _is_real_nifti_bytes(pointer) is False


def test_preferred_annex_pointer_does_not_hide_real_gzip(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "ds000003"
    preferred = root / "sub-01" / "anat" / "sub-01_T1w.nii.gz"
    preferred.parent.mkdir(parents=True)
    preferred.write_text("../.git/annex/objects/aa/bb/SHA256E-s1--dead/SHA256E-s1--dead\n")
    real = root / "sub-01" / "anat" / "alt_T1w.nii.gz"
    # Magic + size only; not a committed NIfTI. Must stay ≥ 1024 bytes.
    real.write_bytes(b"\x1f\x8b" + bytes(range(256)) * 8)
    monkeypatch.setattr("kernel.external.DS000003_ROOT", root)
    found = find_ds000003_t1w()
    assert found == real.resolve()
    assert _is_git_annex_pointer(preferred) is True
    assert _is_real_nifti_bytes(real) is True


def test_cli_submit_t1w_ds000003_dry_run_fail_closed(tmp_path: Path) -> None:
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            [
                "submit",
                str(DS000003),
                "--approve",
                "--store",
                str(tmp_path),
            ]
        )
    payload = json.loads(buf.getvalue())
    assert code == 0
    assert payload["status"] == "accepted"
    receipt = payload["receipt"]
    assert receipt["dry_run"] is True
    assert receipt["qc_did_not_run"]
    assert "input_schema" in receipt["qc_did_not_run"]
    assert receipt["qc_passed"] == []
    assert payload["score"]["execution_reported_complete"] is False
    assert payload["score"]["platform_silent_success"] is False
    assert payload["hardware"]["fastsurfer_gpu"] is False
    assert payload["hardware"]["image_pulled"] is False
    status = payload["external_s0"]
    assert status["bytes_in_git"] is False
    assert status["download_in_pytest"] is False
    scicap = (payload.get("preflight") or {}).get("scicap") or {}
    sciguard = (payload.get("preflight") or {}).get("sciguard") or {}
    assert scicap.get("decision") != "PASS"
    assert sciguard.get("status") != "PASS"
    if status["present"]:
        assert receipt["bids_identities"]["t1w"] == status["path"]
        assert "ds000003" in (status["path"] or "")
        assert receipt["input_hashes"]["t1w"].startswith("sha256:")
        assert receipt["input_hashes"]["t1w"] != "bytes_unavailable"
        assert Path(status["path"]).read_bytes()[:2] == b"\x1f\x8b"
    else:
        assert receipt["bids_identities"]["t1w"] == EXTERNAL_TOKEN
        assert receipt["input_hashes"]["t1w"] == "bytes_unavailable"
