"""Validate → approve → boundary → (dry-run execute) → QC → receipt → score."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from kernel.approve import require_approval
from kernel.boundary import evaluate_boundary
from kernel.execute import ExecutionResult, execute
from kernel.external import resolve_external_inputs
from kernel.hardware import probe_hardware
from kernel.preflight import preflight
from kernel.qc import collect_qc
from kernel.receipt import build_receipt, write_receipt
from kernel.request import RunRequest, parse_request, validate_request
from kernel.score import compute_score


def submit(
    source: Path | str | dict[str, Any],
    *,
    approve: bool,
    store: Path | None = None,
    dry_run: bool = True,
    use_external_s0: bool = False,
) -> dict[str, Any]:
    request = source if isinstance(source, RunRequest) else parse_request(source)
    request = resolve_external_inputs(request, use_external_s0=use_external_s0)
    run_id = f"ni-{uuid.uuid4().hex[:12]}"
    validation = validate_request(request)
    if not validation["ok"]:
        return _finish(
            request,
            run_id=run_id,
            approve_record={"ok": False, "approver": None, "reason": "invalid_request"},
            boundary_held=True,
            status="rejected",
            reason="; ".join(validation["errors"]),
            execution=None,
            digest_matches=validation["digest_matches"],
            store=store,
            dry_run=dry_run,
            preflight_record=None,
            execute_called=False,
        )

    approval = require_approval(request, cli_approve=approve)
    if not approval["ok"]:
        return _finish(
            request,
            run_id=run_id,
            approve_record=approval,
            boundary_held=True,
            status="rejected",
            reason=approval["reason"],
            execution=None,
            digest_matches=validation["digest_matches"],
            store=store,
            dry_run=dry_run,
            preflight_record=None,
            execute_called=False,
        )

    boundary = evaluate_boundary(request)
    if boundary.rejected or boundary.decision == "FAIL":
        failure = "rejected_boundary" if boundary.rejected else "irrecoverable"
        return _finish(
            request,
            run_id=run_id,
            approve_record=approval,
            boundary_held=boundary.boundary_held,
            status="rejected" if boundary.rejected else "failed",
            reason=boundary.reason,
            execution=None,
            digest_matches=validation["digest_matches"],
            store=store,
            dry_run=dry_run,
            preflight_record=None,
            execute_called=False,
            failure_class=failure,
        )

    if not validation["digest_matches"]:
        return _finish(
            request,
            run_id=run_id,
            approve_record=approval,
            boundary_held=True,
            status="failed",
            reason=validation["digest_reason"],
            execution=None,
            digest_matches=False,
            store=store,
            dry_run=dry_run,
            preflight_record=None,
            execute_called=False,
            failure_class="irrecoverable",
        )

    preflight_record = preflight(request)
    if preflight_record["refuse"]:
        return _finish(
            request,
            run_id=run_id,
            approve_record=approval,
            boundary_held=True,
            status="rejected",
            reason=preflight_record["reason"],
            execution=None,
            digest_matches=True,
            store=store,
            dry_run=dry_run,
            preflight_record=preflight_record,
            execute_called=False,
            failure_class="rejected_preflight",
        )

    execution = execute(request, approved=True, dry_run=dry_run)
    injected_fail = execution.reason in {"oom", "interrupted_worker"}
    return _finish(
        request,
        run_id=run_id,
        approve_record=approval,
        boundary_held=True,
        status="failed" if injected_fail else "accepted",
        reason=execution.reason,
        execution=execution,
        digest_matches=True,
        store=store,
        dry_run=dry_run,
        preflight_record=preflight_record,
        execute_called=True,
        failure_class="irrecoverable" if injected_fail else "none",
    )


def _finish(
    request: RunRequest,
    *,
    run_id: str,
    approve_record: dict[str, Any],
    boundary_held: bool,
    status: str,
    reason: str,
    execution: ExecutionResult | None,
    digest_matches: bool,
    store: Path | None,
    dry_run: bool,
    preflight_record: dict[str, Any] | None,
    execute_called: bool,
    failure_class: str = "none",
) -> dict[str, Any]:
    qc = collect_qc(request, execution, preflight=preflight_record)
    required_stages_ran = bool(execution and execution.stages_ran)
    reported_complete = bool(execution and execution.reported_complete)
    injection = request.raw.get("injection") or {}
    if isinstance(injection, dict) and injection.get("ui_reported_complete") is True:
        reported_complete = True
    elif request.raw.get("ui_reported_complete") is True:
        reported_complete = True
    receipt = build_receipt(
        request,
        run_id=run_id,
        approver=approve_record.get("approver"),
        qc=qc,
        boundary_held=boundary_held,
        status=status,
        reason=reason,
        dry_run=dry_run,
        executed_digest=None if execution is None else execution.image_digest,
        hardware=None if execution is None else execution.hardware or probe_hardware(),
        external_s0=request.raw.get("external_s0"),
    )
    receipt_path = None
    if store is not None:
        receipt_path = str(write_receipt(receipt, Path(store)))
    proposer = request.proposer if request.proposer in {"human", "agent"} else "human"
    backend = request.backend if request.backend in {"local_container", "slurm"} else "local_container"
    score = compute_score(
        run_id=run_id,
        proposer=proposer,
        backend=backend,
        execution_reported_complete=reported_complete,
        required_qc_passed=qc["required_qc_passed"],
        digest_matches=digest_matches,
        boundary_held=boundary_held,
        required_stages_ran=required_stages_ran,
        approved_by=approve_record.get("approver"),
        plugin_id=request.plugin_id,
        image_digest_approved=request.image_digest,
        image_digest_executed=None if execution is None else execution.image_digest,
        failure_class=failure_class,
    )
    return {
        "run_id": run_id,
        "status": status,
        "reason": reason,
        "execute_called": execute_called,
        "receipt": receipt,
        "receipt_path": receipt_path,
        "score": score,
        "qc": qc,
        "preflight": preflight_record,
        "validation_digest_matches": digest_matches,
        "hardware": receipt.get("hardware"),
        "external_s0": receipt.get("external_s0"),
    }
