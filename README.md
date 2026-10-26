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

Optional agent transport (`submit` only; no execute tool): `python -m neuroworkbench.mcp`

```bash
pytest tests
```

Proposer (no execute): [`nwproposer`](https://github.com/phindagijimana/nwproposer).

[Methods](docs/NeuroInsight_Methods.md) · Apache-2.0 · no NIfTI or PHI
