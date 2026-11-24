# Analysis / SspModel

Generates the analysis artifacts for a position servo: one exportable
`SspModel` with two `Analysis` compositions over two applied scenarios.

## Run

From the `pyssp_dev` workspace root, with the workspace venv active:

```bash
pyssp generate analysis \
  --architecture repos/pyssp_sysml/examples/analysis \
  --composition test_baseline \
  --model position_servo \
  --core-definitions \
  --output-dir build/examples/analysis/test_baseline
```

| Artifact | Path |
| --- | --- |
| Applied scenario | `build/examples/analysis/test_baseline/NominalScenario.ssv` |
| Parameter mappings | `build/examples/analysis/test_baseline/test_baseline.ssm` |
| Analysis descriptor | `build/examples/analysis/test_baseline/analysis.json` |

Expected output:

```text
SSV written to build/examples/analysis/test_baseline/NominalScenario.ssv
SSM written to build/examples/analysis/test_baseline/test_baseline.ssm
Analysis descriptor written to build/examples/analysis/test_baseline/analysis.json
```

The second analysis differs only in its composition and scenario:

```bash
pyssp generate analysis \
  --architecture repos/pyssp_sysml/examples/analysis \
  --composition test_aggressive \
  --model position_servo \
  --core-definitions \
  --output-dir build/examples/analysis/test_aggressive
```

`generate analysis` writes no SSD. Generate the model structure separately:

```bash
pyssp generate ssd \
  --architecture repos/pyssp_sysml/examples/analysis \
  --composition PositionServo \
  --core-definitions \
  --output build/examples/analysis/PositionServo/SystemStructure.ssd
```

## Setup

Activate the workspace venv (this checkout: `source ../venv/bin/activate`); the
`pyssp` console script comes from the editable install of this package. See the
workspace `README.md`.

## What the definition encodes

`PositionServo :> SspModel` is the exportable model. `test_baseline` and
`test_aggressive` are `:> Analysis` definitions: each composes the model through
`sut`, applies exactly one parameter set, and declares exactly one `Experiment`.
The scenario binds land on the plant parameter interface, so the SSM targets are
model-root relative (`axis.plant.inputScale`, `axis.plant.gain`,
`axis.plant.timeConstant`); `analysis.json` records the model, composition,
`sut` usage, target SSD, experiment window, and scenario files.

Both role markers and their carriers come from the shared `PysspCore`
vocabulary, imported as `private import PysspCore::*;`. The role contract is
owned by
[`docs/roles.md`](../../../pyssp_sysml_definitions/docs/roles.md).

## Composition

The servo is a `ServoAxis` system containing a `driver` and a parameterized
`plant`. `test_baseline` uses `NominalScenario` over 10 s at 0.01 s steps;
`test_aggressive` uses `AggressiveScenario` over 2 s at 0.002 s steps.

`generate ssp` accepts `PositionServo` but rejects any `:> Analysis`
composition. Packaging the model as an SSP additionally requires
`fmu_meta.source` on each leaf component, which also means marking those leaves
`:> FmuModel`; `FmuModel` and `FmuMetadata` come from `PysspCore`.
