# Limitations that can become methods

NeuroInsight / Paper 5 · 26 October 2026

Same filter as Papers 1–4: a limitation is a method only if it yields a representation, decision rule, or evaluation protocol that still stands after Neurodesk, brainlife.io, CBRAIN, ChRIS, Flywheel, Nipype/Pydra, BIDS Apps, Boutiques, BABS/DataLad, NeuroClaw, CyberNeuro, NeuroPilot, Brain Researcher, and BCER Agent are granted. The locked Paper 5 protocol is [`NeuroInsight_Methods.md`](NeuroInsight_Methods.md).

The folder is `05_NeuroInsight`. “NeuroInsightAgent” is not a fifth product. The AI interface is optional. Deterministic local/HPC operation is first-class. If you strip the LLM and nothing of scientific interest remains, you do not have a Paper 5 method.

**Filter**

| Keep as a method | Discard as a feature gap |
|---|---|
| One kernel: human click and agent proposal emit the same receipt | “First neuroimaging platform” |
| Platform silent success under failure injection | “First agent workbench” |
| Local vs Slurm equivalence with a declared tolerance | Local + HPC + BIDS + a website |
| Receipt contract + blinded reconstructability | Another plugin language |
| Matched setup-burden protocol vs Neurodesk / BIDS App / Nipype | Claiming SciCap, SciGuard, or NeuroAgentBench results |

SciCap owns **contracts**. SciGuard owns **preflight edges**. NeuroAgentBench owns **how agent runs are scored**. EvidenceGraph owns **literature binding**. NeuroInsight owns **the workbench that executes, records, and refuses to hide a failed or unsafe run**. Do not republish M1–M4, G1–G5, B1–B7, or E1–E5 as Paper 5 methods. The platform may *host* those packages. Hosting is not novelty.

---

## 1. What the closest systems cannot do

| System | Limitation | Why it is not already NeuroInsight |
|---|---|---|
| Nipype / Pydra | Typed Python workflows, caching, provenance, diverse executors. Neurodesk added Pydra in Dec 2025. | Steal the executor. Residual: non-programmer onboarding and operator-level receipts, not a better scheduler. |
| BIDS Apps | Portable `bids /out participant` convention. | Wrap it. Do not redefine it. Residual: multi-tool life cycle, QC, and a dual human/agent interface on the same kernel. |
| Boutiques | Invocation schema, containers, command generation. Used by CBRAIN. | Plugin syntax is taken. Residual: run life cycle and receipts, not a new descriptor. |
| Neurodesk (*Nature Methods*; still shipping 2026) | 100+ containers; desktop, CLI, notebooks, cloud, HPC. 2026 releases add coding-agent remotes (OpenCode/Codex). | Highest environment-platform blocker. Residual: workflow-level orchestration, fail-closed receipts, and a controlled human-vs-agent study — not image packaging. |
| CBRAIN | Web portal to distributed HPC; Boutiques integration. | Cloud-portal first. Residual: installable local-first mode under the *same* receipt contract. |
| brainlife.io | 400+ apps; DOI-addressed workflows; OpenNeuro import. | Cloud ecosystem. Residual: deployment independence and a no-egress path for restricted MRI. |
| ChRIS | Medical-image plugin workflows; NiiVue. | Plugin platform exists. Residual: BIDS-native research receipts and local/HPC parity, not another plugin bus. |
| Flywheel / QMENTA / LONI | Data/workflow management, Gears, governance. | Commercial/service platforms. Residual: open, independently installable components and a published evaluation. |
| DataLad / ReproNim / BABS | Re-executable, versioned provenance for BIDS Apps on SGE/Slurm. | Provenance of large BIDS-App jobs is taken. Residual: a reconstructability *test* and a receipt that also covers approval, QC-not-run, and refused egress — not a second DataLad. |
| NeuroClaw (2026) | Agentic neuroimaging assistant; pinned envs; Docker; checkpoints; JSONL audit; NeuroBench. | Highest **agent-workbench** blocker. Residual: agent is optional and cannot execute; Paper 3 already owns the agent score. |
| CyberNeuro (2026) | Local-only Windows workbench; planner/validate/dispatch; no-egress tests; JSON receipts; approval. | Highest **privacy-workbench** blocker. Residual: the same fail-closed boundary on Linux + Slurm, with a human-only path that is first-class. |
| NeuroPilot (2026) | Agent pipeline; BIDS standardization; approval on consequential steps; ledger. | Approval-gated agent pipelines exist. Residual: the approval object is the same as a human-submitted run. |
| Brain Researcher (2026) | Local agentic harness; commitment and claim cards; reproducibility ladder. | Live-run claim audit. Cite; do not clone. Different object: their card is a scientific claim; your receipt is an execution record. |
| BCER Agent (MICCAI 2026) | Compilation, artifact binding, bounded local recovery on long MRI chains. | Recovery of a failed node exists. Residual: *silent* success of the platform (green UI, bad or leaked artifact), not restart policy. |
| Paper2Agent (*Nature*, 2026) | A paper becomes an MCP agent. | Different object. Do not become a paper-agent host and call it a workbench. |

