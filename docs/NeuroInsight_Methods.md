# NeuroInsight methods

Paper 5 protocol · 26 October 2026 · planning document, no results claimed

This is the locked methods stack for NeuroInsight. It follows the blueprint and the limitations-to-methods filter. NeuroInsight is a **fail-closed workbench plus platform scoring**, not the first neuroimaging workbench and not NeuroInsightAgent. The installable name is **`neuroworkbench`** so it is not confused with the shipping `neuroinsight_research` product.

Related documents: [limitations to methods](NeuroInsight_Limitations_to_Methods.md) · [blueprint](Paper5_NeuroInsight_Research_Blueprint.pdf)

SciCap owns contracts. SciGuard owns preflight edges. NeuroAgentBench owns whether an agent run produced a scientifically valid artifact. EvidenceGraph owns literature binding. NeuroInsight owns **whether this workbench executed, recorded, and refused to hide a failed or unsafe run**.

Neurodesk already ships tools everywhere (*Nature Methods*; 2026 coding-agent remotes). NeuroClaw, CyberNeuro, NeuroPilot, and Brain Researcher already occupy agentic MRI workbenches. Cite them. Do not write “first platform” or “first agent workbench.”

The AI interface is optional. Deterministic local/HPC operation is first-class. If you strip the LLM and nothing of scientific interest remains, these methods have failed. The agentic condition is **Paper 6**, implemented against the existing product at `git@github.com:phindagijimana/neuroinsight_research.git`, not as a rewrite of this folder.

---

## 1. Scope

**Question.** Can one installable kernel — human and optional agent as proposers only — reduce setup burden and platform silent success, and produce reconstructable, locally-and-Slurm-equivalent runs, compared with Neurodesk, BIDS Apps, Nipype/Pydra, and an accessible portal?

**Unit.** One approved run request × one plugin or workflow × one backend (local container or Slurm). Human-only and agent-proposed requests are the same object.

**First workflows.** Public BIDS T1w anatomical (FastSurfer/FreeSurfer-class) and a public DWI connectome recipe. Synthetic invalid fixtures for failure injection.

**Non-scope.** Capability-contract algorithms (Paper 1). Composition preflight as a result (Paper 2). Agent artifact scoring (Paper 3). Literature attribution (Paper 4). Replacing Nipype, Pydra, Nextflow, Slurm, Neurodesk, or BABS. Clinical diagnosis. Autonomous science. Automatic upload of restricted MRI to external model APIs.

---

## 2. The methods

These are the Paper 5 methods. They are not optional product features.

### N1. Dual-interface invariant

One execution kernel. The only write that starts a run is an **approved run request**. A human form and an agent proposal compile to the same request type.

The kernel:

1. Validates the request (schema, BIDS, allowlisted image digest, resource quota, data-boundary policy).
2. Requires explicit approval for execution, overwrite, HPC submission, and any network path.
3. Emits one receipt format regardless of proposer (`proposer` ∈ {human, agent}).
4. Refuses unrestricted shell and any model-written command that is not an allowlisted plugin invoke.

The agent cannot call the executor. SciCap or SciGuard, if present, run on this request as they would on a human request. Their detections are not Paper 5 results.

**Test.** Receipt equality on matched human vs agent-proposed runs. Incorrect-submission rate under the same checks. If the agent path can complete a run the human path would reject, N1 has failed.

### N2. Platform silent success

For every run record:

| Field | Meaning |
|---|---|
| `execution_reported_complete` | UI/API said the job finished |
| `required_qc_passed` | Every check the plugin declared as required actually ran and passed |
| `digest_matches` | Executed image digest equals the approved digest |
| `boundary_held` | No undeclared egress or path escape |
| `required_stages_ran` | Every required stage ran |
| `platform_silent_success` | Reported complete, and QC failed **or** digest mismatch **or** boundary broken **or** a required stage did not run |

Inject failures before scoring: missing image, invalid parameter, interrupted worker, OOM, unavailable container, digest swap, attempted outbound on restricted data. Count recovered, irrecoverable, and silent. Debugging time is secondary.

Do not call this NeuroAgentBench. Paper 3 scores the agent’s artifact. Paper 5 scores the platform’s report.

### N3. Cross-environment equivalence

Before any local–Slurm pair, lock per-artifact comparison rules:

- byte identity where scientifically required (manifests, hashes, parameters, image digest)
- declared numeric tolerance where not (segmentation volumes, connectome weights)
- `environment_divergence` when the pair disagrees beyond tolerance
- `comparison_unknown` when an artifact needed for the comparison is missing — not a pass

Primary number for this arm: fraction of paired runs that meet the locked rule, plus the divergence list. Hardware-specific differences are reported, not averaged away.

Running on two backends is not the method. **Scoring the pair** is.

### N4. Reconstructability receipt

A receipt is a contract. An independent reader, without the original operator, must be able to answer:

- who or what proposed the run, and who approved it
- input hashes and BIDS identities
- plugin version and image digest
- parameters and resource request
- environment (local container vs Slurm job id)
- which QC checks passed, failed, or **did not run**
- outputs and their hashes
- whether the data boundary held

Encode with PROV / RO-Crate / DataLad. Do not invent a provenance language. If BABS receipts already suffice on the BIDS-App subset, emit BABS/RO-Crate and do not claim N4 as novel on that subset.

**Test.** Blinded reconstruct and diagnose-from-receipt. Gold is successful reconstruction and correct failure class.

### N5. Matched setup-burden protocol

Freeze tasks and validity criteria first. Counterbalance NeuroInsight (human-only) against at least:

- documented CLI + the same containers
- Nipype or Pydra, same stages
- a BIDS App, same algorithm
- one accessible portal (CBRAIN or brainlife) only on like-for-like tasks

Outcomes: independently verified completion, setup minutes, interventions, configuration-error count, and N2 silent success. Expertise is a factor. IRB determination if you run a user study.

Without this protocol, Paper 5 is a README.

### N6. Fail-closed data boundary

A decision rule on every run request:

| Request | Kernel decision |
|---|---|
| Local/HPC plugin, no network, paths inside workspace | Eligible after approval |
| Any external model API with image bytes or paths to restricted MRI | `REJECT` |
| Undeclared outbound during a run | fail the run; `boundary_held = false`; N2 silent success if the UI still says complete |
| Metadata-only agent help | Allowed only if the policy says so and no image leaves the box |

Test on Linux local **and** Slurm, including a disconnected-host condition and an attempted-exfil fixture. CyberNeuro owns the Windows measurement. The residual is the same rule on backends labs actually use.

Research use only. No diagnostic or FDA language.

---

## 3. Representation (what is implemented)

| Object | Location |
|---|---|
| Plugin manifest | `plugins/examples/` ; `plugins/sdk` |
| Run request (human or agent) | `schema/run_request.yaml` |
| Data-boundary policy | `schema/boundary.yaml` |
| Receipt checklist | `schema/receipt.yaml` |
| Platform score | `schema/score.schema.json` |
| BIDS intake | `bids/` |
| Local / Slurm adapters | `execution/local` ; `execution/hpc` |
| Per-stage QC | `qc/` |
| RO-Crate / PROV export | `provenance/` |
| Optional proposer | `agents/` |
| Failure injection | `tests/` |

Interfaces (proposed, not implemented):

```text
neuroinsight validate plugin.yaml
neuroinsight submit run_request.yaml --approve
neuroinsight receipt --run RUN_ID --format ro-crate
neuroinsight evaluate --pair local,slurm --runs runs/
```

The kernel must run with no model API configured. Agent code, if present, may only write a run request.

---

## 4. Primary and secondary endpoints

**Primary (software toolbox; pre-register).** Independently verified workflow completion from a declared starting install state through validated artifacts, on the frozen tasks, with numerator, denominator, and a clustered interval.

**Primary (methods increment, if claimed).** Platform silent-success rate under the injected-failure suite (N2), paired against CLI / Neurodesk / BIDS App on the same fixtures.

**Secondary**

- Receipt equality, human vs agent-proposed (N1)
- Incorrect-submission rate on the agent path (N1)
- Local–Slurm equivalence and `environment_divergence` list (N3)
- Blinded reconstructability and missing-field rate (N4)
- Setup minutes, interventions, configuration errors (N5)
- Boundary reject / held rates, including attempted exfil (N6)
- Recovered vs irrecoverable failures
- Compute and token cost; agent cost tracked separately

Do not treat agent-assisted speed as the primary. If speed improves and silent success rises, N1/N2 have failed.

---

## 5. Pilot that decides the methods are real

Five independently installable plugins and the two public recipes (anatomical, diffusion), plus a synthetic invalid set.

