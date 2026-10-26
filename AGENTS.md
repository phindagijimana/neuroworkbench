# Agent instructions — NeuroInsight (Paper 5)

Read [`docs/NeuroInsight_Methods.md`](docs/NeuroInsight_Methods.md) before writing code. This folder is a **fail-closed execution kernel plus platform scoring**, not NeuroInsightAgent and not the first neuroimaging workbench.

Program build plan: [`../docs/BUILD_PLAN.md`](../docs/BUILD_PLAN.md) · S0: [`../shared/AGENTS.md`](../shared/AGENTS.md)

Build **after** SciCap invoke and SciGuard validate exist, or stub those calls behind interfaces. Human-only kernel first.

## Mission

The only write that starts a run is an **approved run request**. Validate → approve → execute (local container) → QC → receipt. Network default off. Agent, if present later, may write a request and must not call the executor.

## Do not build

- NeuroInsightAgent, or an agent that wraps Papers 1–4 as the product.
- A Nipype/Pydra/Slurm/Neurodesk replacement.
- A new plugin language (import Boutiques / BIDS App conventions).
- Automatic upload of MRI to external model APIs.
- A polished web UI before the CLI kernel works.
- Claiming SciCap/SciGuard/NAB confirmatory tables as Paper 5 results.
- Clinical or FDA language.

## Locked methods you must implement

| ID | Rule |
|---|---|
| N1 | Human and agent compile to the same request. Agent cannot execute. Receipt format identical. |
| N2 | `platform_silent_success` = reported complete ∧ (QC fail ∨ digest mismatch ∨ boundary broken ∨ required stage skipped). |
| N3 | Local vs Slurm scored with locked tolerances; missing compare artifact → `comparison_unknown`. Not v0 unless Slurm exists. |
| N4 | Receipt answers proposer, approver, digest, hashes, QC passed/failed/**did not run**, boundary. Encode PROV/RO-Crate. |
| N5 | Setup-burden protocol is evaluation, not code. Freeze task sheets later. |
| N6 | External model API with restricted MRI → REJECT. Undeclared outbound fails the run. |

## Reuse (do not replace)

- [`schema/run_request.yaml`](schema/run_request.yaml)
- [`schema/boundary.yaml`](schema/boundary.yaml)
- [`schema/receipt.yaml`](schema/receipt.yaml)
- [`schema/score.schema.json`](schema/score.schema.json)
- [`plugins/examples/fastsurfer_anatomical.yaml`](plugins/examples/fastsurfer_anatomical.yaml)

Call `scicap invoke` and `sciguard validate` as libraries on the request when those packages are importable. If they are not installed, skip with `qc_did_not_run` recorded — do not fake PASS.

Neurodesk/Apptainer for the image. BIDS Validator for intake. Do not write a scheduler.

## Target tree

```text
schema/                 # already present
plugins/examples/fastsurfer_anatomical.yaml
kernel/request.py       # parse + validate run_request
kernel/boundary.py      # N6
kernel/approve.py       # refuse if approval missing
kernel/execute.py       # local container only in v0; no shell interpolation
kernel/qc.py
kernel/receipt.py
kernel/score.py         # platform_silent_success
neuroinsight/cli.py
tests/test_kernel.py
tests/test_boundary.py
pyproject.toml          # console_script: neuroinsight
```

`agents/` may be absent in v0. If you add it, it can only write `run_request.yaml`.

## CLI

```text
neuroinsight validate plugins/examples/fastsurfer_anatomical.yaml
neuroinsight submit examples/requests/t1w_human.yaml --approve
neuroinsight receipt --run RUN_ID --format json
```

Without `--approve`, submit must not execute.

## Run request (v0 instance)

```yaml
proposer: human
plugin_id: fastsurfer_anatomical
plugin_version: 0.1.0
image_digest: "sha256:PENDING"   # must match pins or REJECT
inputs:
  t1w: "bids:sub-01/anat/sub-01_T1w.nii.gz"
parameters: {}
backend: local_container
network: off
approval:
  execution: true
```

If `proposer: agent` and code in `kernel/execute.py` is called from `agents/`, that is an N1 failure.

## First vertical slice (must pass)

| Case | Gold |
|---|---|
| Human-approved request, network off, digest matches pin (or dry-run) | accepted; receipt has proposer=human, qc fields |
| Missing `--approve` | no execution |
| Agent-shaped request that SciGuard would FAIL (labels→DWI) | kernel refuses; no execute |
| Required QC listed but not run, UI/API would say complete | `platform_silent_success` true in score helper |
| Digest in request ≠ pin | refuse or fail; not complete |
| Request asks external model API with an image path | `REJECT`; `boundary_held` true if nothing left |

v0 may **dry-run** execution (no FastSurfer GPU) if the container is unavailable: still run validate, approve, boundary, receipt, and score. Record `qc_did_not_run` rather than inventing QC pass. Do not pretend FastSurfer completed.

## Receipt (required keys)

See [`schema/receipt.yaml`](schema/receipt.yaml): proposer, approver, input hashes or “bytes_unavailable”, plugin version, image digest, parameters, backend, `qc_passed`, `qc_failed`, `qc_did_not_run`, `boundary_held`.

## Tests

- `test_kernel.py`: no approve → no execute; digest mismatch → not complete.
- `test_boundary.py`: request with `network: on` and `external_model_api: true` → REJECT.
- `test_n1.py`: if an `agents/` helper exists, it cannot import `kernel.execute`.
- Unset model API keys. Kernel path has no model.

## Boundaries

| Call | Owner of the result |
|---|---|
| `scicap invoke` on the plugin | Paper 1 |
| `sciguard validate` on a multi-step request | Paper 2 |
| `neuroagentbench evaluate` on the run tree | Paper 3 |
| Receipt + silent success | **Paper 5** |

## Done when

- `neuroinsight submit --approve` dry-run produces a receipt offline.
- Agent cannot call execute.
- `platform_silent_success` is computed from the score schema.
- Network default is off.

Stop. Do not add Slurm, a React UI, or an agent proposer until N1/N2 tests are green and methods §5 is re-read. Do not name any binary `neuroinsight-agent`.
