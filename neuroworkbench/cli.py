"""CLI: validate plugin, submit approved request, print receipt. No model API."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import yaml

FOLDER_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STORE = FOLDER_ROOT / "provenance" / "runs"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="neuroworkbench")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="validate a plugin manifest")
    p_validate.add_argument("plugin")

    p_submit = sub.add_parser("submit", help="submit a run request (dry-run kernel)")
    p_submit.add_argument("request")
    p_submit.add_argument(
        "--approve",
        action="store_true",
        help="human execution approval; without this flag execute is not called",
    )
    p_submit.add_argument("--store", default=str(DEFAULT_STORE))
    p_submit.add_argument(
        "--external-s0",
        action="store_true",
        help="point t1w at shared/data/external/ds000003 if present (no download)",
    )

    p_pin = sub.add_parser(
        "pin-check",
        help="public pin/digest baseline; no approve, no QC, no receipt",
    )
    p_pin.add_argument("request")

    p_receipt = sub.add_parser("receipt", help="print a stored receipt")
    p_receipt.add_argument("--run", required=True)
    p_receipt.add_argument("--format", default="json", choices=("json", "ro-crate"))
    p_receipt.add_argument("--store", default=str(DEFAULT_STORE))

    args = parser.parse_args(argv)
    if args.command == "validate":
        return _validate_plugin(Path(args.plugin))
    if args.command == "submit":
        return _submit(
            Path(args.request),
            approve=args.approve,
            store=Path(args.store),
            use_external_s0=args.external_s0,
        )
    if args.command == "pin-check":
        return _pin_check(Path(args.request))
    if args.command == "receipt":
        return _receipt(args.run, fmt=args.format, store=Path(args.store))
    return 2


def _validate_plugin(path: Path) -> int:
    if not path.is_file():
        print(json.dumps({"ok": False, "reason": "plugin_not_found", "path": str(path)}))
        return 2
    data = yaml.safe_load(path.read_text()) or {}
    errors = []
    for key in ("name", "version", "inputs", "executor", "checks"):
        if key not in data:
            errors.append(f"missing {key}")
    checks = data.get("checks") or {}
    if not checks.get("required"):
        errors.append("checks.required missing")
    if checks.get("not_run_is_not_pass") is not True:
        errors.append("checks.not_run_is_not_pass must be true")
    if data.get("approval_required") is not True:
        errors.append("approval_required must be true")
    network = data.get("network", "off")
    if network not in {False, None, 0, "off", "false"}:
        errors.append("plugin network must default off")
    if data.get("agent_may_invoke_directly") is True:
        errors.append("agent_may_invoke_directly must be false")
    payload = {
        "ok": not errors,
        "plugin": data.get("name"),
        "version": data.get("version"),
        "errors": errors,
    }
    print(json.dumps(payload, indent=2))
    return 0 if not errors else 2


def _pin_check(path: Path) -> int:
    from baselines.pin_check import pin_check

    result = pin_check(path)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "pin_ok" else 1


def _submit(path: Path, *, approve: bool, store: Path, use_external_s0: bool = False) -> int:
    # Kernel path has no model. Unset keys do not block; they must stay unused.
    _ = os.environ.get("OPENAI_API_KEY")
    from kernel.submit import submit

    result = submit(
        path,
        approve=approve,
        store=store,
        dry_run=True,
        use_external_s0=use_external_s0,
    )
    print(json.dumps(_public(result), indent=2))
    if result["status"] == "accepted":
        return 0
    if result["reason"] == "missing_cli_approve":
        return 3
    return 1


def _receipt(run_id: str, *, fmt: str, store: Path) -> int:
    from kernel.receipt import load_receipt

    try:
        receipt = load_receipt(store, run_id)
    except FileNotFoundError as exc:
        print(json.dumps({"ok": False, "reason": str(exc)}))
        return 2
    if fmt == "ro-crate":
        from provenance.rocrate import receipt_to_rocrate

        print(json.dumps(receipt_to_rocrate(receipt), indent=2))
        return 0
    print(json.dumps(receipt, indent=2))
    return 0


def _public(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": result["run_id"],
        "status": result["status"],
        "reason": result["reason"],
        "execute_called": result["execute_called"],
        "receipt": result["receipt"],
        "score": result["score"],
        "receipt_path": result["receipt_path"],
        "hardware": result.get("hardware"),
        "external_s0": result.get("external_s0"),
        "qc": result.get("qc"),
        "preflight": result.get("preflight"),
    }


if __name__ == "__main__":
    sys.exit(main())
