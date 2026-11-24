# Aircraft subset

Builds the SSD, parameter sets, and SSD-synced SysML for a nested aircraft
composition: three subsystems with connected signal ports and an applied
`NominalSet`.

## Run

From the `pyssp_dev` workspace root, with the workspace venv active:

```bash
bash repos/pyssp_sysml/examples/cli_usage.sh
```

| Artifact | Path |
| --- | --- |
| SSD | `build/examples/cli_usage/SystemStructure.ssd` |
| SSV directory | `build/examples/cli_usage/parameter_sets/` |
| Bootstrapped SysML | `build/examples/cli_usage/new_architecture/architecture.sysml` |
| SSD-synced SysML | `build/examples/cli_usage/synced_sysml/` |

Expected output:

```text
build/examples/cli_usage/SystemStructure.ssd
build/examples/cli_usage/parameter_sets
build/examples/cli_usage/new_architecture/architecture.sysml
build/examples/cli_usage/synced_sysml
```

SSD only:

```bash
pyssp generate ssd \
  --architecture repos/pyssp_sysml/examples/aircraft_subset \
  --composition AircraftComposition \
  --core-definitions \
  --output build/examples/aircraft_subset/SystemStructure.ssd
```

## Setup

Activate the workspace venv (this checkout: `source ../venv/bin/activate`); the
`pyssp` console script comes from the editable install of this package. See the
workspace `README.md`.

## What the definition encodes

`AutopilotModule`, `MissionComputer`, and `Environment` are the parts;
`AircraftComposition` wires `autopilot.autopilotCmd` to
`missionComputer.autopilotInput`, and the environment's orientation, location,
and flight status back into the autopilot. The applied `NominalSet` supplies
`autopilot.parameters.note`, `waypointCount`, and `waypointX_km`. The role
markers and parameter-set contract are owned by
[`docs/roles.md`](../../../pyssp_sysml_definitions/docs/roles.md).

## Composition

`AircraftComposition` instantiates the three part definitions, binds the
`NominalSet` attributes to the autopilot parameter interface, and connects the
five signal ports between autopilot, mission computer, and environment.
`AutopilotModule` declares `fmu_meta.source`; an SSP packaging run would need
that on every leaf, plus the built FMUs at those paths.
