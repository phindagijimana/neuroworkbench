"""Refuse execution unless the human CLI --approve gate is present."""

from __future__ import annotations

from typing import Any

from kernel.request import RunRequest


class ApprovalError(PermissionError):
    """Submit lacked --approve or the request approval object is closed."""


def require_approval(request: RunRequest, *, cli_approve: bool) -> dict[str, Any]:
    if not cli_approve:
        return {
            "ok": False,
            "reason": "missing_cli_approve",
            "approver": None,
        }
    if not request.approval:
        return {
            "ok": False,
            "reason": "approval_object_missing",
            "approver": None,
        }
    if request.approval.get("execution") is False:
        return {
            "ok": False,
            "reason": "approval.execution_false",
            "approver": None,
        }
    if request.approval.get("execution") is not True:
        return {
            "ok": False,
            "reason": "approval.execution_not_true",
            "approver": None,
        }
    return {
        "ok": True,
        "reason": "human_approved",
        "approver": "human",
    }
