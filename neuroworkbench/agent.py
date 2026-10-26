"""Agent call contract. Same as `neuroworkbench submit`. No execute tool."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from neuroworkbench import submit

TOOLS: list[dict[str, Any]] = [
    {
        "name": "submit",
        "description": (
            "Fail-closed workbench submit. Without approve=true, execute is not called. "
            "Dry-run only. Not an agent."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "request": {"type": "string", "description": "Path to request YAML"},
                "approve": {
                    "type": "boolean",
                    "default": False,
                    "description": "Human execution approval",
                },
                "store": {"type": "string", "description": "Optional receipt store directory"},
            },
            "required": ["request"],
        },
    }
]


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    if name == "execute":
        raise ValueError("execute is not a tool; the workbench does not expose execute")
    if name != "submit":
        raise ValueError(f"unknown tool: {name}")
    store = Path(arguments["store"]) if arguments.get("store") else None
    result = submit(
        arguments["request"],
        approve=bool(arguments.get("approve", False)),
        store=store,
        dry_run=True,
    )
    return {
        "run_id": result.get("run_id"),
        "status": result.get("status"),
        "reason": result.get("reason"),
        "execute_called": result.get("execute_called"),
        "receipt": result.get("receipt"),
        "score": result.get("score"),
    }
