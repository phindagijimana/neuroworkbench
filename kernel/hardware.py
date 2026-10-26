"""Honest GPU / Slurm / container probe. Never invent presence. Never pull."""

from __future__ import annotations

import shutil
from typing import Any

from kernel.request import DRY_RUN_DIGEST, RunRequest, _norm_digest


def which(name: str) -> str | None:
    return shutil.which(name)


def gpu_present() -> bool:
    """FastSurfer GPU only if nvidia-smi is actually on PATH."""
    return which("nvidia-smi") is not None


def slurm_present() -> bool:
    """Slurm only if sbatch or sinfo is actually on PATH."""
    return which("sbatch") is not None or which("sinfo") is not None


def pin_is_dry_run_allowlist(digest: str) -> bool:
    return _norm_digest(digest) == _norm_digest(DRY_RUN_DIGEST)


def local_image_available(digest: str) -> bool:
    """Local inspect only. Never pull. PENDING is not a container."""
    if not digest or pin_is_dry_run_allowlist(digest):
        return False
    runtime = which("apptainer") or which("singularity") or which("docker")
    if runtime is None:
        return False
    # A digest pin without a local SIF/image is not available. Do not pull.
    return False


def probe_hardware() -> dict[str, Any]:
    """Record what is on this host. Absence is recorded, not invented."""
    return {
        "gpu_present": gpu_present(),
        "slurm_present": slurm_present(),
        "nvidia_smi": which("nvidia-smi"),
        "sbatch": which("sbatch"),
        "sinfo": which("sinfo"),
        "apptainer": which("apptainer") or which("singularity"),
        "docker": which("docker"),
        "fastsurfer_gpu": False,
        "image_pulled": False,
    }


def dry_run_policy(
    request: RunRequest,
    *,
    hardware: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Stay dry-run unless a real pin matches a local image.

    Slurm or nvidia-smi on PATH does not submit a job or launch FastSurfer.
    ``sha256:PENDING`` is the dry-run allowlist, not a pulled Neurodesk image.
    """
    hw = dict(hardware or probe_hardware())
    digest = request.image_digest
    allowlist = pin_is_dry_run_allowlist(digest)
    image_local = local_image_available(digest)
    hw["image_pulled"] = image_local
    reason = "dry_run_no_fastsurfer_gpu"
    if request.backend == "slurm":
        if not hw["slurm_present"]:
            reason = "slurm_not_present"
        elif allowlist or not image_local:
            reason = "dry_run_slurm_present_pin_unmatched"
        else:
            reason = "dry_run_no_fastsurfer_gpu"
    elif hw["gpu_present"] and (allowlist or not image_local):
        reason = "dry_run_gpu_present_pin_unmatched"
    return {
        "dry_run": True,
        "reason": reason,
        "hardware": hw,
        "image_local": image_local,
        "pin_is_allowlist": allowlist,
    }
