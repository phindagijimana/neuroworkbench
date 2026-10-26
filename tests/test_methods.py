"""Wave 2 methods layer: N1–N6 residuals vs the public pin tool. No N7."""

from __future__ import annotations

from pathlib import Path

from kernel.execute import AGENT_MAY_CALL_EXECUTOR
from kernel.receipt import RECEIPT_KEYS
from kernel.request import parse_request
from kernel.score import compute_score, platform_silent_success
from kernel.submit import submit

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"
METHODS = ROOT / "docs" / "NeuroInsight_Methods.md"
TRACE = ROOT / "docs" / "METHODS_TRACE.md"


def test_methods_trace_cites_n1_to_n6_and_literature() -> None:
    text = TRACE.read_text()
    for method in ("N1", "N2", "N3", "N4", "N5", "N6"):
        assert method in text
    assert "| N7 |" not in text
    assert "### N7" not in text
    for cite in ("Neurodesk", "BABS", "NeuroClaw", "CyberNeuro", "NeuroPilot"):
        assert cite in text
    assert "not first platform" in text.lower() or "Not first platform" in text


def test_locked_methods_file_not_replaced() -> None:
    text = METHODS.read_text()
    assert "### N1. Dual-interface invariant" in text
    assert "### N6. Fail-closed data boundary" in text
    assert "N7" not in text


def test_n1_agent_cannot_call_execute() -> None:
    assert AGENT_MAY_CALL_EXECUTOR is False


def test_n2_silent_success_is_ui_complete_and_hidden_failure() -> None:
    # CyberNeuro-style receipt honesty: complete UI + QC-not-run is silent success.
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
    assert (
        platform_silent_success(
            execution_reported_complete=False,
            required_qc_passed=False,
            digest_matches=True,
            boundary_held=True,
            required_stages_ran=False,
        )
        is False
    )


def test_n3_not_in_v0_comparison_unknown_or_not_paired(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=True, store=tmp_path)
    assert result["score"]["environment_status"] in {"not_paired", "comparison_unknown"}
    assert not (ROOT / "execution" / "hpc").exists() or not any(
        (ROOT / "execution" / "hpc").glob("*.py")
    )


def test_n4_receipt_answers_approve_qc_not_run_boundary(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=True, store=tmp_path)
    receipt = result["receipt"]
    for key in RECEIPT_KEYS:
        assert key in receipt
    assert receipt["approver"] == "human"
    assert receipt["qc_did_not_run"]
    assert receipt["boundary_held"] is True
    crate = Path(result["receipt_path"]).parent / "ro-crate-metadata.json"
    assert crate.is_file()
    import json

    payload = json.loads(crate.read_text())
    assert payload["@context"] == "https://w3id.org/ro/crate/1.1/context"
    assert any(
        node.get("@type") == "Dataset" or "Dataset" in (node.get("@type") or [])
        for node in payload["@graph"]
    )


def test_n5_not_in_v0_no_setup_burden_scorer() -> None:
    assert not (ROOT / "kernel" / "setup_burden.py").exists()
    text = TRACE.read_text()
    assert "N5" in text
    assert "Not in v0" in text


def test_n6_pin_check_does_not_enforce_boundary() -> None:
    from baselines.pin_check import pin_check

    request = parse_request(HUMAN).raw
    request["network"] = "on"
    request["external_model_api"] = True
    pin = pin_check(request)
    assert pin["status"] == "pin_ok"
    assert "boundary_held" not in pin