**One-sentence answers you will need.**

- Neurodesk asks whether **tools can run anywhere**. NeuroInsight asks whether **this run can be reconstructed, and whether the platform hid a failure**, locally and on Slurm.
- NeuroClaw asks whether an **agent can execute neuroimaging**. NeuroInsight asks whether a **human and an agent proposal are the same object** to one fail-closed kernel.
- CyberNeuro asks whether a **Windows box can keep data local**. NeuroInsight asks whether the **same no-egress and approval rules hold when the backend is Linux or Slurm**.
- BABS asks whether a **BIDS App job has DataLad provenance**. NeuroInsight asks whether an **independent person can reconstruct the run from the receipt**, including who approved it and which QC did not run.
- NeuroAgentBench asks whether an **agent’s artifact is scientifically valid**. NeuroInsight asks whether the **workbench reported the run honestly**.

---

## 2. Methods worth keeping (Paper 5)

### N1. Dual-interface invariant (agent is a proposer, never an executor)

**Limitation.** 2026 split the field: environment platforms (Neurodesk), cloud portals (brainlife, CBRAIN), and agent workbenches (NeuroClaw, CyberNeuro, NeuroPilot, Brain Researcher). Almost none pre-register that a human click and an agent proposal are the same object. Agent products grow a second, quieter path around the checks the UI shows.

**Method.** One execution kernel. The only write that starts a run is an **approved run request**. A human form and an agent proposal compile to the same request type. The kernel:

1. Validates the request (schema, BIDS, allowlisted image digest, resource quota, data-boundary policy).
2. Requires explicit approval for execution, overwrite, HPC submission, and any network path.
3. Emits one receipt format regardless of proposer.
4. Refuses unrestricted shell and any model-written command that is not an allowlisted plugin invoke.

The agent cannot call the executor. If SciCap or SciGuard are present, they run on this request as they would on a human request. Their detections are not Paper 5 results.

**Test.** Blueprint E6, but the primary contrast is not “agent is faster.” It is: **receipt equality** and **incorrect-submission rate** under the same checks. If the agent path can complete a run the human path would reject, N1 has failed.

This is the method that answers the name “NeuroInsightAgent.” The agent is a condition, not the title.

### N2. Platform silent success as a first-class endpoint

**Limitation.** Platforms demo the happy path. NeuroAgentBench (Paper 3) scores *agent* false success. BCER recovers a failed node. Nobody treats **the workbench lying** as a primary number: UI or API reports complete when QC failed, the image digest drifted, a stage was skipped, or data left the declared boundary.

**Method.** For every run record:

| Field | Meaning |
|---|---|
| `execution_reported_complete` | UI/API said the job finished |
| `required_qc_passed` | Every check the plugin declared as required actually ran and passed |
| `digest_matches` | Executed image digest equals the approved digest |
| `boundary_held` | No undeclared egress or path escape |
| `platform_silent_success` | Reported complete, and QC failed **or** digest mismatch **or** boundary broken **or** a required stage did not run |

