# Building on pyssp_sysml2

Status: current for `pyssp_sysml2` 0.5.0. The code and `docs/breakdown/` are
the source of truth.

## The important part

`pyssp_sysml2` is the last build step. It reads one SysML v2 architecture and
packages an `.ssp` from FMUs that already exist on disk. It never calls a
builder.

A library that builds FMUs must respect three facts:

1. The part definition name is the component identity and the archive resource
   name, `resources/<PartDefinition>.fmu`.
2. FMU variable names must match the SysML ports and attributes that become SSD
   connectors.
3. `fmu_meta.source` points at the built `.fmu` file or extracted FMU directory;
   relative paths resolve against `fmu_root`.

Everything else is layering: producers run before assembly, orchestrators
sequence them, and no layer imports a later one.

**Order is fixed:** all leaf FMUs exist before `generate_ssp` runs. Assembly
never calls a builder and never treats a missing FMU as a successful build.

The same architecture feeds both phases, but the two readers want different
things from it. The producer decides what to build; the assembler decides how
to wire and package. A model must satisfy both contracts, and producer
requirements may go beyond what assembly needs.

Do not extend `FmuMetadata` (the schema is `source` and `implementation`; extra
members are rejected). Do not add a plugin registry; the seam is the CLI plus
files.

## One-way layering

```text
pycps_sysml2            dialect: parse, IR, markers, policies
  |-- pyfmi_interfaces      FMI artifacts
  `-- pyssp_sysml2      SSP-family assembly
FMU producers           pyfmu_csv, project builders
orchestrators           pyssp_workflow, build scripts, CI
```

- Imports and data point one way. `pyssp_sysml2` never imports a producer or an
  orchestrator; producers read the model through `pycps_sysml2`, not through
  `pyssp_sysml2` internals.
- Layers exchange artifacts, not objects: a built `.fmu` into assembly; SSD,
  SSV, SSM, SSP out of it.
- Ecosystem vocabulary lives in `pycps_sysml2` (via `RolePolicy`,
  `DialectPolicy`, `ControlAttributes`). Never re-declare a marker in an
  implementer.

Phases: model (`.sysml`) -> FMU (`<Part>.fmu`) -> assembly (`.ssp`) -> run and
judge. Each phase is idempotent and reads only earlier outputs. Phase 1 must
finish for every leaf FMU before phase 2 starts. Assembly is terminal for the
build.

## Two views of one architecture

An FMU producer and the assembler read the same `.sysml` files for different
purposes:

- the producer needs the parts it must build, their interfaces, and the data
  that drives the build (CSV path, source model, tags);
- the assembler needs the composition, connections, parameter bindings, and
  `fmu_meta.source`.

The model must satisfy both. Producer requirements can be stricter than the
system's, and they can use part-type markers, parameter interfaces, or producer
config. The assembler does not enforce them, and a producer must not rely on
packaging to catch a missing build input. A producer may select only the part
definitions it builds; it does not need the final composition to be complete or
selected.

## Producer obligations

- Emit an FMU whose variable names match the SysML ports and attributes that
  become SSD connectors.
- Put it where `fmu_meta.source` points, or pass `fmu_root`. A declared source
  that does not exist is an error; a leaf with no source is a design
  placeholder, not a shippable leaf in a built archive.
- Do not rename the part definition to control the file name. The archive name
  is derived (`pycps_sysml2/core/fmi_helpers.py:15`).
- Set `implementation` to `CoSimulation` or `ModelExchange`; it is validated
  against the FMU.
- A part with subparts cannot also be an FMU component.

Assembler guarantees: SSD `Component/@source` is always
`resources/<PartDefinition>.fmu` (the authored path never appears); a declared
FMU file or extracted directory is copied into the archive; `generate ssp`
always rebuilds the SSD from SysML, so external SSD edits need `pyssp sync ssd`
first.

## Where producer data may live

An exported component may carry only control attributes, one `FmuMetadata`
attribute, an `SspMetadata` attribute, and parameter-set usages. Anything else
is rejected as a flat parameter attribute
(`pycps_sysml2/parameters/dialect/composition.py:384`). Three legal places:

1. **Part-type marker** for discovery:

   ```sysml
   part def CsvComponent;
   part def CsvSource :> CsvComponent { attribute fmu_meta : CsvSourceFmu; }
   ```

2. **Parameter interface** for values the SSP carries to run time:

   ```sysml
   port def CsvSourceParameters :> ParameterInterface {
     attribute csv_path : String;
   }
   part def CsvSource { in port parameters : CsvSourceParameters; }
   ```

3. **Producer config** for build-only data. Key it by part name; do not add a
   SysML attribute.

`FmuMetadata` is fixed to `source` and `implementation`; extra members are
rejected (`pycps_sysml2/metadata/fmu_metadata.py:141`). There is no annotation
channel: a "tag" is a typed definition or a part-type marker.

## Prebuilt-first is the contract

Build every FMU, then package:

```bash
# producer wrote build/fmus/<PartDefinition>.fmu for every leaf
# model declares fmu_meta.source = "build/fmus/<PartDefinition>.fmu"
pyssp generate ssp --architecture model --composition System \
  --output build/System.ssp --fmu-root .
