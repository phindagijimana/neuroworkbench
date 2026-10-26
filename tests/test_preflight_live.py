"""Live SciCap/SciGuard when siblings import; not_run if missing. Never fake PASS."""

from __future__ import annotations

import ast
from pathlib import Path

from kernel.execute import execute_call_count
from kernel.preflight import (
    _load_scicap_core_module,
    _load_scicap_invoke,
    _load_sciguard_check,
)
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
    if _load_sciguard_check() is not None:
        assert sciguard.get("library") == "sciguard"
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
    invoke_fn, origin = _load_scicap_invoke()
    if invoke_fn is not None:
        assert scicap.get("library") in {"scicap", "scicap_core"}
        assert origin in {"scicap", "scicap_core"}
        assert scicap.get("decision") == "ABSTAIN"
        assert not scicap.get("bound_space")
    else:
        assert scicap.get("library") == "not_run"
        assert scicap.get("decision") == "not_run"
    if _load_sciguard_check() is not None:
        assert sciguard.get("library") == "sciguard"
        assert sciguard.get("status") == "not_run"
        assert sciguard.get("reason") == "sciguard_no_workflow_for_request"
    else:
        assert sciguard.get("library") == "not_run"
        assert sciguard.get("status") == "not_run"
    assert result["receipt"]["qc_did_not_run"]
    assert "input_schema" in result["receipt"]["qc_did_not_run"]
    assert result["receipt"]["dry_run"] is True


def test_load_scicap_core_module_defined_once_no_nameerror() -> None:
    src = (ROOT / "kernel" / "preflight.py").read_text()
    tree = ast.parse(src)
    defs = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef) and node.name == "_load_scicap_core_module"
    ]
    assert defs == ["_load_scicap_core_module"]
    assert callable(_load_scicap_core_module)
    assert _load_scicap_core_module() in {True, False}
