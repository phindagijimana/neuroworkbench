# NeuroWorkbench

Fail-closed neuroimaging **workbench**: validate → `--approve` → boundary → receipt → silent-success flag.

Install name and command: **`neuroworkbench`**. This is not [NeuroInsight](https://github.com/phindagijimana/neuroinsight_research) (the shipping desktop) and not an agent. There is no `neuroinsight` or `neuroinsight-agent` command.

The agent cannot execute. A proposer is a separate package (`neuroworkbench-proposer`).

## Install

```bash
pip install -e .
```

Python 3.11+. Dry-run only (no FastSurfer GPU). No model API.

## Use

```bash
neuroworkbench pin-check examples/requests/t1w_human.yaml
neuroworkbench submit examples/requests/t1w_human.yaml            # no execute
neuroworkbench submit examples/requests/t1w_human.yaml --approve
neuroworkbench receipt --run RUN_ID --format ro-crate
```

## Tests

```bash
pytest tests
```

## Docs

- [Methods](docs/NeuroInsight_Methods.md) (N1–N6)
- [Literature map](docs/NeuroInsight_Literature_Map.md)
- [Methods trace](docs/METHODS_TRACE.md)

Apache-2.0. No NIfTI or PHI in this repo.
