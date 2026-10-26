# Agent instructions — shared fixture (S0)

Build this before SciCap, SciGuard, NeuroAgentBench, and NeuroInsight. EvidenceGraph does not need these imaging bytes.

## Mission

One frozen, licensed, tiny imaging world. Papers 1, 2, 3, and 5 all cite the same pin file.

## Do not

- Commit NIfTI, DICOM, or any image bytes.
- Download HCP or restricted data.
- Invent a layout that is not BIDS.

## Create

```text
shared/
  AGENTS.md
  pins.yaml
  LICENSES.md
  data/manifests/<accession>.yaml
  fixtures/valid/          # pointers only, or tiny synthetic JSON sidecars
  fixtures/invalid/
    missing_space/
    dk_as_dkt/
    labels_t1w_on_dwi/
    digest_swap/
```

## `pins.yaml` contract

```yaml
schema_version: 0.1
bids_validator: "<version>"
container:
  name: neurodesk-or-apptainer-image
  digest: "sha256:<pin>"
dataset:
  source: OpenNeuro
  accession: "<ds00xxxx>"
  doi: "<doi>"
  retrieved: "YYYY-MM-DD"
  subjects: ["sub-01"]
  bytes_in_git: false
```

## Invalid family (required)

| Fixture | Intended failure | Used by |
|---|---|---|
| `missing_space/` | sidecar omits `Space` / `space-` | SciCap ABSTAIN; SciGuard UNKNOWN |
| `dk_as_dkt/` | DK labels declared as DKT | SciCap REJECT |
| `labels_t1w_on_dwi/` | T1w parcellation wired to DWI, no transform | SciGuard FAIL; NAB abstain/reject |
| `digest_swap/` | image digest ≠ approved digest | NeuroInsight N2 |

## Done when

- `bids-validator` would pass the valid set (document the command; skip if bytes are not local).
- Each invalid fixture has a README stating the **named** expected check.
- A clean machine can fetch the snapshot from the manifest.
- `shared/LICENSES.md` lists dataset and container licenses.

## Tests

`shared/tests/test_pins.py`: pins.yaml parses; every invalid fixture directory exists; `bytes_in_git` is false; no file under `shared/` has suffix `.nii` or `.nii.gz`.
