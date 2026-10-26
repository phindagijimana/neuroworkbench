"""Live SciCap/SciGuard on labels→DWI, or not_run. Never fake PASS."""

from __future__ import annotations

from pathlib import Path

from kernel.execute import execute_call_count
from kernel.request import parse_request
from kernel.submit import submit

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"


def _labels_request() -> dict:
    request = parse_request(HUMAN).raw
    request["proposer"] = "agent"
    request["plugin_id"] = "map_labels_to_diffusion"
    request["inputs"] = {
        "labels": "bids:sub-01/anat/sub-01_space-T1w_dseg.nii.gz",
        "reference": "bids:sub-01/dwi/sub-01_dwi.nii.gz",
    }
    return request


def test_labels_to_dwi_live_sciguard_fail_or_not_run(tmp_path: Path) -> None:
    result = submit(_labels_request(), approve=True, store=tmp_path)
    assert result["status"] == "rejected"
    assert result["execute_called"] is False
    assert execute_call_count() == 0
    assert result["reason"] == "sciguard_fail_labels_to_dwi"

    sciguard = result["preflight"]["sciguard"]
    scicap = result["preflight"]["scicap"]
    assert sciguard.get("status") in {"FAIL", "not_run"}
    assert sciguard.get("status") != "PASS"
    assert scicap.get("decision") != "PASS"
    assert scicap.get("decision") != "ALLOW"
    if sciguard.get("library") == "sciguard":
        assert sciguard["status"] == "FAIL"
    if sciguard.get("library") == "not_run":
        assert sciguard["status"] in {"FAIL", "not_run"}
    if scicap.get("library") == "not_run":
        assert scicap.get("decision") == "not_run"


def test_human_t1w_does_not_invent_library_pass(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=True, store=tmp_path)
    scicap = result["preflight"]["scicap"]
    sciguard = result["preflight"]["sciguard"]
    assert scicap.get("decision") != "PASS"
    assert sciguard.get("status") != "PASS"
