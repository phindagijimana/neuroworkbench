"""N2 failure-injection suite. No measured silent-success rate."""

from __future__ import annotations

from pathlib import Path

from kernel.execute import execute_call_count
from kernel.score import compute_score, platform_silent_success
from kernel.submit import submit

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"
INJECTION = ROOT / "fixtures" / "injection"
DIGEST_SWAP = INJECTION / "digest_swap.yaml"
OOM = INJECTION / "oom.yaml"
INTERRUPTED = INJECTION / "interrupted.yaml"
QC_SKIP = INJECTION / "qc_skip_ui_complete.yaml"


def test_digest_swap_is_not_complete(tmp_path: Path) -> None:
    result = submit(DIGEST_SWAP, approve=True, store=tmp_path)
    assert result["execute_called"] is False
    assert execute_call_count() == 0
    assert result["status"] != "accepted"
    assert result["receipt"]["status"] != "complete"
    assert result["score"]["digest_matches"] is False
    assert result["score"]["execution_reported_complete"] is False
    assert result["score"]["platform_silent_success"] is False
    assert "silent_success_rate" not in result["score"]


def test_qc_listed_not_run_and_ui_complete_is_silent_success(tmp_path: Path) -> None:
    helper = platform_silent_success(
        execution_reported_complete=True,
        required_qc_passed=False,
        digest_matches=True,
        boundary_held=True,
        required_stages_ran=False,
    )
    assert helper is True

    score = compute_score(
        run_id="ni-injection-qc-skip",
        proposer="human",
        backend="local_container",
        execution_reported_complete=True,
        required_qc_passed=False,
        digest_matches=True,
        boundary_held=True,
        required_stages_ran=False,
        failure_class="none",
    )
    assert score["platform_silent_success"] is True
    assert "silent_success_rate" not in score

    result = submit(QC_SKIP, approve=True, store=tmp_path)
    assert result["receipt"]["qc_did_not_run"]
    assert result["qc"]["required_qc_passed"] is False
    assert result["score"]["execution_reported_complete"] is True
    assert result["score"]["platform_silent_success"] is True
    assert "silent_success_rate" not in result["score"]


def test_no_approve_does_not_execute(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=False, store=tmp_path)
    assert result["status"] == "rejected"
    assert result["reason"] == "missing_cli_approve"
    assert result["execute_called"] is False
    assert execute_call_count() == 0


def test_oom_fixture_is_not_silent_success(tmp_path: Path) -> None:
    result = submit(OOM, approve=True, store=tmp_path)
    assert result["status"] == "failed"
    assert result["reason"] == "oom"
    assert result["score"]["execution_reported_complete"] is False
    assert result["score"]["platform_silent_success"] is False
    assert result["score"]["failure_class"] == "irrecoverable"
    assert result["receipt"]["status"] != "complete"


def test_interrupted_worker_is_not_silent_success(tmp_path: Path) -> None:
    result = submit(INTERRUPTED, approve=True, store=tmp_path)
    assert result["status"] == "failed"
    assert result["reason"] == "interrupted_worker"
    assert result["score"]["execution_reported_complete"] is False
    assert result["score"]["platform_silent_success"] is False
    assert result["score"]["failure_class"] == "irrecoverable"
    assert result["receipt"]["status"] != "complete"
