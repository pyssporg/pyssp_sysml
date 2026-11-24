# Parameter-set examples

Four SysML models, each encoding one parameter-set shape: identity, explicit
mapping, multiple disjoint sets, and a nested component path.

Every model imports the shared `PysspCore` vocabulary, so each command passes
`--core-definitions`. The vocabulary and its roles are owned by
[`docs/roles.md`](../../../pyssp_sysml_definitions/docs/roles.md).

## Run

From the `pyssp_dev` workspace root, with the workspace venv active, the
identity model is the smallest path:

```bash
pyssp generate ssv \
  --architecture repos/pyssp_sysml/examples/parameter-sets/identity \
  --composition IdentityComposition \
  --core-definitions \
  --output-dir build/examples/parameter-sets/identity/parameter_sets

pyssp generate ssd \
  --architecture repos/pyssp_sysml/examples/parameter-sets/identity \
  --composition IdentityComposition \
  --core-definitions \
  --output build/examples/parameter-sets/identity/SystemStructure.ssd
```

| Artifact | Path |
| --- | --- |
| SSV | `build/examples/parameter-sets/identity/parameter_sets/NominalSet.ssv` |
| SSD | `build/examples/parameter-sets/identity/SystemStructure.ssd` |

Expected output:

```text
Wrote build/examples/parameter-sets/identity/parameter_sets/NominalSet.ssv
SSD written to build/examples/parameter-sets/identity/SystemStructure.ssd
```

## Explicit mapping

Different set and interface names, plus an SSM:

```bash
pyssp generate ssv \
  --architecture repos/pyssp_sysml/examples/parameter-sets/explicit \
  --composition ExplicitComposition \
  --core-definitions \
  --output-dir build/examples/parameter-sets/explicit/parameter_sets

pyssp generate ssd \
  --architecture repos/pyssp_sysml/examples/parameter-sets/explicit \
  --composition ExplicitComposition \
  --core-definitions \
  --output build/examples/parameter-sets/explicit/SystemStructure.ssd

pyssp generate ssm \
  --architecture repos/pyssp_sysml/examples/parameter-sets/explicit \
  --composition ExplicitComposition \
  --core-definitions \
  --output-dir build/examples/parameter-sets/explicit/parameter_mappings
```

Artifacts: `parameter_sets/NominalSet.ssv`, `parameter_mappings/NominalSet_autopilot.ssm`,
and `SystemStructure.ssd` under `build/examples/parameter-sets/explicit/`.

## Multiple disjoint sets

Two sets applied to one component:

```bash
pyssp generate ssv \
  --architecture repos/pyssp_sysml/examples/parameter-sets/multiple \
  --composition MultipleSetComposition \
  --core-definitions \
  --output-dir build/examples/parameter-sets/multiple/parameter_sets

pyssp generate ssd \
  --architecture repos/pyssp_sysml/examples/parameter-sets/multiple \
  --composition MultipleSetComposition \
  --core-definitions \
  --output build/examples/parameter-sets/multiple/SystemStructure.ssd
```

Artifacts: `parameter_sets/Counts.ssv`, `parameter_sets/Gains.ssv`, and
`SystemStructure.ssd` under `build/examples/parameter-sets/multiple/`.

## Nested component path

A set applied to a nested component path, then regenerated SysML from the SSD:

```bash
pyssp generate ssv \
  --architecture repos/pyssp_sysml/examples/parameter-sets/nested \
  --composition NestedPathComposition \
  --core-definitions \
  --output-dir build/examples/parameter-sets/nested/parameter_sets

pyssp generate ssd \
  --architecture repos/pyssp_sysml/examples/parameter-sets/nested \
  --composition NestedPathComposition \
  --core-definitions \
  --output build/examples/parameter-sets/nested/SystemStructure.ssd

pyssp generate sysml \
  --ssd build/examples/parameter-sets/nested/SystemStructure.ssd \
  --output build/examples/parameter-sets/nested/recovered.sysml
```

Artifacts: `parameter_sets/NominalSet.ssv`, `SystemStructure.ssd`, and
`recovered.sysml` under `build/examples/parameter-sets/nested/`.

## Setup

Activate the workspace venv (this checkout: `source ../venv/bin/activate`); the
`pyssp` console script comes from the editable install of this package. See the
workspace `README.md`.

## What each model encodes

| Model | Contract |
| --- | --- |
| `identity/` | Matching set and interface names; the SSD binding uses `prefix="autopilot."` and needs no SSM. |
| `explicit/` | Different names; the SSM renames `n_waypoints` to `autopilot.waypointCount` and maps the list elements to `autopilot.waypointX_km[i]`; the SSD also carries the mapping inline. |
| `multiple/` | Two disjoint sets on one component; targets `controller.count` and `controller.gain`. |
| `nested/` | The set lands on `outer.inner.k`; the regenerated SysML reconstructs `part def outer` with `part inner` and the parameter bind. |

## Deliberately not shown

- A set inside a set. Not supported; see `IMP-001`.
- Set inheritance or union with `:>` and `:>>`. Proposed only; see `IMP-001`.
- Top-level composition parameter bags. Rejected by the dialect.
- Overlapping sets on one component. Rejected; documented in `INFO-016`.
