"""NeuroInsight Paper 5 kernel. Human-only dry-run. Agent must not call execute."""

from kernel.approve import ApprovalError, require_approval
from kernel.boundary import BoundaryDecision, evaluate_boundary
from kernel.execute import AGENT_MAY_CALL_EXECUTOR, execute, execute_call_count, reset_execute_calls
from kernel.preflight import preflight
from kernel.qc import collect_qc
from kernel.receipt import build_receipt, write_receipt
from provenance.rocrate import receipt_to_rocrate
from kernel.request import RunRequest, parse_request, validate_request
from kernel.score import compute_score, platform_silent_success
from kernel.submit import submit

__all__ = [
    "AGENT_MAY_CALL_EXECUTOR",
    "ApprovalError",
    "BoundaryDecision",
    "RunRequest",
    "build_receipt",
    "collect_qc",
    "compute_score",
    "evaluate_boundary",
    "execute",
    "execute_call_count",
    "parse_request",
    "platform_silent_success",
    "preflight",
    "receipt_to_rocrate",
    "require_approval",
    "reset_execute_calls",
    "submit",
    "validate_request",
    "write_receipt",
]
