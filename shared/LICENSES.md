# Shared fixture licenses

Recorded 26 October 2026. No image bytes are stored in git.

| Object | Identifier | License (as stated by the source) |
|---|---|---|
| OpenNeuro `ds000003` (Rhyme judgment) | DOI [10.18112/openneuro.ds000003.v1.0.0](https://doi.org/10.18112/openneuro.ds000003.v1.0.0) | Dataset README: [PDDL 1.0](https://opendatacommons.org/licenses/pddl/1.0/). OpenNeuro distribution is public; do not add PHI. |
| Neurodesktop image tag `2026-06-09` | `ghcr.io/neurodesk/neurodesktop/neurodesktop:2026-06-09` | Neurodesk project license as published on [NeuroDesk/neurodesktop](https://github.com/NeuroDesk/neurodesktop). Digest pinned in `pins.yaml`. Bytes not in git. |
| BIDS Validator 3.0.2 | [bids-standard/bids-validator](https://github.com/bids-standard/bids-validator) | MIT (upstream). Used as the named validator; not vendored here. |
| Boutiques | Glatard et al., 2018; schema on GitHub | BSD-style / project license on [boutiques/boutiques](https://github.com/boutiques/boutiques). SciCap must not replace the schema. |
| BIDS specification | [bids-specification](https://bids-specification.readthedocs.io/) | CC-BY. Field names (`space-`, `atlas-`, `T1w`) are reused, not re-invented. |

Invalid fixtures under `shared/fixtures/invalid/` are synthetic JSON sidecars. They point at paths that must not be committed as NIfTI.
