"""Kernel go-gate: no approve → no execute; digest mismatch → not complete."""

from __future__ import annotations

from pathlib import Path

from kernel.execute import execute_call_count
from kernel.request import parse_request
from kernel.score import platform_silent_success
from kernel.submit import submit

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"


def _human(**overrides):
    request = parse_request(HUMAN).raw
    request.update(overrides)
    return request


def test_missing_approve_does_not_execute(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=False, store=tmp_path)
    assert result["status"] == "rejected"
    assert result["reason"] == "missing_cli_approve"
    assert result["execute_called"] is False
    assert execute_call_count() == 0
    assert result["receipt"]["qc_did_not_run"]


def test_digest_mismatch_is_not_complete(tmp_path: Path) -> None:
    request = _human(image_digest="sha256:DIGEST_SWAP")
    result = submit(request, approve=True, store=tmp_path)
    assert result["execute_called"] is False
    assert execute_call_count() == 0
    assert result["status"] == "failed"
    assert result["score"]["digest_matches"] is False
    assert result["score"]["execution_reported_complete"] is False
    assert result["score"]["platform_silent_success"] is False
    assert result["receipt"]["status"] != "complete"


def test_human_approved_dry_run_receipt(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=True, store=tmp_path)
    assert result["status"] == "accepted"
    assert result["execute_called"] is True
    receipt = result["receipt"]
    assert receipt["proposer"] == "human"
    assert receipt["approver"] == "human"
    assert receipt["qc_did_not_run"]
    assert "input_schema" in receipt["qc_did_not_run"]
    assert receipt["boundary_held"] is True
    assert receipt["input_hashes"]["t1w"] == "bytes_unavailable"
    assert receipt["dry_run"] is True
    assert result["score"]["execution_reported_complete"] is False
    scicap = result["preflight"]["scicap"]
    sciguard = result["preflight"]["sciguard"]
    assert scicap.get("library") in {"scicap", "scicap_core", "not_run"}
    assert sciguard.get("library") in {"sciguard", "not_run"}
    assert scicap.get("decision") != "PASS"
    assert sciguard.get("status") != "PASS"
    if scicap.get("library") in {"scicap", "scicap_core"}:
        # T1w request does not declare space; live SciCap must ABSTAIN, not invent ALLOW.
        assert scicap.get("decision") == "ABSTAIN"
        assert not scicap.get("bound_space")


def test_labels_to_dwi_refused_no_execute(tmp_path: Path) -> None:
    request = _human(
        proposer="agent",
        plugin_id="map_labels_to_diffusion",
        inputs={
            "labels": "bids:sub-01/anat/sub-01_space-T1w_dseg.nii.gz",
            "reference": "bids:sub-01/dwi/sub-01_dwi.nii.gz",
        },
    )
    result = submit(request, approve=True, store=tmp_path)
    assert result["status"] == "rejected"
    assert result["execute_called"] is False
    assert execute_call_count() == 0
    assert result["reason"] == "sciguard_fail_labels_to_dwi"
    sciguard = result["preflight"]["sciguard"]
    assert sciguard["status"] != "PASS"
    assert sciguard["status"] in {"FAIL", "not_run"}
    if sciguard["library"] == "sciguard":
        assert sciguard["status"] == "FAIL"
    if sciguard["library"] == "not_run":
        assert sciguard["status"] == "FAIL"


def test_silent_success_when_ui_complete_but_qc_not_run() -> None:
    assert (
        platform_silent_success(
            execution_reported_complete=True,
            required_qc_passed=False,
            digest_matches=True,
            boundary_held=True,
            required_stages_ran=False,
        )
        is True
    )


def test_honest_dry_run_is_not_silent_success(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=True, store=tmp_path)
    assert result["score"]["platform_silent_success"] is False
    assert result["qc"]["required_qc_passed"] is False
