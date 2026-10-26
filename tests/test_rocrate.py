"""N4: neuroinsight receipt --format ro-crate is RO-Crate-shaped, not a new language."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

from kernel.submit import submit
from neuroworkbench.cli import main
from provenance.rocrate import RO_CRATE_CONTEXT, receipt_to_rocrate

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"


def _dataset(crate: dict) -> dict:
    for node in crate.get("@graph") or []:
        types = node.get("@type")
        if types == "Dataset" or (isinstance(types, list) and "Dataset" in types):
            return node
    raise AssertionError("RO-Crate missing Dataset @type")


def test_receipt_to_rocrate_has_context_and_dataset() -> None:
    crate = receipt_to_rocrate(
        {
            "run_id": "ni-demo",
            "proposer": "human",
            "approver": "human",
            "input_hashes": {"t1w": "bytes_unavailable"},
            "plugin_version": "0.1.0",
            "image_digest": "sha256:PENDING",
            "qc_did_not_run": ["input_schema"],
            "boundary_held": True,
            "status": "accepted",
            "dry_run": True,
        }
    )
    assert crate["@context"] == RO_CRATE_CONTEXT
    dataset = _dataset(crate)
    assert dataset["@type"] == "Dataset"
    assert dataset["input_hashes"]["t1w"] == "bytes_unavailable"
    assert dataset["qc_did_not_run"] == ["input_schema"]
    assert dataset["approver"] == "human"


def test_cli_receipt_format_ro_crate(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=True, store=tmp_path)
    run_id = result["run_id"]
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(
            ["receipt", "--run", run_id, "--format", "ro-crate", "--store", str(tmp_path)]
        )
    assert code == 0
    crate = json.loads(buf.getvalue())
    assert crate["@context"] == RO_CRATE_CONTEXT
    dataset = _dataset(crate)
    assert dataset["@type"] == "Dataset"
    assert dataset["input_hashes"]["t1w"] == "bytes_unavailable"
    assert dataset["dry_run"] is True
    assert "qc_did_not_run" in dataset
