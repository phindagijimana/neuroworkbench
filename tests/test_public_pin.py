"""Public pin/digest baseline. pin_ok is not silent success and does not run QC."""

from __future__ import annotations

import json
from pathlib import Path

from baselines.pin_check import pin_check

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"
SHARED_PINS = ROOT.parent / "shared" / "pins.yaml"
DIGEST_SWAP = (
    ROOT.parent / "shared" / "fixtures" / "invalid" / "digest_swap" / "instance.json"
)


def test_matching_digest_is_pin_ok() -> None:
    result = pin_check(HUMAN)
    assert result["status"] == "pin_ok"
    assert result["digest_matches"] is True
    assert result["requested_digest"] == "sha256:PENDING"


def test_shared_neurodesk_digest_is_pin_ok() -> None:
    import yaml

    pins = yaml.safe_load(SHARED_PINS.read_text())
    digest = pins["container"]["digest"]
    result = pin_check({"image_digest": digest})
    assert result["status"] == "pin_ok"
    assert digest in result["allowed_digests"]


def test_digest_swap_is_pin_fail() -> None:
    fixture = json.loads(DIGEST_SWAP.read_text())
    result = pin_check(fixture)
    assert result["status"] == "pin_fail"
    assert result["digest_matches"] is False
    assert result["requested_digest"] == fixture["presented_digest"]


def test_pin_ok_does_not_run_qc_or_set_silent_success() -> None:
    result = pin_check(HUMAN)
    assert result["status"] == "pin_ok"
    assert result["qc_ran"] is False
    assert result["approve_ran"] is False
    assert result["receipt"] is None
    assert "platform_silent_success" not in result
    assert result.get("platform_silent_success") is not True


def test_pin_check_exports_ro_crate_shape_not_a_new_model() -> None:
    result = pin_check(HUMAN)
    crate = result["ro_crate"]
    assert crate["@context"] == "https://w3id.org/ro/crate/1.1/context"
    assert any(node.get("@id") == "./" for node in crate["@graph"])


def test_cli_pin_check_matching_digest() -> None:
    import io
    import json
    from contextlib import redirect_stdout

    from neuroworkbench.cli import main

    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(["pin-check", str(HUMAN)])
    payload = json.loads(buf.getvalue())
    assert code == 0
    assert payload["status"] == "pin_ok"
    assert "platform_silent_success" not in payload