```

Exception: design-first, only when the FMU build truly depends on the assembled
structure:

```bash
pyssp generate ssp ...   # empty Component/@source, warning, no resource
```

```python
# ... build the FMUs ...
with SSP(path, mode="a") as ssp:
    ssp.attach_fmu("source", fmu)
```

This is an explicit exception to the prebuilt rule, for exploratory models. A
delivered archive must have every FMU attached and pass validation.

## Public surface

Exported (`src/pyssp_sysml2/__init__.py:5`): `build_ssd`,
`check_fmu_interfaces`, `generate_ssd`, `generate_parameter_sets`,
`generate_parameter_mappings`, `generate_ssp`, `generate_analysis`,
`generate_sysml_from_ssd`, `sync_sysml_from_ssd`; the `pyssp` CLI; artifact
schemas through `pyssp_standard`.

Gates: `pyssp validate --architecture ... --composition ...` checks the model
and built FMU interfaces without writing; `check_fmu_interfaces(...)` reports
all problems in one pass.

Not public: private helpers (`_collect_fmu_resources`, `_connector_name`),
`SSP_POLICY`, unexported `src/` names, and the
`pyssp_sysml2.{model,core,metadata,parameters}` shims (removed in 0.5.0; import
`pycps_sysml2`).

## Anti-patterns

- Editing the `.ssp` zip instead of `SSP.attach_fmu`.
- Extending `FmuMetadata` or adding `pyssp_*` attributes in an implementer.
- Importing `pyssp_sysml2` internals to read a model; use `pycps_sysml2.load()`.
- A producer writing SSD/SSV/SSP XML itself instead of using `pyssp_standard`.
- Putting a builder call inside `generate_ssp`, or assembly inside a builder.
- Shipping an archive built with `--allow-missing-fmus`.
- Renaming a part to control the resource name.

## Checklist

1. Read this guide and the target repo's `AGENTS.md`.
2. Depend on `pycps_sysml2`; call `pyssp_sysml2` only through its public API,
   else exchange files with the CLI.
3. Mark parts with a defined part-type marker. Run-time values go on a
   `ParameterInterface`; build-only values stay in your config.
4. Build every leaf FMU before assembly. Emit `<PartDefinition>.fmu` matching
   the port names.
5. Prove it: load the model, build the FMUs, run `generate_ssp`, assert
   `resources/<PartDefinition>.fmu` exists for every leaf and validates.
6. Add no discovery or plugin layer until a second consumer needs it.

## For agents

- `repos/<name>` is its own repo: commit there, then bump the pin in the
  superproject.
- Read the target repo's `AGENTS.md` and `docs/breakdown/00-intent/intent.md`.
- Ownership: dialect `pycps_sysml2`, FMI `pyfmi_interfaces`, assembly and
  SSD-to-SysML `pyssp_sysml2`.
- Gates: `ruff check src tests` and `python -m pytest -m "not slow"`. Do not
  hand-edit product-breakdown registers.
- Code wins over this guide; update both together.
