"""RO-Crate 1.1-shaped export of an N4 receipt.

Reuse the Research Object Crate vocabulary. Do not invent a provenance
language. NIfTI hashes may be the literal ``bytes_unavailable``.
"""

from __future__ import annotations

from typing import Any

RO_CRATE_CONTEXT = "https://w3id.org/ro/crate/1.1/context"
RO_CRATE_CONFORMS = "https://w3id.org/ro/crate/1.1"


def receipt_to_rocrate(receipt: dict[str, Any]) -> dict[str, Any]:
    """Build a JSON dict with ``@context`` and a Dataset ``@type`` from a receipt."""
    run_id = str(receipt.get("run_id") or "unknown")
    hashes = receipt.get("input_hashes") or {}
    dataset: dict[str, Any] = {
        "@id": "./",
        "@type": "Dataset",
        "name": f"NeuroInsight receipt {run_id}",
        "description": (
            "Reconstructability receipt (N4). Encoded as RO-Crate / PROV, "
            "not a new language."
        ),
        "proposer": receipt.get("proposer"),
        "approver": receipt.get("approver"),
        "plugin_id": receipt.get("plugin_id"),
        "plugin_version": receipt.get("plugin_version"),
        "image_digest": receipt.get("image_digest"),
        "parameters": receipt.get("parameters") or {},
        "resource_request": receipt.get("resource_request"),
        "environment": receipt.get("environment"),
        "backend": receipt.get("backend"),
        "slurm_job_id_if_hpc": receipt.get("slurm_job_id_if_hpc"),
        "input_hashes": hashes,
        "bids_identities": receipt.get("bids_identities") or {},
        "qc_passed": list(receipt.get("qc_passed") or []),
        "qc_failed": list(receipt.get("qc_failed") or []),
        "qc_did_not_run": list(receipt.get("qc_did_not_run") or []),
        "output_hashes": receipt.get("output_hashes", "bytes_unavailable"),
        "boundary_held": bool(receipt.get("boundary_held")),
        "status": receipt.get("status"),
        "reason": receipt.get("reason"),
        "dry_run": bool(receipt.get("dry_run")),
        "hasPart": [{"@id": "receipt.json"}],
    }
    return {
        "@context": RO_CRATE_CONTEXT,
        "@graph": [
            {
                "@id": "ro-crate-metadata.json",
                "@type": "CreativeWork",
                "conformsTo": {"@id": RO_CRATE_CONFORMS},
                "about": {"@id": "./"},
            },
            dataset,
            {
                "@id": "receipt.json",
                "@type": ["File", "CreativeWork"],
                "encodingFormat": "application/json",
                "name": f"receipt {run_id}",
            },
        ],
    }
