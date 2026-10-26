"""Local-container dry-run only. N1: agents must not import or call this module."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from kernel.approve import ApprovalError
from kernel.request import RunRequest

# Locked N1 policy. An agents/ helper that imports this module fails test_n1.
AGENT_MAY_CALL_EXECUTOR = False

_EXECUTE_CALLS: list[str] = []

OOM_KINDS = frozenset({"oom", "out_of_memory"})
INTERRUPTED_KINDS = frozenset({"interrupted", "interrupted_worker", "interrupt"})


def injection_kind(request: RunRequest) -> str | None:
    blob = request.raw.get("injection") or request.parameters.get("injection")
    if isinstance(blob, str) and blob.strip():
        return blob.strip().lower()
    if isinstance(blob, dict):
        kind = blob.get("kind") or blob.get("failure") or blob.get("mode")
        if kind:
            return str(kind).strip().lower()
    return None


@dataclass
class ExecutionResult:
    dry_run: bool
    executed: bool
    backend: str
    image_digest: str
    stages_ran: list[str] = field(default_factory=list)
    reported_complete: bool = False
    reason: str = "dry_run_no_container"
    argv: list[str] = field(default_factory=list)


def reset_execute_calls() -> None:
    _EXECUTE_CALLS.clear()


def execute_call_count() -> int:
    return len(_EXECUTE_CALLS)


def execute(
    request: RunRequest,
    *,
    approved: bool,
    dry_run: bool = True,
) -> ExecutionResult:
    """Invoke only after validate, --approve, and boundary ALLOW.

    v0 never launches FastSurfer or a GPU job. Arguments are a list, never a
    shell-interpolated string.
    """
    if not approved:
        raise ApprovalError("execute refused: approval missing")
    if AGENT_MAY_CALL_EXECUTOR:
        raise RuntimeError("N1 violation: agent_may_call_executor must stay false")
    _EXECUTE_CALLS.append(request.plugin_id)
    kind = injection_kind(request)
    if kind in OOM_KINDS:
        return ExecutionResult(
            dry_run=True,
            executed=False,
            backend=request.backend,
            image_digest=request.image_digest,
            stages_ran=[],
            reported_complete=False,
            reason="oom",
            argv=_plugin_argv(request),
        )
    if kind in INTERRUPTED_KINDS:
        return ExecutionResult(
            dry_run=True,
            executed=False,
            backend=request.backend,
            image_digest=request.image_digest,
            stages_ran=[],
            reported_complete=False,
            reason="interrupted_worker",
            argv=_plugin_argv(request),
        )
    if request.backend != "local_container":
        return ExecutionResult(
            dry_run=True,
            executed=False,
            backend=request.backend,
            image_digest=request.image_digest,
            reported_complete=False,
            reason="slurm_not_in_v0",
            argv=_plugin_argv(request),
        )
    if not dry_run:
        return ExecutionResult(
            dry_run=False,
            executed=False,
            backend=request.backend,
            image_digest=request.image_digest,
            reported_complete=False,
            reason="container_unavailable_no_fastsurfer_gpu",
            argv=_plugin_argv(request),
        )
    return ExecutionResult(
        dry_run=True,
        executed=False,
        backend=request.backend,
        image_digest=request.image_digest,
        stages_ran=[],
        reported_complete=False,
        reason="dry_run_no_fastsurfer_gpu",
        argv=_plugin_argv(request),
    )


def _plugin_argv(request: RunRequest) -> list[str]:
    argv = ["apptainer", "exec", "--contain", "--net", "--network", "none"]
    argv.append(request.image_digest)
    argv.extend(["plugin", request.plugin_id, "--version", request.plugin_version])
    for key, value in request.inputs.items():
        argv.extend([f"--{key}", str(value)])
    return argv


def execution_result_from_dict(data: dict[str, Any]) -> ExecutionResult:
    return ExecutionResult(
        dry_run=bool(data.get("dry_run", True)),
        executed=bool(data.get("executed", False)),
        backend=str(data.get("backend", "local_container")),
        image_digest=str(data.get("image_digest", "")),
        stages_ran=list(data.get("stages_ran") or []),
        reported_complete=bool(data.get("reported_complete", False)),
        reason=str(data.get("reason", "")),
        argv=list(data.get("argv") or []),
    )