Inject failures (blueprint E2): missing image, invalid parameter, interrupted worker, OOM, unavailable container, digest swap, attempted outbound on restricted data. Count recovered, irrecoverable, and silent. Debugging time is secondary.

Do not call this NeuroAgentBench. Paper 3 scores the agent’s artifact. Paper 5 scores the platform’s report.

### N3. Cross-environment equivalence with a declared tolerance

**Limitation.** Neurodesk and BIDS Apps already sell portability. Papers still treat “we also submitted to Slurm” as a feature. Numerical identity across CPU/GPU is often false, and then quietly ignored.

**Method.** Before any paired run, lock per-artifact comparison rules:

- byte identity where it is scientifically required (manifests, hashes, parameters, image digest)
- declared numeric tolerance where it is not (segmentation volumes, connectome weights)
- `environment_divergence` when local and Slurm disagree beyond tolerance
- `comparison_unknown` when an artifact needed for the comparison is missing — not a pass

Primary number for this arm: fraction of paired runs that meet the locked rule, plus the divergence list. Hardware-specific differences are reported, not averaged away.

This is H2 made into a protocol. Running on two backends is not the method. **Scoring the pair** is.

### N4. Reconstructability receipt (not a log dump)

**Limitation.** BABS/DataLad already produce re-executable provenance. RO-Crate and PROV already package runs. EVI already graphs computational evidence. NeuroClaw already writes JSONL audits. A zip of logs is not a contribution.

**Method.** A receipt is a contract with a closed checklist. An independent reader, without the original operator, must be able to answer:

- who or what proposed the run, and who approved it
- input hashes and BIDS identities
- plugin version and image digest
- parameters and resource request
- environment (local container vs Slurm job id)
- which QC checks passed, failed, or **did not run**
- outputs and their hashes
- whether the data boundary held

Encode with PROV / RO-Crate / DataLad. Do not invent a provenance language.

**Test.** Blueprint E5: blinded reconstruct and diagnose-from-receipt. Gold is successful reconstruction and correct failure class. Time and missing-field rate are secondary. If BABS receipts already suffice on the BIDS-App subset, N4 has no residual — say so and emit BABS/RO-Crate instead of a paper claim.

### N5. Matched setup-burden protocol

**Limitation.** Every platform claims easier setup. The 2025 *Imaging Neuroscience* survey already taxonomized BIDS Apps, Neurodesk, Boutiques, Nipype, Pydra, CBRAIN, and brainlife. Screenshots are not evidence.

**Method.** Freeze tasks and validity criteria first. Counterbalance NeuroInsight (human-only) against at least:

- documented CLI + the same containers
- Nipype or Pydra, same stages
- a BIDS App, same algorithm
- one accessible portal (CBRAIN or brainlife) only on like-for-like tasks

Outcomes: independently verified completion, setup minutes, interventions, configuration-error count, and N2 silent success. Expertise is a factor, not a covariate you hide. IRB determination if you run a user study.

This is H1. It is the Software Toolbox method. Without it, Paper 5 is a README.

### N6. Fail-closed data boundary (testable, not a banner)

**Limitation.** CyberNeuro already measured no-egress on a Windows box. NeuroInsight’s blueprint already forbids automatic upload of restricted MRI. A privacy paragraph is not a method.

**Method.** A decision rule on every run request:

| Request | Kernel decision |
|---|---|
| Local/HPC plugin, no network, paths inside workspace | Eligible after approval |
| Any external model API with image bytes or paths to restricted MRI | `REJECT` |
| Undeclared outbound during a run | fail the run; `boundary_held = false`; N2 silent success if the UI still says complete |
| Metadata-only agent help | Allowed only if the policy says so and no image leaves the box |

Test on Linux local **and** Slurm, including a disconnected-host condition and an attempted-exfil fixture. CyberNeuro owns the Windows measurement. The residual is the same rule on the backends neuroimaging labs actually use.

