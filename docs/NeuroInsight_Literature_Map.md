# NeuroInsight literature map

**Paper 5 — fail-closed execution kernel and platform scoring**  
Scoping map and novelty matrix · 26 October 2026 · search cutoff 26 October 2026

**Status.** Claim-setting map, not a PRISMA review and not a finding that NeuroInsight works. No confirmatory numbers are claimed. Re-check bibliographic metadata before any manuscript.

**Bottom line.** A new neuroimaging workbench, a new plugin language, a new scheduler, or “first agent platform” is not a defensible contribution. Neurodesk, brainlife.io, CBRAIN, ChRIS, BIDS Apps, Boutiques, Nipype/Pydra, and BABS already occupy environment, portal, plugin, and provenance slots. NeuroClaw, CyberNeuro, and NeuroPilot already occupy agentic MRI workbenches. The residual that still looks testable is **one kernel** (human and agent compile to the same approved request; the agent cannot execute), **platform silent success** under injected failure, a **scored local–Slurm pair** with locked tolerances, and a **reconstructability receipt** (approval, digest, hashes, QC passed/failed/**did not run**, boundary). Not first platform.

---

## 1. Search protocol

### 1.1 Sources queried on 26 October 2026

Web search over publisher sites, arXiv, PMC, official docs, and GitHub, plus snowball from the locked methods and Paper 6 prior-art inventory. Clusters match the systems named in [`NeuroInsight_Limitations_to_Methods.md`](NeuroInsight_Limitations_to_Methods.md).

| Cluster | Query family | Meant to catch |
|---|---|---|
| A | Neurodesk + Nature Methods + 2026 coding-agent remotes | Environment platform; OpenCode/Codex/T3 Code |
| B | brainlife / CBRAIN / ChRIS / Flywheel | Cloud and plugin portals |
| C | BIDS Apps + Boutiques + Nipype + Pydra | Descriptors and workflow engines |
| D | BABS + DataLad + Slurm + RO-Crate / PROV | Provenance of BIDS-App jobs |
| E | NeuroClaw / NeuroDiscovery + CyberNeuro + NeuroPilot | 2026 agent workbenches |

### 1.2 What this map is not

- Not an exhaustive screen with recorded inclusion counts.
- Not a claim that 2026 preprints will remain the version of record.
- Not a license to republish SciCap, SciGuard, or NeuroAgentBench tables as Paper 5 results.
- Peer-review status of NeuroClaw, CyberNeuro, and NeuroPilot must be rechecked at submission.

### 1.3 How to read threat levels

| Level | Meaning for NeuroInsight |
|---|---|
| **Blocker** | Already implements the object Paper 5 would otherwise call novel. Do not claim that object. |
| **High** | Same job, different encoding. Must be a baseline or a hard differentiator. |
| **Must-cite baseline** | Fair experimental comparator even if conceptually older. |
| **Reuse** | Emit or call this standard; do not replace it. |

---

## 2. Residual (locked)

Grant every system below. What remains is N1–N6 as specified in [`NeuroInsight_Methods.md`](NeuroInsight_Methods.md):

1. **One kernel.** Human form and agent proposal compile to the same run request. Approval is required. The agent cannot call execute. Receipt format is identical.
2. **Platform silent success.** UI/API said complete ∧ (required QC failed ∨ digest mismatch ∨ boundary broken ∨ a required stage did not run). Paper 3 scores the agent artifact; Paper 5 scores the platform report.
3. **Local–Slurm pair scored**, not merely submitted. Locked byte or numeric tolerances. Missing compare artifact → `comparison_unknown`. Not v0 until Slurm exists.
4. **Reconstructability receipt.** Independent reader can answer proposer, approver, digest, hashes or `bytes_unavailable`, plugin version, parameters, backend, QC passed/failed/**did not run**, boundary. Encode as PROV / RO-Crate / DataLad.

If those four collapse into a Neurodesk wrapper plus a BABS export, the methods paper is a no-go (JOSS / upstream).

---

## 3. Environment, portal, and plugin platforms

### 3.1 Neurodesk — highest environment-platform blocker

Renton et al., *Nature Methods* (2024). Accessible, portable containers; desktop, CLI, notebooks; local, HPC, and cloud. Official publications page: Nature Methods 21(5), 804–808, 2024. Live docs: https://neurodesk.org/.

**2026 refresh (not a 2026 Nature Methods paper).** Release history current as of 2026-09-23:

- 2025-12-20: Pydra and Nipoppy added to Neurodesktop.
- 2026-04-28: Slurm dashboard; OpenCode, Codex, and Claude agent apps.
- 2026-09-23: T3 Code remote-server support (OpenCode/Codex providers); one-link pairing.

Neurodesk asks whether **tools can run anywhere**. It now also ships coding-agent remotes. That kills “first accessible environment” and “first coding agent on neuroimaging containers.”

**Residual.** Workflow-level fail-closed kernel, honest platform numbers (silent success, QC-not-run), and a human-vs-agent study on the **same request object** — not image packaging and not a desktop.

### 3.2 brainlife.io — cloud ecosystem

Hayashi et al. / brainlife.io platform paper (PMC10274934). 400+ apps, DOI-addressed workflows, OpenNeuro import, typed datatypes, opportunistic compute. https://brainlife.io/

**Residual.** Deployment independence and a no-egress path for restricted MRI under the same receipt as local/Slurm. Do not rebuild a cloud app store.

### 3.3 CBRAIN — web portal to distributed HPC

Sherif et al. lineage; Boutiques integration; BIDS Apps; CARMIN-style remote execution. Portal-first.

**Residual.** Installable local-first mode under the **same** receipt contract as the portal path. Do not write another web HPC broker.

### 3.4 ChRIS — medical-image plugin bus

FNNDSC ChRIS: plugin workflows, pfcon, NiiVue. https://chrisproject.org/

**Residual.** BIDS-native research receipts and local/HPC parity, not another plugin bus. Import plugin conventions; do not invent a cube language.

### 3.5 BIDS Apps — portable invocation

Gorgolewski et al., *PLOS Comput Biol* (2017). `bids /out participant`. Execution spec already describes typed CLI inputs.

**Residual.** Multi-tool life cycle, QC-not-run as a first-class field, and dual human/agent interface on one kernel. Wrap the convention. Do not redefine it.

### 3.6 Boutiques — invocation schema

Glatard et al., *GigaScience* (2018). JSON descriptors, container hash, command generation. Used by CBRAIN and later Nipoppy.

**Residual.** Run life cycle and receipts, not a new descriptor. Plugin syntax is taken.

---

## 4. Engines and BIDS-App provenance

### 4.1 Nipype / Pydra — do not write a scheduler

Nipype (Gorgolewski et al., 2011): typed interfaces, DAGs, provenance. Pydra is the Nipype 2.0 dataflow engine (typed tasks, cache, Slurm/SGE workers). Neurodesk added Pydra on 2025-12-20.

**Residual.** Non-programmer onboarding and operator-level receipts, not a better engine. Steal the executor. Paper 5 v0 is a thin local-container dry-run, not Pydra.

### 4.2 BABS / DataLad — blocker for “we added Slurm provenance”

Zhao et al., *Imaging Neuroscience* (BIDS App Bootstrap). DataLad-tracked BIDS App jobs on SGE/Slurm; machine-readable re-executable provenance. https://github.com/PennLINC/babs

**Residual.** A reconstructability *test* and a receipt that also covers **who approved**, **which QC did not run**, and **refused egress** — not a second DataLad. If BABS receipts already suffice on the BIDS-App subset, emit BABS/RO-Crate and do not claim N4 novelty on that subset.

---

## 5. 2026 agent workbenches (do not claim first)

### 5.1 NeuroClaw / NeuroDiscovery — highest agent-workbench blocker

Wang et al., technical report, arXiv:2604.24696 (27 April 2026). Closed-loop agentic neuroimaging; pinned envs; Docker; checkpoints; JSONL audit; NeuroBench. Public git evolved to NeuroDiscovery: https://github.com/CUHK-AIM-Group/NeuroClaw (repo now NeuroDiscovery). Homepage historically https://cuhk-aim-group.github.io/NeuroClaw/.

NeuroClaw asks whether an **agent can execute neuroimaging**.

**Residual.** Agent is optional and **cannot execute**. Paper 3 already owns the agent artifact score. Do not vendor `claw-shell` or the NeuroBench GPT rubric.

### 5.2 CyberNeuro — highest privacy-workbench blocker

arXiv:2607.28841 (30 July 2026). Windows-only local workbench; Planner / Validator / Dispatcher / Reporter; JSON receipts; no-egress and disconnected-host tests on Windows/WSL. Product host: https://wanda-cyberbench.com. **No cloneable Linux kernel found on 26 October 2026.**

CyberNeuro asks whether a **Windows box can keep data local**.

**Residual.** The same fail-closed boundary on **Linux local and Slurm**, with a human-only path that is first-class. Copy the *test design*, not the Windows measurement. Dispatcher must not be an agent.

### 5.3 NeuroPilot — approval-gated agent pipelines exist

Chen et al., arXiv:2608.07541 (2026). Agent skills for BIDS standardization, preprocessing, and QC; human sign-off on consequential exports; append-only ledger. Same product host as CyberNeuro. Research git not found (unrelated VS Code “NeuroPilot” exists).

**Residual.** The approval object is the **same** as a human-submitted run request. Do not grow a second, quieter agent path.

---

## 6. 26 October 2026 literature updates (five)

These are the refresh notes for this map. They are not evaluation results.

1. **Neurodesk is a 2024 *Nature Methods* paper, still shipping in 2026.** Do not write “Neurodesk 2026 Nature Methods.” The 2026 increment is coding-agent remotes (OpenCode, Codex, Claude; then T3 Code remotes on 2026-09-23) plus a Slurm dashboard (2026-04-28). Environment + agent-remote slots are taken.
2. **Neurodesk added Pydra (and Nipoppy) on 2025-12-20.** A Paper 5 scheduler or “we brought Pydra to containers” claim is closed. v0 must not write a workflow engine.
3. **NeuroClaw (arXiv:2604.24696) is public and has been renamed NeuroDiscovery** on the CUHK-AIM-Group git. NeuroBench expanded beyond processing into model training. Highest blocker for “first agent workbench.” Cite the report; do not clone it into this folder.
4. **CyberNeuro (arXiv:2607.28841) measured no-egress on Windows**, with JSON receipts and a Planner ≠ Dispatcher split. No Linux/Slurm kernel was found. N6 residual is the same REJECT / undeclared-outbound rule on the backends labs actually use.
5. **NeuroPilot (arXiv:2608.07541) already gates consequential steps and writes an append-only approval ledger.** Residual is receipt equality: agent proposal and human submit are one object. BABS remains the BIDS-App/Slurm provenance baseline; N4 must not be a second DataLad.

---

## 7. Work-by-work novelty matrix

| Work | Threat | NeuroInsight must add or test |
|---|---|---|
| Nipype (2011) | Must-cite engine | Do not rebuild; steal executor |
| BIDS Apps (2017) | Must-cite invocation | Wrap `bids /out`; do not redefine |
| Boutiques (2018) | **Blocker for new plugin language** | Life cycle + receipts |
| CBRAIN | High (portal + Boutiques) | Local-first, same receipt |
| ChRIS | High (plugin bus) | BIDS-native receipts; no new cubes |
| brainlife.io | High (cloud apps + DOI workflows) | No-egress + installable kernel |
| Neurodesk (2024; 2026 remotes) | **Blocker for environment / “tools anywhere”** | Silent success + reconstructability, not packaging |
| Pydra (Neurodesk 2025-12) | **Blocker for new engine** | Thin container runner only |
| BABS / DataLad | **Blocker for Slurm provenance** | Approval + QC-not-run + refused egress on the receipt |
| NeuroClaw / NeuroDiscovery (2026) | **Blocker for first agent workbench** | Agent cannot execute; Paper 3 owns artifact score |
| CyberNeuro (2026) | **Blocker for Windows no-egress** | Same rule on Linux + Slurm; human path first-class |
| NeuroPilot (2026) | **High for approval-gated agents** | One approval object for human and agent |
| PROV / RO-Crate / DataLad | Reuse | Encode N4; do not invent a language |
| SciCap / SciGuard / NAB | Other papers | Libraries only; do not republish their tables |

---

## 8. What would not be novel (do not write these sentences)

- “The first neuroimaging platform” or “first reproducible container pipeline.”
- “The first agent workbench.”
- “We combined local, HPC, BIDS, QC, and a UI.”
- “A new plugin language.”
- “We replaced Nipype, Pydra, Nextflow, Slurm, Neurodesk, or BABS.”
- “Nature Methods novel because the UI is nicer.”
- Claiming SciCap invoke, SciGuard unsafe-acceptance, or NeuroAgentBench false-success as platform results.

---

## 9. Seed bibliography (verified starting set)

Links checked as live search hits on 26 October 2026. Lock author/volume/page before submission. Do not treat this list as results.

1. Gorgolewski et al. (2011). Nipype. *Front Neuroinform*. https://doi.org/10.3389/fninf.2011.00013
2. Gorgolewski et al. (2016). BIDS. *Sci Data*. https://doi.org/10.1038/sdata.2016.44
3. Gorgolewski et al. (2017). BIDS Apps. *PLOS Comput Biol*. https://doi.org/10.1371/journal.pcbi.1005209
4. Glatard et al. (2018). Boutiques. *GigaScience*. https://doi.org/10.1093/gigascience/giy016
5. Renton et al. (2024). Neurodesk. *Nat Methods* 21, 804–808. https://www.nature.com/articles/s41592-024-02237-2 — PMC: https://pmc.ncbi.nlm.nih.gov/articles/PMC11180540/ — releases: https://neurodesk.org/overview/release-history/
6. Pydra. https://nipype.github.io/pydra/ — Neurodesk 2025-12-20 note: https://neurodesk.org/overview/release-history/
7. Zhao et al. BABS. *Imaging Neuroscience*. https://direct.mit.edu/imag/article/doi/10.1162/imag_a_00074/119046 — https://github.com/PennLINC/babs
8. brainlife.io platform paper. https://pmc.ncbi.nlm.nih.gov/articles/PMC10274934/ — https://brainlife.io/
9. CBRAIN (Sherif lineage; Boutiques/BIDS integration). https://portal.cbrain.mcgill.ca/
10. ChRIS. https://chrisproject.org/
11. W3C PROV-O. https://www.w3.org/TR/prov-o/
12. RO-Crate. https://www.researchobject.org/ro-crate/specification
13. Wang et al. (2026). NeuroClaw. arXiv:2604.24696. https://arxiv.org/abs/2604.24696 — git: https://github.com/CUHK-AIM-Group/NeuroClaw
14. CyberNeuro (2026). arXiv:2607.28841. https://arxiv.org/abs/2607.28841
15. Chen et al. (2026). NeuroPilot. arXiv:2608.07541. https://arxiv.org/abs/2608.07541

---

## 10. Decision for this folder

Implement the dry-run kernel (validate → `--approve` → boundary → receipt → `platform_silent_success`). Do not clone `neuroinsight_research`. Do not name a binary `neuroinsight-agent`. Do not run FastSurfer on GPU. Do not require a model API. If the kernel still does N1–N6 after the LLM is stripped, Paper 5 is intact.
