"""Locate public S0 T1w under shared/data/external. Never download.

Wave 6: if ``shared/data/external/ds000003`` already has real gzip
T1w bytes, resolve ``external:ds000003`` to that path. A git-annex
pointer (tiny ASCII, starts with ``..``) is absent — do not treat
it as a T1w. Pytest must not fetch OpenNeuro. NIfTI bytes stay
outside git.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from kernel.request import RunRequest

FOLDER_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = FOLDER_ROOT.parent
EXTERNAL_ROOT = WORKSPACE / "shared" / "data" / "external"
DS000003_ROOT = EXTERNAL_ROOT / "ds000003"
T1W_REL = Path("sub-01") / "anat" / "sub-01_T1w.nii.gz"
EXTERNAL_TOKEN = "external:ds000003"
PLACEHOLDER_T1W = "bids:sub-01/anat/sub-01_T1w.nii.gz"
_ABSENT_REASON = (
    "shared/data/external/ds000003 has no public T1w bytes; "
    "pytest does not download; placeholder jobs remain"
)


def external_root() -> Path:
    return EXTERNAL_ROOT


def manifest_t1w_path() -> Path:
    return DS000003_ROOT / T1W_REL


def _is_nifti(path: Path) -> bool:
    name = path.name.lower()
    return name.endswith(".nii.gz") or name.endswith(".nii")


def _looks_t1w(path: Path) -> bool:
    return "t1w" in path.name.lower()


def _is_git_annex_pointer(path: Path) -> bool:
    """Tiny ASCII annex pointer (starts with ``..``) is not a T1w."""
    try:
        size = path.stat().st_size
        if size >= 1024:
            return False
        head = path.read_bytes()[:256]
    except OSError:
        return False
    if not head or head.startswith(b"\x1f\x8b"):
        return False
    try:
        text = head.decode("ascii").lstrip()
    except UnicodeDecodeError:
        return False
    return text.startswith("..") or text.startswith("/annex/")


def _is_real_nifti_bytes(path: Path) -> bool:
    """Accept real gzip/NIfTI. Reject git-annex / LFS pointers."""
    if _is_git_annex_pointer(path):
        return False
    try:
        size = path.stat().st_size
        if size < 1024:
            return False
        head = path.read_bytes()[:8]
    except OSError:
        return False
    if head.startswith(b"\x1f\x8b"):
        return True
    if head[:2] in (b"\x5c\x01", b"\x6c\x01"):  # NIfTI-1 sizeof_hdr 348
        return True
    if head.startswith(b"..") or head.startswith(b"<") or head.startswith(b"version"):
        return False
    return False


def find_ds000003_t1w() -> Path | None:
    """Return an on-disk public T1w, or None. Does not download."""
    preferred = manifest_t1w_path()
    if preferred.is_file() and _is_real_nifti_bytes(preferred):
        return preferred.resolve()
    if DS000003_ROOT.is_dir():
        hits = [
            path.resolve()
            for path in DS000003_ROOT.rglob("*")
            if path.is_file()
            and _is_nifti(path)
            and _looks_t1w(path)
            and _is_real_nifti_bytes(path)
        ]
        if hits:
            return sorted(hits)[0]
    return None


def external_s0_status() -> dict[str, Any]:
    """Record why a live-path dry-run is or is not available. Not an evaluation."""
    path = find_ds000003_t1w()
    present = path is not None
    return {
        "present": present,
        "path": str(path) if path is not None else None,
        "accession": "ds000003",
        "bytes_in_git": False,
        "download_in_pytest": False,
        "reason": (
            "public T1w present under shared/data/external/ds000003"
            if present
            else _ABSENT_REASON
        ),
    }


def resolve_external_inputs(
    request: RunRequest,
    *,
    use_external_s0: bool = False,
) -> RunRequest:
    """Point ``inputs.t1w`` at ds000003 when present. Never invent bytes."""
    status = external_s0_status()
    request.raw["external_s0"] = status
    t1w = str((request.inputs or {}).get("t1w") or "")
    token = t1w == EXTERNAL_TOKEN or t1w.startswith("external:")
    should = use_external_s0 or token
    if should and status["present"] and status["path"]:
        request.inputs["t1w"] = status["path"]
        raw_inputs = dict(request.raw.get("inputs") or {})
        raw_inputs["t1w"] = status["path"]
        request.raw["inputs"] = raw_inputs
    return request


def request_for_external_s0(
    *,
    template: Path | None = None,
    proposer: str = "human",
    use_if_present: bool = True,
) -> dict[str, Any]:
    """Human-shaped FastSurfer request. Rewrites t1w only when bytes exist."""
    import yaml

    source = template or FOLDER_ROOT / "examples" / "requests" / "t1w_ds000003.yaml"
    if source.is_file():
        job = yaml.safe_load(source.read_text()) or {}
    else:
        fallback = FOLDER_ROOT / "examples" / "requests" / "t1w_human.yaml"
        job = yaml.safe_load(fallback.read_text()) or {}
        job["inputs"] = {**(job.get("inputs") or {}), "t1w": EXTERNAL_TOKEN}
    if not isinstance(job, dict):
        raise ValueError("external S0 template must be a mapping")
    job["proposer"] = proposer
    status = external_s0_status()
    job["external_s0"] = status
    if use_if_present and status["present"] and status["path"]:
        job["inputs"] = {**dict(job.get("inputs") or {}), "t1w": status["path"]}
    return job
