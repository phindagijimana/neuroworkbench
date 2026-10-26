"""N6 fail-closed data boundary. Linux local / Slurm rule. No model API upload."""

from __future__ import annotations

import os
from dataclasses import dataclass

from kernel.request import RunRequest


def _offline_host() -> bool:
    """Disconnected-host unit: NI_OFFLINE=1 still REJECTS external API + network:on."""
    return os.environ.get("NI_OFFLINE", "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class BoundaryDecision:
    decision: str
    reason: str
    boundary_held: bool
    undeclared_outbound: bool = False

    @property
    def rejected(self) -> bool:
        return self.decision == "REJECT"


def evaluate_boundary(request: RunRequest) -> BoundaryDecision:
    """Reject external model APIs that see image bytes or restricted MRI paths.

    Undeclared outbound fails the run and sets boundary_held false. A clean
    REJECT before execute leaves nothing — boundary_held stays true.
    """
    wants_external = request.external_model_api or _has_external_endpoint(request)
    # N6 disconnected host: NI_OFFLINE=1 does not weaken REJECT.
    if wants_external and (request.has_image_input or request.network == "on"):
        return BoundaryDecision(
            decision="REJECT",
            reason="external_model_api_with_restricted_mri",
            boundary_held=True,
        )
    if _offline_host() and request.network == "on":
        return BoundaryDecision(
            decision="REJECT",
            reason="offline_host_network_on",
            boundary_held=True,
        )
    if request.network == "on" and not request.approval.get("any_network_path"):
        return BoundaryDecision(
            decision="REJECT",
            reason="network_on_without_network_approval",
            boundary_held=True,
        )
    undeclared = bool(request.raw.get("undeclared_outbound"))
    if undeclared:
        return BoundaryDecision(
            decision="FAIL",
            reason="undeclared_outbound_during_run",
            boundary_held=False,
            undeclared_outbound=True,
        )
    return BoundaryDecision(
        decision="ALLOW",
        reason="local_plugin_network_off",
        boundary_held=True,
    )


def _has_external_endpoint(request: RunRequest) -> bool:
    for blob in (request.parameters, request.raw):
        for key in ("api_url", "model_endpoint", "external_api"):
            value = blob.get(key)
            if value:
                return True
    return False
