"""Call SciCap/SciGuard from siblings when importable. Never fake PASS."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Callable

from kernel.request import RunRequest

FOLDER_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = FOLDER_ROOT.parent
SCICAP_CORE = WORKSPACE / "01_SciCap" / "packages" / "scicap-core"
SCIGUARD_ROOT = WORKSPACE / "02_SciGuard"
SCIGUARD_LABELS_FIXTURE = (
    SCIGUARD_ROOT / "fixtures" / "invalid" / "labels_t1w_to_dwi_no_transform.yaml"
)

LABELS_TO_DWI_PLUGINS = frozenset(
    {
        "map_labels_to_diffusion",
        "labels_t1w_on_dwi",
        "labels_t1w_to_dwi",
    }
)


def preflight(request: RunRequest) -> dict[str, Any]:
    scicap = _scicap_invoke(request)
    sciguard = _sciguard_validate(request)
    refuse = False
    reason = "ok"
    if scicap.get("decision") == "REJECT":
        refuse = True
        reason = "scicap_reject"
    if sciguard.get("status") == "FAIL":
        refuse = True
        reason = "sciguard_fail_labels_to_dwi"
    elif _labels_to_dwi_no_transform(request):
        # Kernel refuses the locked FAIL fixture even when SciGuard is a stub.
        # Library status stays not_run — do not record a fake SciGuard PASS.
        refuse = True
        reason = "sciguard_fail_labels_to_dwi"
        if sciguard.get("library") == "not_run":
            sciguard = {
                **sciguard,
                "status": "FAIL",
                "source": "kernel_stub_not_importable",
                "library": "not_run",
                "note": (
                    "not_run recorded; FAIL is the locked labels→DWI fixture, "
                    "not a claimed SciGuard PASS"
                ),
            }
    return {
        "scicap": scicap,
        "sciguard": sciguard,
        "refuse": refuse,
        "reason": reason,
    }


def _append_sys_path(path: Path) -> None:
    text = str(path)
    if text not in sys.path:
        sys.path.append(text)


def _scicap_invoke(request: RunRequest) -> dict[str, Any]:
    """Import SciCap if possible. Do not call invoke without capability+instance."""
    invoke_fn, origin = _load_scicap_invoke()
    if invoke_fn is None:
        return {
            "decision": "not_run",
            "library": "not_run",
            "reason": "scicap_not_importable",
        }
    capability, instance = _scicap_bind_args(request)
    if capability is None or instance is None:
        # Importable but this run request is not a SciCap instance. Not PASS.
        return {
            "decision": "not_run",
            "library": "not_run",
            "reason": "scicap_no_capability_instance",
            "importable": origin,
        }
    try:
        result = invoke_fn(capability, instance)
    except TypeError:
        return {
            "decision": "not_run",
            "library": "not_run",
            "reason": "scicap_invoke_signature_mismatch",
            "importable": origin,
        }
    except Exception as exc:  # noqa: BLE001 — live sibling may raise; never fake PASS
        return {
            "decision": "not_run",
            "library": "not_run",
            "reason": f"scicap_error:{exc}",
            "importable": origin,
        }
    decision = str(result.get("decision", "not_run"))
    if decision == "PASS":
        decision = "not_run"
    return {"decision": decision, "library": "scicap", "raw": result, "importable": origin}


def _sciguard_validate(request: RunRequest) -> dict[str, Any]:
    """Live SciGuard on labels→DWI. Record FAIL or not_run. Never fake PASS."""
    check_fn = _load_sciguard_check()
    if check_fn is None:
        return {
            "status": "not_run",
            "library": "not_run",
            "reason": "sciguard_not_importable",
        }
    if not _labels_to_dwi_no_transform(request):
        return {
            "status": "not_run",
            "library": "not_run",
            "reason": "sciguard_no_workflow_for_request",
        }
    workflow: Path | dict[str, Any]
    if SCIGUARD_LABELS_FIXTURE.is_file():
        workflow = SCIGUARD_LABELS_FIXTURE
    else:
        workflow = _synthesize_labels_workflow(request)
    try:
        result = check_fn(workflow)
    except Exception as exc:  # noqa: BLE001 — live sibling may raise; never fake PASS
        return {
            "status": "not_run",
            "library": "not_run",
            "reason": f"sciguard_error:{exc}",
        }
    failed = any(item.get("status") == "FAIL" for item in (result.get("edges") or []))
    graph = result.get("graph_status")
    if failed or graph == "reject":
        status = "FAIL"
    else:
        # Do not map eligible / not_auto_accepted onto a kernel PASS.
        status = "not_run"
    return {
        "status": status,
        "library": "sciguard",
        "raw_status": graph,
        "raw": {"graph_status": graph, "certificate": result.get("certificate_of_scientific_correctness")},
    }


def _load_scicap_invoke() -> tuple[Callable[..., Any] | None, str | None]:
    try:
        import scicap as pkg  # type: ignore

        fn = getattr(pkg, "invoke", None)
        if callable(fn):
            return fn, "scicap"
    except ImportError:
        pass
    try:
        from scicap_core.invoke import invoke as core_invoke  # type: ignore

        return core_invoke, "scicap_core"
    except ImportError:
        pass
    init = SCICAP_CORE / "__init__.py"
    if not init.is_file():
        return None, None
    if "scicap_core" not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            "scicap_core",
            init,
            submodule_search_locations=[str(SCICAP_CORE)],
        )
        if spec is None or spec.loader is None:
            return None, None
        module = importlib.util.module_from_spec(spec)
        sys.modules["scicap_core"] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop("scicap_core", None)
            return None, None
    try:
        from scicap_core.invoke import invoke as sibling_invoke  # type: ignore

        return sibling_invoke, "scicap_core"
    except ImportError:
        return None, None


def _load_sciguard_check() -> Callable[..., Any] | None:
    try:
        import sciguard as pkg  # type: ignore

        fn = getattr(pkg, "validate", None) or getattr(pkg, "check_workflow", None)
        if callable(fn):
            return fn
    except ImportError:
        pass
    try:
        from validation.check import check_workflow

        return check_workflow
    except ImportError:
        pass
    if SCIGUARD_ROOT.is_dir():
        _append_sys_path(SCIGUARD_ROOT)
        try:
            from validation.check import check_workflow

            return check_workflow
        except ImportError:
            return None
    return None


def _scicap_bind_args(request: RunRequest) -> tuple[Any, Any]:
    """NeuroInsight run requests are not SciCap capability/instance pairs."""
    _ = request
    return None, None


def _synthesize_labels_workflow(request: RunRequest) -> dict[str, Any]:
    """Locked labels→DWI no-transform shape when the sibling fixture is absent."""
    return {
        "schema_version": "0.1",
        "workflow_id": f"ni-{request.plugin_id}",
        "operations": [
            {
                "id": "map1",
                "contract": "map_labels_to_diffusion",
                "interpolation": "nearest_neighbor",
            }
        ],
        "edges": [
            {
                "id": "labels→map1",
                "from": "labels",
                "to": "map1.labels",
                "artifact": {
                    "kind": "parcellation",
                    "modality": "T1w",
                    "space": "subject_T1w",
                    "atlas": "DesikanKilliany",
                    "value_type": "discrete_labels",
                    "subject": "sub-01",
                },
            },
            {
                "id": "ref→map1",
                "from": "tractogram",
                "to": "map1.reference",
                "artifact": {
                    "kind": "diffusion_reference",
                    "modality": "dwi",
                    "space": "subject_DWI",
                    "subject": "sub-01",
                },
            },
        ],
    }


def _labels_to_dwi_no_transform(request: RunRequest) -> bool:
    plugin = request.plugin_id
    if plugin in LABELS_TO_DWI_PLUGINS:
        transform = request.inputs.get("transform") or request.workflow.get("transform")
        return not transform
    labels = request.inputs.get("labels") or request.inputs.get("parcellation")
    reference = str(
        request.inputs.get("reference")
        or request.inputs.get("dwi")
        or request.workflow.get("reference")
        or ""
    ).lower()
    transform = request.inputs.get("transform") or request.workflow.get("transform")
    if labels and ("dwi" in reference or "diffusion" in reference) and not transform:
        return True
    return False
