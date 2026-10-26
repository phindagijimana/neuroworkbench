"""N2 platform silent success. Paper 5 scores the platform report, not the agent artifact."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import jsonschema

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schema" / "score.schema.json"


def platform_silent_success(
    *,
    execution_reported_complete: bool,
    required_qc_passed: bool,
    digest_matches: bool,
    boundary_held: bool,
    required_stages_ran: bool,
) -> bool:
    hidden_failure = (
        (not required_qc_passed)
        or (not digest_matches)
        or (not boundary_held)
        or (not required_stages_ran)
    )
    return bool(execution_reported_complete and hidden_failure)


def compute_score(
    *,
    run_id: str,
    proposer: str,
    backend: str,
    execution_reported_complete: bool,
    required_qc_passed: bool,
    digest_matches: bool,
    boundary_held: bool,
    required_stages_ran: bool,
    approved_by: str | None = None,
    plugin_id: str | None = None,
    image_digest_approved: str | None = None,
    image_digest_executed: str | None = None,
    failure_class: str = "none",
    environment_status: str = "not_paired",
) -> dict[str, Any]:
    silent = platform_silent_success(
        execution_reported_complete=execution_reported_complete,
        required_qc_passed=required_qc_passed,
        digest_matches=digest_matches,
        boundary_held=boundary_held,
        required_stages_ran=required_stages_ran,
    )
    score = {
        "run_id": run_id,
        "proposer": proposer,
        "backend": backend,
        "execution_reported_complete": execution_reported_complete,
        "required_qc_passed": required_qc_passed,
        "digest_matches": digest_matches,
        "boundary_held": boundary_held,
        "required_stages_ran": required_stages_ran,
        "platform_silent_success": silent,
        "failure_class": "silent" if silent else failure_class,
        "environment_status": environment_status,
        "receipt_equal_to_human_path": proposer == "human",
        "infrastructure_failure": False,
    }
    optional = {
        "approved_by": approved_by,
        "plugin_id": plugin_id,
        "image_digest_approved": image_digest_approved,
        "image_digest_executed": image_digest_executed,
    }
    for key, value in optional.items():
        if value is not None:
            score[key] = value
    schema = json.loads(SCHEMA_PATH.read_text())
    jsonschema.validate(score, schema)
    return score