| Case | Gold | Method under test |
|---|---|---|
| Human-approved FastSurfer on a public BIDS T1w | complete, receipt reconstructable | N4, N5 |
| Agent proposes the same run; human approves | identical receipt to the human-only path | N1 |
| Agent proposes a run the schema or SciGuard would reject | kernel refuses; no execution | N1 |
| Required QC fails; UI says success | `platform_silent_success` | N2 |
| Image digest swapped after approval | refuse or fail; not complete | N2, N4 |
| Restricted dataset, agent asks an external API | `REJECT`; boundary held | N6 |
| Same recipe, local container vs Slurm | locked equivalence or listed divergence | N3 |
| Interrupted worker / OOM | recovered or irrecoverable, never silent | N2 |
| Blinded reviewer given only the receipt | reconstructs who approved, digest, QC-not-run | N4 |
| New user, same task, Neurodesk vs NeuroInsight | report time and errors; do not assume a win | N5 |

**Go (software toolbox).** Independent install works; receipts reconstruct; silent success is measured and rare; local–Slurm rule is declared and tested.  
**Go (methods increment).** N1 receipt equality holds; N2 silent success is lower than CLI/Neurodesk on injected failures; N5 setup burden moves without raising silent success.  
**No-go as a methods paper.** A polished wrapper around Neurodesk and BIDS Apps. Then JOSS, or contribute upstream.

---

## 6. Boundaries with the other papers

| Method | Owner |
|---|---|
| N1–N6 as specified above | **NeuroInsight (Paper 5)** |
| Late binding and invoke ALLOW / REJECT / ABSTAIN | SciCap (Paper 1) |
| Edge-level PASS / FAIL / UNKNOWN preflight | SciGuard (Paper 2) |
| Layered artifact oracle, agent false success | NeuroAgentBench (Paper 3) |
| Scoped literature attribution | EvidenceGraph (Paper 4) |
| Containerized tool availability | Neurodesk; wrap, do not replace |
| DataLad-tracked BIDS App jobs on Slurm | BABS; emit or call |
| Agentic closed-loop neuroimaging execution | NeuroClaw; comparator |
| Windows no-egress agent workbench | CyberNeuro; cite |
| Live-run claim cards | Brain Researcher / NEURA; cite |

Paper 5 may integrate Papers 1–3 as libraries. Those tables do not become this paper’s novelty and must not be republished as confirmatory results for Papers 1–3 without a cross-reference.

---

## 7. Journal gates (locked with the methods)

Do not assume a workbench yields a Nature paper.

| Strongest output | Venue |
|---|---|
| Installable workbench, five plugins, receipts, independent install reports | ***Imaging Neuroscience* Software Toolbox** — default |
| Thin residual over Neurodesk + BABS | *JOSS* / *SoftwareX* |
| Broad biological utility plus a real powered imaging study | *PLOS Computational Biology* Software |
| A new general life-science method, not integration | Then, and only then, *Nature Methods* |

**Do not design the project as a Nature paper.** Neurodesk already occupies accessible reproducible environments in *Nature Methods*. NeuroClaw already occupies agentic neuroimaging execution. The differentiator is **one fail-closed kernel and honest platform numbers**.

---

## 8. What these methods are not

Do not describe NeuroInsight as any of the following:

- The first neuroimaging platform or first reproducible container pipeline
- NeuroInsightAgent, or the first agent workbench
- A replacement for Nipype, Pydra, Nextflow, Slurm, Neurodesk, or BABS
- A new plugin language
- A SciCap, SciGuard, NeuroAgentBench, or EvidenceGraph methods paper
- Clinical decision support or FDA-cleared software
- Autonomous science
- A Nature Methods paper because the UI is nicer

---

## 9. Implementation correspondence

| Method | Location |
|---|---|
| N1 dual-interface request | `schema/run_request.yaml` ; `agents/` writes requests only |
| N2 silent success | `schema/score.schema.json` ; `tests/` failure injection |
| N3 local–Slurm pair | `execution/local` ; `execution/hpc` ; score `environment_*` |
| N4 receipt | `schema/receipt.yaml` ; `provenance/` RO-Crate export |
| N5 setup-burden tasks | `tests/` task sheets; evaluation protocol in this document |
| N6 boundary | `schema/boundary.yaml` ; kernel reject path |

Public demo data: synthetic or OpenNeuro snapshots only. No PHI. Network off by default. Distinguishing human-approved runs from agent-proposed requests is mandatory in the receipt.
