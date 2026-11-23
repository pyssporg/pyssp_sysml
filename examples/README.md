# Examples

Runnable SysML architectures for this package's artifact landing: a composition
becomes an SSD, SSV, SSM, analysis descriptor, or packaged SSP.

The examples import the shared `PysspCore` vocabulary in the files that use it
(`private import PysspCore::*;`) and supply it as an include root: CLI commands
pass `--core-definitions`, and Python callers pass
`pycps_sysml2.core_definitions()` in `includes`. That function re-exports
`pyssp_sysml_definitions.core_definitions()`, so no `.sysml` vocabulary file is
copied into this repository. The role contract is stated once in
[`docs/roles.md`](../../pyssp_sysml_definitions/docs/roles.md); this page does
not repeat it.

## Run

From the `pyssp_dev` workspace root, with the workspace venv active:

```bash
bash repos/pyssp_sysml2/examples/cli_usage.sh
python repos/pyssp_sysml2/examples/module_usage.py
```

Both resolve their inputs from their own location, so the working directory does
not matter. Both drive `examples/aircraft_subset` and write under the gitignored
`build/examples/<script>/`. `cli_usage.sh` accepts one optional `--out DIR`;
`module_usage.py` accepts `--out DIR`.

| Script | Shows | Default output |
| --- | --- | --- |
| [`cli_usage.sh`](cli_usage.sh) | CLI path: `generate ssd`, `generate ssv`, `generate sysml`, `sync ssd` | `build/examples/cli_usage/` |
| [`module_usage.py`](module_usage.py) | The same SSD, SSV, and sync steps through the Python API | `build/examples/module_usage/` |

`cli_usage.sh` prints one artifact path per line:

```text
build/examples/cli_usage/SystemStructure.ssd
build/examples/cli_usage/parameter_sets
build/examples/cli_usage/new_architecture/architecture.sysml
build/examples/cli_usage/synced_sysml
```

`module_usage.py` prints the SSD, the SSV directory, and every synced file:

```text
build/examples/module_usage/SystemStructure.ssd
build/examples/module_usage/parameter_sets
build/examples/module_usage/synced_sysml/composition.sysml
build/examples/module_usage/synced_sysml/parameter_sets.sysml
build/examples/module_usage/synced_sysml/part_definitions.sysml
build/examples/module_usage/synced_sysml/port_definitions.sysml
build/examples/module_usage/synced_sysml/requirements.sysml
```

## Examples

| Example | Shows | Artifacts |
| --- | --- | --- |
| [`aircraft_subset/`](aircraft_subset/README.md) | Nested aircraft composition, component parameters, signal connectors | SSD, SSV (optional SSP) |
| [`analysis/`](analysis/README.md) | `SspModel` model with two `Analysis` compositions over one applied scenario | analysis descriptor (`.json`), SSV, SSM, SSD |
| [`parameter-sets/`](parameter-sets/README.md) | Four parameter-set shapes: identity, explicit, disjoint, nested | SSD, SSV, SSM, regenerated SysML |

## Setup

Activate the workspace venv (this checkout: `source ../venv/bin/activate`); the
`pyssp` console script and the `pyssp_sysml2` import come from the editable
install described in the workspace `README.md`.

Each example directory states its own commands and expected files; the full
artifact sequence is in `docs/breakdown/05-operation/examples.md`.
