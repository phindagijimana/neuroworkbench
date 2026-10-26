"""N6: external model API with images or network:on is REJECT."""

from __future__ import annotations

from pathlib import Path

import pytest

from kernel.boundary import evaluate_boundary
from kernel.execute import execute_call_count
from kernel.request import parse_request
from kernel.submit import submit

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"


def test_external_api_and_network_on_rejected(tmp_path: Path) -> None:
    request = parse_request(HUMAN).raw
    request["network"] = "on"
    request["external_model_api"] = True
    result = submit(request, approve=True, store=tmp_path)
    assert result["status"] == "rejected"
    assert result["reason"] == "external_model_api_with_restricted_mri"
    assert result["execute_called"] is False
    assert execute_call_count() == 0
    assert result["receipt"]["boundary_held"] is True
    assert result["score"]["failure_class"] == "rejected_boundary"


def test_external_api_with_image_path_rejected() -> None:
    request = parse_request(HUMAN)
    request.external_model_api = True
    request.network = "off"
    decision = evaluate_boundary(request)
    assert decision.rejected is True
    assert decision.boundary_held is True
    assert decision.reason == "external_model_api_with_restricted_mri"


def test_offline_host_network_on_external_api_still_reject(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("NI_OFFLINE", "1")
    request = parse_request(HUMAN).raw
    request["network"] = "on"
    request["external_model_api"] = True
    result = submit(request, approve=True, store=tmp_path)
    assert result["status"] == "rejected"
    assert result["reason"] == "external_model_api_with_restricted_mri"
    assert result["execute_called"] is False
    assert execute_call_count() == 0
    assert result["receipt"]["boundary_held"] is True


def test_undeclared_outbound_fails_boundary(tmp_path: Path) -> None:
    request = parse_request(HUMAN).raw
    request["undeclared_outbound"] = True
    result = submit(request, approve=True, store=tmp_path)
    assert result["status"] == "failed"
    assert result["receipt"]["boundary_held"] is False
    assert result["execute_called"] is False
