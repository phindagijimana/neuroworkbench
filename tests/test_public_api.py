"""Public import, agent tool, optional MCP. No execute tool. No model API."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from neuroworkbench import submit
from neuroworkbench.agent import TOOLS, call_tool
from neuroworkbench.mcp import handle_message

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "examples/requests/t1w_human.yaml"


def test_public_submit_requires_approve(tmp_path: Path) -> None:
    os.environ.pop("OPENAI_API_KEY", None)
    result = submit(REQUEST, approve=False, store=tmp_path)
    assert result["status"] == "rejected"
    assert result["execute_called"] is False


def test_agent_tool_has_no_execute(tmp_path: Path) -> None:
    via = call_tool("submit", {"request": str(REQUEST), "approve": False, "store": str(tmp_path)})
    assert via["execute_called"] is False
    assert {tool["name"] for tool in TOOLS} == {"submit"}
    with pytest.raises(ValueError, match="execute"):
        call_tool("execute", {})


def test_mcp_tools_call_submit(tmp_path: Path) -> None:
    listed = handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    assert [tool["name"] for tool in listed["result"]["tools"]] == ["submit"]
    called = handle_message(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "submit",
                "arguments": {
                    "request": str(REQUEST),
                    "approve": False,
                    "store": str(tmp_path),
                },
            },
        }
    )
    assert called["result"]["isError"] is False
    assert "rejected" in called["result"]["content"][0]["text"]
