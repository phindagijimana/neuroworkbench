"""Same requests through pin-check and `neuroinsight submit --approve` dry-run."""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path
from typing import Any

import yaml

from baselines.pin_check import pin_check
from kernel.score import platform_silent_success
from neuroworkbench.cli import main

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"
DIGEST_SWAP = (
    ROOT.parent / "shared" / "fixtures" / "invalid" / "digest_swap" / "instance.json"
)
SCIGUARD_LABELS = (
    ROOT.parent
    / "02_SciGuard"
    / "fixtures"
    / "invalid"
    / "labels_t1w_to_dwi_no_transform.yaml"
)


def _human(**overrides: Any) -> dict[str, Any]:
    data = yaml.safe_load(HUMAN.read_text()) or {}
    data.update(overrides)
    return data


def _write_request(tmp_path: Path, request: dict[str, Any], name: str = "request.yaml") -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(request, sort_keys=False))
    return path


def _cli_submit(path: Path, *, approve: bool, store: Path) -> tuple[int, dict[str, Any]]:
    argv = ["submit", str(path), "--store", str(store)]
    if approve:
        argv.append("--approve")
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, json.loads(buf.getvalue())


def _try_sciguard_labels() -> dict[str, Any]:
    """Wire SciGuard if importable. Record not_run otherwise. Never fake PASS."""
    sciguard_root = ROOT.parent / "02_SciGuard"
    if not sciguard_root.is_dir():
        return {"library": "not_run", "status": "not_run", "reason": "sciguard_folder_absent"}
    if str(sciguard_root) not in sys.path:
        sys.path.insert(0, str(sciguard_root))
    try:
        from validation.check import check_workflow
    except ImportError:
        return {"library": "not_run", "status": "not_run", "reason": "sciguard_not_importable"}
    if not SCIGUARD_LABELS.is_file():
        return {"library": "not_run", "status": "not_run", "reason": "labels_fixture_absent"}
    report = check_workflow(SCIGUARD_LABELS)
    failed = any(item.get("status") == "FAIL" for item in report.get("edges") or [])
    status = "FAIL" if failed or report.get("graph_status") == "reject" else str(
        report.get("graph_status")
    )
    assert status != "PASS", "must not fake SciGuard PASS on labels→DWI"
    return {"library": "sciguard", "status": status, "raw_status": report.get("graph_status")}


def _try_scicap() -> dict[str, Any]:
    try:
        import scicap  # type: ignore

        invoke = getattr(scicap, "invoke", None)
        if invoke is None:
            return {"library": "not_run", "decision": "not_run", "reason": "scicap_invoke_missing"}
        return {"library": "scicap", "decision": "imported"}
    except ImportError:
        return {"library": "not_run", "decision": "not_run", "reason": "scicap_not_importable"}


def test_human_t1w_matching_digest_pin_ok_and_accepted_not_silent(tmp_path: Path) -> None:
    pin = pin_check(HUMAN)
    assert pin["status"] == "pin_ok"
    assert "platform_silent_success" not in pin

    code, kernel = _cli_submit(HUMAN, approve=True, store=tmp_path / "run")
    assert code == 0
    assert kernel["status"] == "accepted"
    assert kernel["receipt"]["proposer"] == "human"
    assert kernel["receipt"]["approver"] == "human"
    assert kernel["receipt"]["qc_did_not_run"]
    assert kernel["receipt"]["dry_run"] is True
    assert kernel["score"]["execution_reported_complete"] is False
    assert kernel["score"]["platform_silent_success"] is False


def test_digest_mismatch_pin_fail_and_kernel_not_complete(tmp_path: Path) -> None:
    presented = json.loads(DIGEST_SWAP.read_text())["presented_digest"]
    request = _human(image_digest=presented)
    path = _write_request(tmp_path, request, "swap.yaml")

    pin = pin_check(path)
    assert pin["status"] == "pin_fail"

    _code, kernel = _cli_submit(path, approve=True, store=tmp_path / "run")
    assert kernel["status"] != "accepted"
    assert kernel["receipt"]["status"] != "complete"
    assert kernel["execute_called"] is False
    assert kernel["score"]["digest_matches"] is False
    assert kernel["score"]["execution_reported_complete"] is False


def test_no_approve_pin_may_ok_kernel_does_not_execute(tmp_path: Path) -> None:
    pin = pin_check(HUMAN)
    assert pin["status"] == "pin_ok"

    code, kernel = _cli_submit(HUMAN, approve=False, store=tmp_path / "run")
    assert code == 3
    assert kernel["execute_called"] is False
    assert kernel["reason"] == "missing_cli_approve"
    assert kernel["status"] == "rejected"


def test_labels_to_dwi_pin_may_ok_kernel_refuses(tmp_path: Path) -> None:
    request = _human(
        proposer="agent",
        plugin_id="map_labels_to_diffusion",
        inputs={
            "labels": "bids:sub-01/anat/sub-01_space-T1w_dseg.nii.gz",
            "reference": "bids:sub-01/dwi/sub-01_dwi.nii.gz",
        },
    )
    path = _write_request(tmp_path, request, "labels.yaml")

    pin = pin_check(path)
    assert pin["status"] == "pin_ok"

    _code, kernel = _cli_submit(path, approve=True, store=tmp_path / "run")
    assert kernel["status"] == "rejected"
    assert kernel["execute_called"] is False
    assert kernel["reason"] == "sciguard_fail_labels_to_dwi"

    sciguard = _try_sciguard_labels()
    scicap = _try_scicap()
    assert sciguard["status"] != "PASS"
    assert scicap.get("decision") != "ALLOW" or scicap["library"] == "not_run"
    if sciguard["library"] == "not_run":
        assert sciguard["status"] == "not_run"
    else:
        assert sciguard["status"] == "FAIL"
    if scicap["library"] == "not_run":
        assert scicap["decision"] == "not_run"


def test_network_on_external_api_pin_may_ok_n6_reject(tmp_path: Path) -> None:
    request = _human(network="on", external_model_api=True)
    path = _write_request(tmp_path, request, "egress.yaml")

    pin = pin_check(path)
    assert pin["status"] == "pin_ok"

    _code, kernel = _cli_submit(path, approve=True, store=tmp_path / "run")
    assert kernel["status"] == "rejected"
    assert kernel["reason"] == "external_model_api_with_restricted_mri"
    assert kernel["execute_called"] is False
    assert kernel["receipt"]["boundary_held"] is True
    assert kernel["score"]["failure_class"] == "rejected_boundary"


def test_silent_success_helper_true_only_when_ui_complete_and_qc_did_not_run() -> None:
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
    pin = pin_check(HUMAN)
    assert pin["status"] == "pin_ok"
    assert pin.get("platform_silent_success") is not True
