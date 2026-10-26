"""Parse and validate an N1 run request. Network defaults to off."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ALLOWED_PROPOSERS = frozenset({"human", "agent"})
ALLOWED_BACKENDS = frozenset({"local_container", "slurm"})
FOLDER_ROOT = Path(__file__).resolve().parents[1]
SHARED_PINS = FOLDER_ROOT.parent / "shared" / "pins.yaml"
LOCAL_PINS = FOLDER_ROOT / "pins.yaml"


class RequestError(ValueError):
    """Run request failed schema or pin checks."""


@dataclass
class RunRequest:
    proposer: str
    plugin_id: str
    plugin_version: str
    image_digest: str
    inputs: dict[str, Any]
    parameters: dict[str, Any]
    backend: str
    network: str
    approval: dict[str, Any]
    external_model_api: bool = False
    workflow: dict[str, Any] = field(default_factory=dict)
    source_path: Path | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def has_image_input(self) -> bool:
        return any(_looks_like_image(value) for value in _walk_values(self.inputs))


def parse_request(source: Path | str | dict[str, Any]) -> RunRequest:
    if isinstance(source, dict):
        data = dict(source)
        path = None
    else:
        path = Path(source)
        data = yaml.safe_load(path.read_text()) or {}
        if not isinstance(data, dict):
            raise RequestError("run request must be a mapping")
    network = _normalize_network(data.get("network", "off"))
    approval = data.get("approval")
    if approval is None:
        approval = {}
    if not isinstance(approval, dict):
        raise RequestError("approval must be a mapping")
    parameters = data.get("parameters") or {}
    if not isinstance(parameters, dict):
        raise RequestError("parameters must be a mapping")
    inputs = data.get("inputs") or {}
    if not isinstance(inputs, dict):
        raise RequestError("inputs must be a mapping")
    workflow = data.get("workflow") or {}
    if not isinstance(workflow, dict):
        raise RequestError("workflow must be a mapping")
    return RunRequest(
        proposer=str(data.get("proposer", "")),
        plugin_id=str(data.get("plugin_id", "")),
        plugin_version=str(data.get("plugin_version", "")),
        image_digest=str(data.get("image_digest", "")),
        inputs=inputs,
        parameters=parameters,
        backend=str(data.get("backend", "local_container")),
        network=network,
        approval=approval,
        external_model_api=_as_bool(
            data.get("external_model_api", parameters.get("external_model_api", False))
        ),
        workflow=workflow,
        source_path=path,
        raw=data,
    )


def validate_request(request: RunRequest) -> dict[str, Any]:
    errors: list[str] = []
    if request.proposer not in ALLOWED_PROPOSERS:
        errors.append("proposer must be human or agent")
    for name in ("plugin_id", "plugin_version", "image_digest"):
        if not getattr(request, name):
            errors.append(f"{name} is required")
    if not request.inputs:
        errors.append("inputs is required")
    if request.backend not in ALLOWED_BACKENDS:
        errors.append("backend must be local_container or slurm")
    if request.network not in {"off", "on"}:
        errors.append("network must be off or on")
    if not request.approval:
        errors.append("approval is required")
    digest_ok, digest_reason = digest_matches_pin(request.image_digest)
    return {
        "ok": not errors,
        "errors": errors,
        "digest_matches": digest_ok,
        "digest_reason": digest_reason,
        "pinned_digest": load_pinned_digest(),
        "network": request.network,
    }


DRY_RUN_DIGEST = "sha256:PENDING"


def load_pinned_digest() -> str:
    for path in (SHARED_PINS, LOCAL_PINS):
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text()) or {}
        container = data.get("container") or {}
        digest = container.get("digest")
        if digest:
            return str(digest)
    return DRY_RUN_DIGEST


def allowed_digests() -> list[str]:
    allowed = [DRY_RUN_DIGEST]
    pinned = load_pinned_digest()
    if pinned not in allowed:
        allowed.append(pinned)
    return allowed


def digest_matches_pin(image_digest: str) -> tuple[bool, str]:
    if not image_digest:
        return False, "image_digest missing"
    allowed = {_norm_digest(item) for item in allowed_digests()}
    if _norm_digest(image_digest) in allowed:
        return True, "digest matches pin or dry-run allowlist"
    pinned = load_pinned_digest()
    return False, f"image_digest {image_digest} != pin {pinned}"


def _norm_digest(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("sha256:"):
        return text
    return f"sha256:{text}"


def _normalize_network(value: Any) -> str:
    if value in (None, ""):
        return "off"
    if value is True or str(value).lower() in {"on", "true", "1", "yes"}:
        return "on"
    return "off"


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).lower() in {"true", "1", "yes", "on"}


def _walk_values(obj: Any) -> list[Any]:
    if isinstance(obj, dict):
        found: list[Any] = []
        for value in obj.values():
            found.extend(_walk_values(value))
        return found
    if isinstance(obj, list):
        found = []
        for value in obj:
            found.extend(_walk_values(value))
        return found
    return [obj]


def _looks_like_image(value: Any) -> bool:
    text = str(value).lower()
    markers = (
        ".nii",
        ".nii.gz",
        "t1w",
        "dwi",
        "bold",
        "bids:",
        "bids://",
        "restricted_mri",
    )
    return any(marker in text for marker in markers)
