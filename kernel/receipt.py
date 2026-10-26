"""N4 reconstructability receipt. Encode as JSON + RO-Crate, not a new language."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from kernel.request import RunRequest
from provenance.rocrate import receipt_to_rocrate


RECEIPT_KEYS = (
    "run_id",
    "proposer",
    "approver",
    "input_hashes",
    "bids_identities",
    "plugin_id",
    "plugin_version",
    "image_digest",
    "parameters",
    "resource_request",
    "environment",
    "backend",
    "slurm_job_id_if_hpc",
    "qc_passed",
    "qc_failed",
    "qc_did_not_run",
    "output_hashes",
    "boundary_held",
    "status",
    "reason",
    "dry_run",
)


def build_receipt(
    request: RunRequest,
    *,
    run_id: str,
    approver: str | None,
    qc: dict[str, Any],
    boundary_held: bool,
    status: str,
    reason: str,
    dry_run: bool,
    executed_digest: str | None = None,
) -> dict[str, Any]:
    receipt = {
        "run_id": run_id,
        "proposer": request.proposer,
        "approver": approver,
        "input_hashes": _input_hashes(request),
        "bids_identities": _bids_identities(request),
        "plugin_id": request.plugin_id,
        "plugin_version": request.plugin_version,
        "image_digest": executed_digest or request.image_digest,
        "parameters": dict(request.parameters),
        "resource_request": {
            "cpu": 8,
            "memory_gb": 32,
            "gpu": False,
            "note": "plugin sketch; GPU not allocated in dry-run",
        },
        "environment": request.backend,
        "backend": request.backend,
        "slurm_job_id_if_hpc": None,
        "qc_passed": list(qc.get("qc_passed") or []),
        "qc_failed": list(qc.get("qc_failed") or []),
        "qc_did_not_run": list(qc.get("qc_did_not_run") or []),
        "output_hashes": "bytes_unavailable",
        "boundary_held": bool(boundary_held),
        "status": status,
        "reason": reason,
        "dry_run": dry_run,
        "encoding": ["PROV", "RO-Crate", "DataLad"],
    }
    missing = [key for key in RECEIPT_KEYS if key not in receipt]
    if missing:
        raise RuntimeError(f"receipt missing keys: {missing}")
    return receipt


def write_receipt(receipt: dict[str, Any], store: Path) -> Path:
    run_dir = Path(store) / receipt["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = run_dir / "receipt.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    crate = receipt_to_rocrate(receipt)
    (run_dir / "ro-crate-metadata.json").write_text(json.dumps(crate, indent=2) + "\n")
    return receipt_path


def load_receipt(store: Path, run_id: str) -> dict[str, Any]:
    path = Path(store) / run_id / "receipt.json"
    if not path.is_file():
        raise FileNotFoundError(f"receipt not found for run {run_id}")
    return json.loads(path.read_text())


def _input_hashes(request: RunRequest) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for key, value in request.inputs.items():
        path = Path(str(value).replace("bids:", "").replace("bids://", ""))
        if path.is_file():
            hashes[key] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            hashes[key] = "bytes_unavailable"
    return hashes


def _bids_identities(request: RunRequest) -> dict[str, str]:
    identities: dict[str, str] = {}
    for key, value in request.inputs.items():
        identities[key] = str(value)
    return identities