Research use only. No diagnostic or FDA language.

---

## 3. Methods that belong next door

| Method | Owner |
|---|---|
| Late binding, invoke ALLOW / REJECT / ABSTAIN | SciCap (Paper 1) |
| Edge-level PASS / FAIL / UNKNOWN preflight | SciGuard (Paper 2) |
| Layered artifact oracle, agent false success, abstention gold | NeuroAgentBench (Paper 3) |
| Scoped literature attribution | EvidenceGraph (Paper 4) |
| Containerized tool availability across OS / HPC / cloud | Neurodesk; wrap, do not replace |
| DataLad-tracked BIDS App jobs on Slurm | BABS; emit or call |
| Agentic closed-loop neuroimaging execution | NeuroClaw; cite as comparator |
| Windows no-egress agent workbench | CyberNeuro; cite |
| Live-run claim cards | Brain Researcher / NEURA; cite |
| Boutiques / CWL / ChRIS plugin schemas | Prior art; import |

Paper 5 may integrate Papers 1–3 as libraries. Those tables do not become this paper’s novelty and must not be republished as confirmatory results for Papers 1–3 without a cross-reference.

---

## 4. Feature gaps that look like methods but are not

- “First neuroimaging platform” / “first reproducible container pipeline.” False since BIDS Apps, Nipype, Neurodesk.
- “First agent workbench.” False in 2026: NeuroClaw, CyberNeuro, NeuroPilot, Brain Researcher, Neurodesk’s coding-agent remotes.
- “We combined local, HPC, BIDS, QC, and a UI.” A product hypothesis, not a method. The blueprint already says so.
- A new plugin language. Boutiques, CWL, ChRIS, Flywheel Gears.
- Replacing Nipype, Pydra, Nextflow, or Slurm.
- “Nature Methods because the UI is nicer.”
- Claiming SciCap invoke, SciGuard unsafe-acceptance, or NeuroAgentBench false-success as platform results.
- A biological discovery from a demo FastSurfer run.
- Clinical or diagnostic claims.

If the competitor matrix shows no residual after N1–N6, contribute upstream (Neurodesk, BABS, Boutiques) and write JOSS, not a methods paper.

---

## 5. Recommended methods stack

1. **Decision rule (N1 + N6):** one kernel; agent proposes; approval required; restricted MRI never leaves the box.
2. **Representation (N4):** receipt contract encoded as PROV / RO-Crate / DataLad, including approval, digest, QC-not-run, and boundary.
3. **Evaluation (N2 + N3 + N5):** platform silent success under injection; local–Slurm equivalence with locked tolerances; matched setup-burden against Neurodesk / BIDS App / Nipype.

**Venue split (do not conflate).**

| Strongest output | Venue |
|---|---|
| Installable workbench, five plugins, receipts, independent install reports | ***Imaging Neuroscience* Software Toolbox** — default |
| Thin residual over Neurodesk + BABS | *JOSS* / *SoftwareX* |
| Broad biological utility plus a real powered imaging study | *PLOS Computational Biology* Software |
| A new general life-science method, not integration | Then, and only then, *Nature Methods* |

**Do not design the project as a Nature paper.** Neurodesk already occupies accessible reproducible environments in *Nature Methods*. NeuroClaw already occupies agentic neuroimaging execution. Your differentiator is **one fail-closed kernel and honest platform numbers**, not an agent and not a desktop.

---

## 6. Pilot that decides these are real methods

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

## 7. Decision

Turn **one kernel with an optional proposer**, **platform silent success**, **declared local–Slurm equivalence**, **reconstructability receipts**, and a **matched setup-burden protocol** into the Paper 5 methods. Leave contracts to SciCap, preflight to SciGuard, agent scoring to NeuroAgentBench, literature binding to EvidenceGraph, containers to Neurodesk, BIDS-App provenance to BABS, and agentic execution to NeuroClaw.

That is the limitation set this field will grant NeuroInsight. The workbench is not the contribution. The invariant and the numbers are.
