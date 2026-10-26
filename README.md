# NeuroWorkbench

Fail-closed workbench: validate → `--approve` → boundary → receipt.

Command: **`neuroworkbench`**. Not the [NeuroInsight desktop](https://github.com/phindagijimana/neuroinsight_research). Not an agent. No `neuroinsight-agent`.

## Go

```bash
pip install git+https://github.com/phindagijimana/neuroworkbench.git
neuroworkbench submit examples/requests/t1w_human.yaml --approve
```

```python
from neuroworkbench import submit
submit("request.yaml", approve=True)
```

Python 3.11+. Dry-run only. No model API. Without `--approve`, execute is not called.

If `shared/data/external/ds000003` is already on disk, point a dry-run at it:

```bash
neuroworkbench submit examples/requests/t1w_ds000003.yaml --approve
neuroworkbench submit examples/requests/t1w_human.yaml --approve --external-s0
```

Do not commit `.nii`. Pytest does not download. Slurm or `nvidia-smi` on PATH still dry-run unless a real pin matches a local image. No FastSurfer GPU launch.

Optional agent transport (`submit` only; no execute tool): `python -m neuroworkbench.mcp`

```bash
pytest tests
```

Proposer (no execute): [`nwproposer`](https://github.com/phindagijimana/nwproposer).

[Methods](docs/NeuroInsight_Methods.md) · Apache-2.0 · no NIfTI or PHI
