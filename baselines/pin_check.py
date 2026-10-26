"""Public pin/digest baseline: Neurodesk/Apptainer container identity.

Reuse the S0 Neurodesk pin in ``shared/pins.yaml`` and the dry-run allowlist
in ``05_NeuroInsight/pins.yaml``. This module answers one question: does the
request digest match a recorded pin?

It does **not** approve, run QC, write a receipt, or set
``platform_silent_success``. ``pin_ok`` is identity only — not a completed
run and not silent success (N2 is the kernel residual).

Optional export is an RO-Crate-shaped dict of pin-file hashes (BABS/RO-Crate
shape). This is not a second DataLad and not a new provenance language.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import yaml

FOLDER_ROOT = Path(__file__).resolve().parents[1]
SHARED_PINS = FOLDER_ROOT.parent / "shared" / "pins.yaml"
LOCAL_PINS = FOLDER_ROOT / "pins.yaml"


def _norm_digest(value: str) -> str:
    text = str(value).strip().lower()
    if not text:
        return ""
    if text.startswith("sha256:"):
        return text
    return f"sha256:{text}"


def load_pin_sources() -> list[dict[str, str]]:
    sources: list[dict[str, str]] = []
    for path in (SHARED_PINS, LOCAL_PINS):
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text()) or {}
        container = data.get("container") or {}
        digest = container.get("digest")
        if not digest:
            continue
        sources.append(
            {
                "path": str(path),
                "digest": str(digest),
                "container_name": str(container.get("name") or ""),
            }
        )
    return sources


def allowed_pin_digests() -> list[str]:
    return [item["digest"] for item in load_pin_sources()]


def _load_request(source: Path | str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(source, dict):
        return dict(source)
    path = Path(source)
    text = path.read_text()
    if path.suffix.lower() == ".json":
        import json

        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError("pin-check request must be a mapping")
    return data


def extract_digest(source: Path | str | dict[str, Any]) -> str:
    data = source if isinstance(source, dict) else _load_request(source)
    for key in ("image_digest", "presented_digest", "digest"):
        value = data.get(key)
        if value:
            return str(value)
    container = data.get("container") or {}
    if isinstance(container, dict) and container.get("digest"):
        return str(container["digest"])
    return ""


def _pin_file_hashes() -> dict[str, str]:
    hashes: dict[str, str] = {}
    for path in (SHARED_PINS, LOCAL_PINS):
        if path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            hashes[path.name if path != SHARED_PINS else "shared/pins.yaml"] = (
                f"sha256:{digest}"
            )
    return hashes


def ro_crate_pin_hashes() -> dict[str, Any]:
    """RO-Crate-shaped dict of pin-file hashes. Not a new provenance model."""
    hashes = _pin_file_hashes()
    parts = [{"@id": name} for name in hashes]
    graph: list[dict[str, Any]] = [
        {
            "@id": "ro-crate-metadata.json",
            "@type": "CreativeWork",
            "conformsTo": {"@id": "https://w3id.org/ro/crate/1.1"},
            "about": {"@id": "./"},
        },
        {
            "@id": "./",
            "@type": "Dataset",
            "name": "NeuroInsight pin/digest baseline",
            "hasPart": parts,
        },
    ]
    for name, digest in hashes.items():
        graph.append(
            {
                "@id": name,
                "@type": ["File"],
                "sha256": digest,
            }
        )
    return {
        "@context": "https://w3id.org/ro/crate/1.1/context",
        "@graph": graph,
    }


def pin_check(source: Path | str | dict[str, Any]) -> dict[str, Any]:
    """Return pin_ok / pin_fail. Never approve, never QC, never a receipt."""
    digest = extract_digest(source)
    sources = load_pin_sources()
    allowed = {_norm_digest(item["digest"]) for item in sources}
    matches = bool(digest) and _norm_digest(digest) in allowed
    result: dict[str, Any] = {
        "status": "pin_ok" if matches else "pin_fail",
        "digest_matches": matches,
        "requested_digest": digest,
        "allowed_digests": [item["digest"] for item in sources],
        "pin_sources": sources,
        "qc_ran": False,
        "approve_ran": False,
        "receipt": None,
        "reason": (
            "digest matches recorded Neurodesk/dry-run pin"
            if matches
            else (
                f"image_digest {digest} not in pins"
                if digest
                else "image_digest missing"
            )
        ),
        "ro_crate": ro_crate_pin_hashes(),
    }
    # pin_ok is not a platform score. Do not set platform_silent_success.
    return result
