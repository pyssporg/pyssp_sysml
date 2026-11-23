<!-- GENERATED FILE — do not edit. Regenerate with `pb registers`. -->

# Decision Stream

Flat, dated history of every committed design choice. Current state lives
in the layer leaves named by each record's `state:` field.

Records live in the cold-storage archive; extract one with `pb archive read <ID>`.

## By Layer

### Architecture

- **AD-001** — Constraints Are Captured in the Adapter and Evaluated After Selection · accepted · 2026-10-30 · `AD-001`
  Constraint definitions and asserted usages are repo-owned model data, evaluated after variation selection and before artifact writes.
- **AD-002** — Analyses Declare Their Variation Selection with a Control Attribute · accepted · 2026-10-30 · `AD-002`
  A pyssp_selection control attribute on an Analysis is the single authored selection; the adapter resolves it and classifies each analysis as legal, violated, or invalid.
- **AD-003** — Configurations derive the analysis selection · accepted · 2026-10-30 · `AD-003`
  An analysis composes a model-level SysML v2 configuration; the adapter derives the selection map from its redefinitions and feature values, replacing the pyssp_selection control attribute.
- **AD-005** — Adapt v0.6.0 to pycps_sysml2 0.3.0 Typed Containers · accepted · 2026-11-19 · `AD-005`
  v0.6.0 reads the experiment from a typed DefaultExperiment container, moves flattening to the --flat-connector export option, drops the control-tag plumbing, and leaves the release pin for a follow-up.
- **AD-006** — SSD generation reads effective members · accepted · 2026-11-19 · `AD-006`
  SSD and preflight resolve inherited members through pycps_sysml2, while the SSV writer and SysML synthesis stay declared-only.
- **AD-007** — SSD drops the experiment tolerance · accepted · 2026-11-19 · `AD-007`
  SSP 2.0's DefaultExperiment has no tolerance attribute, so the SSD writer emits only startTime and stopTime.
- **AD-008** — implementation is closed and the SSD keeps only the SSP experiment fields · accepted · 2026-11-19 · `AD-008`
  pyssp_sysml2 validates implementation against the four ssd:Component values and projects only startTime and stopTime into the .ssd.
- **AD-009** — Generated FMU components specialize FmuModel · accepted · 2026-11-20 · `AD-009`
  A synthesized component that receives fmu_meta is marked ':> FmuModel', and the generated file declares the marker locally.
- **AD-010** — SSP emission splits into projection and emission inside one repository · accepted · 2026-11-22 · `AD-010`
  The SSP emitters stop taking pycps objects; a projection stage produces parser-free records and an emission stage writes artifacts, while SSP stays one package until a non-SysML caller exists.

### Implementation

- **AD-004** — pyssp_sysml2 Becomes an SSP-Artifact Implementer · accepted · 2026-11-05 · `AD-004`
  At v0.4.0 pyssp_sysml2 keeps only SSP-family emission and SSD-to-SysML synthesis; the SysML dialect moved to pycps_sysml2 and FMI to pyfmi_sysml2.
