# Methods trace — NeuroInsight kernel (Paper 5, wave 2)

Planning document. No evaluation numbers, no novelty already owned by Neurodesk, BABS, NeuroClaw, CyberNeuro, or NeuroPilot. Locked methods stay in [`NeuroInsight_Methods.md`](NeuroInsight_Methods.md). This file maps each locked method to the **public pin/digest tool**, the **literature residual**, and the **test**. There is no N7.

Public substrate: BIDS/pin digest + Neurodesk/Apptainer container identity (`shared/pins.yaml`, `05_NeuroInsight/pins.yaml`). BABS/RO-Crate is the provenance *shape*, not a second DataLad. The public tool is `baselines/pin_check.py`. It answers only whether the request digest matches a recorded pin. It does not approve, run QC, write a receipt, or set `platform_silent_success`.

## Residual (not first platform)

Grant Neurodesk (tools anywhere; 2026 coding-agent remotes), BABS (DataLad-tracked BIDS-App jobs on Slurm), NeuroClaw / NeuroDiscovery (agent executes neuroimaging), CyberNeuro (Windows no-egress + JSON receipts), and NeuroPilot (approval-gated agent pipelines). What remains is:

1. **One kernel** — human and agent compile to the same approved request; the agent cannot execute.
2. **Platform silent success** — UI/API said complete ∧ (QC fail ∨ digest mismatch ∨ boundary broken ∨ required stage skipped), including `qc_did_not_run`.
3. **Local–Slurm scoring later** — locked tolerances; missing compare artifact → `comparison_unknown`. Not v0.
4. **Reconstructability** — approver, digest, hashes or `bytes_unavailable`, QC passed/failed/**did not run**, boundary. Encode PROV/RO-Crate; do not invent a language.

Not first platform. Not first agent workbench. Not a Neurodesk or BABS replacement.

## Trace

| Method | Public tool reused | Literature residual | Test |
|---|---|---|---|
| N1 | existing submit object (`schema/run_request.yaml`; pin-check does not execute) | Agent cannot call execute; same receipt keys regardless of proposer. NeuroClaw’s agent *does* execute; NeuroPilot gates steps but is not one request object for human and agent. | `tests/test_n1.py` |
| N2 | CyberNeuro receipt idea (JSON report of what ran) | `qc_did_not_run` + UI-complete = `platform_silent_success`. Pin-ok is **not** that score. Paper 3 scores the agent artifact; Paper 5 scores the platform report. | `tests/test_kernel.py` |
| N3 | BABS/Slurm (Zhao et al.; DataLad-tracked BIDS-App jobs) | Not in v0. No scheduler. When a Slurm pair exists, score it; missing compare artifact → `comparison_unknown`, not a pass. Document only. | this file |
| N4 | RO-Crate / BABS provenance shape | Reconstructability: who approved, digest, hashes, QC-not-run, boundary. If BABS already suffices on the BIDS-App subset, emit BABS/RO-Crate and do not claim N4 novelty on that subset. | receipt tests in `test_kernel.py`, `test_n1.py`, `test_holistic.py` |
| N5 | Neurodesk remotes (2026 OpenCode/Codex/Claude; T3 Code pairing) | Not in v0. Setup-burden protocol is evaluation, not code. Environment + agent-remote slots are taken; do not write “first accessible environment.” | this file |
| N6 | CyberNeuro no-egress (Windows measurement; no Linux kernel found 26 Oct 2026) | Same REJECT rule on Linux local: `network: on` + external model API with image paths → REJECT; `boundary_held` if nothing left. Pin-check does not enforce this. | `tests/test_boundary.py` |

## Citations (reuse, do not replace)

- **Neurodesk** — Renton et al., *Nature Methods* 21, 804–808 (2024). https://www.nature.com/articles/s41592-024-02237-2 · releases https://neurodesk.org/overview/release-history/ · 2026 remotes (OpenCode, Codex, Claude; T3 Code 2026-09-23) occupy environment and coding-agent-remote slots. Pin identity is their container digest, not a new image format.
- **BABS** — Zhao et al., *Imaging Neuroscience*. https://github.com/PennLINC/babs · DataLad-tracked BIDS-App jobs on SGE/Slurm. Occupies Slurm provenance. N3/N4 must not be a second DataLad.
- **NeuroClaw / NeuroDiscovery** — Wang et al., arXiv:2604.24696 (27 April 2026). https://arxiv.org/abs/2604.24696 · Closed-loop agentic neuroimaging; the agent executes. Residual: agent cannot call `kernel.execute`.
- **CyberNeuro** — arXiv:2607.28841 (30 July 2026). https://arxiv.org/abs/2607.28841 · Windows no-egress, JSON receipts, Planner ≠ Dispatcher. Copy the *test design* (no-egress, receipt honesty), not the Windows measurement. N6 is the same rule on Linux local.
- **NeuroPilot** — Chen et al., arXiv:2608.07541 (2026). https://arxiv.org/abs/2608.07541 · Approval-gated agent pipelines and an append-only ledger. Residual: one approval object for human submit and agent proposal (N1).

PROV / RO-Crate / DataLad encode the receipt. Do not invent a provenance language.

## SciCap / SciGuard on the labels→DWI request

Call `scicap invoke` and `sciguard validate` as libraries when importable. If they are not installed, record `not_run`. Never fake PASS. A kernel refuse of labels→DWI is not a SciGuard confirmatory table.

## Not in v0

- **N3** local–Slurm pair scoring (BABS already occupies the job tracker).
- **N5** matched setup-burden protocol vs Neurodesk remotes / CLI / BIDS App.
- FastSurfer GPU. Model API. A `neuroinsight-agent` binary. A clone of `neuroinsight_research`.

## Wave 3 (this slice)

| Slice | Location | Test |
|---|---|---|
| RO-Crate receipt export | `provenance/rocrate.py`; `neuroinsight receipt --format ro-crate` | `tests/test_rocrate.py` |
| Failure injection (digest swap, QC skip + UI complete, no `--approve`, OOM / interrupted) | `fixtures/injection/`; `kernel/execute.py` | `tests/test_injection.py` |
| Live SciCap / SciGuard on labels→DWI, else `not_run` | `kernel/preflight.py` (sibling import; never fake PASS) | `tests/test_preflight_live.py` |
| N6 disconnected host | `NI_OFFLINE=1` still REJECT on `network: on` + external API | `tests/test_boundary.py` |

No FastSurfer GPU. No Slurm. No `neuroinsight-agent` script. No clone of `neuroinsight_research`. No measured silent-success rate.

## Holistic (same requests)

Same run requests through `pin_check` and `neuroinsight submit --approve` dry-run: matching T1w digest, digest swap, missing `--approve`, labels→DWI, `network: on` + external API. See `tests/test_holistic.py`.
