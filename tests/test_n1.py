"""N1: agent cannot execute; receipt format is identical regardless of proposer."""

from __future__ import annotations

import ast
import tomllib
from pathlib import Path

from kernel.execute import AGENT_MAY_CALL_EXECUTOR
from kernel.receipt import RECEIPT_KEYS
from kernel.request import parse_request
from kernel.submit import submit

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"
FORBIDDEN_EXECUTE_IMPORTS = frozenset(
    {
        "kernel.execute",
        "kernel.execute.execute",
    }
)


def test_agent_may_not_call_executor() -> None:
    assert AGENT_MAY_CALL_EXECUTOR is False


def test_agents_directory_cannot_import_execute() -> None:
    agents = ROOT / "agents"
    if not agents.exists():
        return
    offenders: list[str] = []
    for path in agents.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in FORBIDDEN_EXECUTE_IMPORTS or alias.name.startswith(
                        "kernel.execute"
                    ):
                        offenders.append(f"{path}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "kernel.execute" or module.startswith("kernel.execute"):
                    offenders.append(f"{path}: from {module} import")
                if module == "kernel" and any(alias.name == "execute" for alias in node.names):
                    offenders.append(f"{path}: from kernel import execute")
    assert offenders == []


def test_no_neuroinsight_agent_binary() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text())
    scripts = data.get("project", {}).get("scripts", {})
    assert "neuroworkbench" in scripts
    assert "neuroinsight" not in scripts
    assert "neuroinsight-agent" not in scripts
    assert all("neuroinsight-agent" not in name for name in scripts)


def test_human_and_agent_receipt_keys_match(tmp_path: Path) -> None:
    human = submit(HUMAN, approve=True, store=tmp_path / "human")
    agent_req = parse_request(HUMAN).raw
    agent_req["proposer"] = "agent"
    agent = submit(agent_req, approve=True, store=tmp_path / "agent")
    assert set(human["receipt"]) >= set(RECEIPT_KEYS)
    assert set(agent["receipt"]) == set(human["receipt"])
    assert human["receipt"]["proposer"] == "human"
    assert agent["receipt"]["proposer"] == "agent"
    assert human["receipt"]["approver"] == agent["receipt"]["approver"] == "human"
    for key in (
        "plugin_version",
        "image_digest",
        "backend",
        "qc_did_not_run",
        "boundary_held",
    ):
        assert human["receipt"][key] == agent["receipt"][key]


def test_agent_request_still_needs_approve(tmp_path: Path) -> None:
    request = parse_request(HUMAN).raw
    request["proposer"] = "agent"
    result = submit(request, approve=False, store=tmp_path)
    assert result["execute_called"] is False
    assert result["reason"] == "missing_cli_approve"
