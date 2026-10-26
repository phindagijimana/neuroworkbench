"""GPU/Slurm only when those tools are on PATH. Still dry-run unless a pin matches."""

from __future__ import annotations

from pathlib import Path

from kernel.hardware import gpu_present, probe_hardware, slurm_present
from kernel.request import parse_request
from kernel.submit import submit

ROOT = Path(__file__).resolve().parents[1]
HUMAN = ROOT / "examples" / "requests" / "t1w_human.yaml"


def test_probe_matches_tools_on_path() -> None:
    hw = probe_hardware()
    assert hw["gpu_present"] is gpu_present()
    assert hw["slurm_present"] is slurm_present()
    assert hw["fastsurfer_gpu"] is False
    assert hw["image_pulled"] is False
    assert hw["gpu_present"] is (hw["nvidia_smi"] is not None)
    assert hw["slurm_present"] is (hw["sbatch"] is not None or hw["sinfo"] is not None)


def test_local_container_stays_dry_run_without_fastsurfer(tmp_path: Path) -> None:
    result = submit(HUMAN, approve=True, store=tmp_path)
    assert result["receipt"]["dry_run"] is True
    assert result["receipt"]["resource_request"]["gpu"] is False
    assert result["score"]["execution_reported_complete"] is False
    assert result["score"]["platform_silent_success"] is False
    hw = result["hardware"]
    assert hw["fastsurfer_gpu"] is False
    if not gpu_present():
        assert result["reason"] == "dry_run_no_fastsurfer_gpu"
    else:
        assert result["reason"] in {
            "dry_run_no_fastsurfer_gpu",
            "dry_run_gpu_present_pin_unmatched",
        }


def test_slurm_backend_does_not_submit_job(tmp_path: Path) -> None:
    request = parse_request(HUMAN).raw
    request["backend"] = "slurm"
    result = submit(request, approve=True, store=tmp_path)
    assert result["receipt"]["dry_run"] is True
    assert result["receipt"]["slurm_job_id_if_hpc"] is None
    assert result["score"]["execution_reported_complete"] is False
    assert result["score"]["platform_silent_success"] is False
    if slurm_present():
        assert result["reason"] == "dry_run_slurm_present_pin_unmatched"
        assert result["hardware"]["slurm_present"] is True
    else:
        assert result["reason"] == "slurm_not_present"
        assert result["hardware"]["slurm_present"] is False
