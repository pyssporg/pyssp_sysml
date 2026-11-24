---
id: INFO-006
type: info
title: Generation pipeline
summary: Load, select, enforce, project to parser-free records, then emit SSD, SSV, SSM, the analysis descriptor, and the packaged SSP.
date: 2026-11-05
status: current
---

# Generation pipeline

## Stages and directions

The SSP direction has five stages, each with one owner:

1. **Load**: `pycps_sysml.load()` produces an `Architecture` (`INFO-032`).
2. **Select and resolve**: the composition wrapper applies variation selection
   and the model-level configuration. Selection belongs here, not to the
   parser package.
3. **Enforce constraints**: `enforce_constraints` rejects an illegal selection
   before any artifact write.
4. **Project**: `pyssp_sysml.projection` converts the loaded, post-selection
   architecture into parser-free records (`projection/model.py`). This is the
   only SSP-generation code that reads `Architecture`, `PartDefinition`,
   `PartUsage`, `effective_members`, `resolve_part`, `resolve_port`,
   `stored_key`, or the parser package's metadata and dialect helpers. It
   pre-resolves definition pointers, flattens inherited members, normalizes
   member directions, expands parameter indices, and projects roles, the
   experiment, parameter sets, and mappings.
5. **Emit**: `pyssp_sysml.emit` writes SSD, SSV, SSM, the analysis descriptor,
   or the packaged SSP from those records. Emitters import no `pycps_sysml`
   module and never see a loaded architecture.

`artifacts/*` hold the composition wrappers: their `generate_*` functions run
stages 1–3, project once, then call the matching `emit.build_*` seam.
`build_ssd(ssd, model)` is the parser-free seam; its legacy
`build_ssd(ssd, part_def, architecture)` form projects on the fly.

The reverse direction starts at an SSD (`INFO-038`): an SSD plus its referenced
SSV/SSM files produce a SysML model through `generate sysml` or `sync ssd`.

SSV, SSM, SSD, and SSP are separate outputs. `generate ssd` does not embed
parameter values; it references an SSV and optionally inlines a mapping. FMI
output belongs to `pyfmi_interfaces` (`INFO-031`). Per-artifact sources are
`INFO-039`; variation selection is `INFO-040`.

Practical ordering:

1. Generate SSV and SSD from SysML.
2. Optionally generate standalone SSM files for inspection.
3. Package built FMUs, SSD, and applied sets as an SSP.
4. Edit the SSD externally, then `sync ssd` to bring structure back.
5. Or run `generate sysml` to synthesize a fresh SysML model.

`generate sysml` and `sync ssd` need the SSV/SSM files referenced by the SSD.
Keep the parameter directory next to the SSD or preserve relative paths.
`generate sysml` marks a synthesized component with FMU metadata as
`:> FmuModel` and declares the marker locally.
