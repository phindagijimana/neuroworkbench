"""Per-stage QC. Missing checks are qc_did_not_run, never a fabricated PASS."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from kernel.execute import ExecutionResult
from kernel.request import RunRequest

FOLDER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PLUGIN = FOLDER_ROOT / "plugins" / "examples" / "fastsurfer_anatomical.yaml"
DEFAULT_REQUIRED = (
    "input_schema",
    "stage_completion",
    "output_exists",
    "qc_required",
)


def load_plugin_required_checks(plugin_id: str) -> list[str]:
    plugin_path = FOLDER_ROOT / "plugins" / "examples" / f"{plugin_id}.yaml"
    path = plugin_path if plugin_path.is_file() else DEFAULT_PLUGIN
    if not path.is_file():
        return list(DEFAULT_REQUIRED)
    data = yaml.safe_load(path.read_text()) or {}
    checks = (data.get("checks") or {}).get("required") or list(DEFAULT_REQUIRED)
    return [str(item) for item in checks]


def collect_qc(
    request: RunRequest,
    execution: ExecutionResult | None,
    *,
    preflight: dict[str, Any] | None = None,
) -> dict[str, Any]:
    required = load_plugin_required_checks(request.plugin_id)
    passed: list[str] = []
    failed: list[str] = []
    did_not_run = list(required)
    notes = ["dry_run: required QC listed but not executed; not_run is not PASS"]
    preflight = preflight or {}
    for name, record in (
        ("scicap_invoke", preflight.get("scicap") or {}),
        ("sciguard_validate", preflight.get("sciguard") or {}),
    ):
        if record.get("library") == "not_run" or record.get("decision") == "not_run" or record.get("status") == "not_run":
            if name not in did_not_run:
                did_not_run.append(name)
            notes.append(f"{name}: not_run")
        elif record.get("decision") == "ALLOW" or record.get("status") == "PASS":
            passed.append(name)
        elif record.get("decision") == "REJECT" or record.get("status") == "FAIL":
            failed.append(name)
    required_ran_and_passed = (not did_not_run) and (not failed)
    return {
        "qc_passed": passed,
        "qc_failed": failed,
        "qc_did_not_run": did_not_run,
        "required_qc_passed": required_ran_and_passed,
        "notes": notes,
        "execution_reason": None if execution is None else execution.reason,
    }
