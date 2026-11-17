---
id: INFO-055
type: info
title: Validation of SSP packaging
summary: Declared sources, FMU readability, connector names and kinds, and implementation must all agree before an archive is committed.
date: 2026-11-05
status: current
---

# Validation of SSP packaging

`pyssp validate` exposes the name, readability, and implementation checks
before generation: `check_fmu_interfaces` reports every missing connector name
and unreadable or missing declared source, and `--implementation` checks the
declared metadata. Pass the same `--base-index` as generation so parameter
arrays compare against the indices the generator will emit. It writes no
artifact. `generate ssp` keeps its late check unchanged: the archive is only
written when the packaged SSD and FMUs agree.

- A declared FMU source must exist unless `--allow-missing-fmus` exports the
  design.
- A file source must be a `.fmu` file or an extracted FMU directory.
- An extracted source must be readable as an FMU.
- Two part definitions cannot map to the same resource name with different
  sources.
- SSD connector names must exist in the FMU.
- SSD connector kinds must match the FMU causality.
- Component implementation must match the FMU interface.

`--skip-fmu-validation` bypasses the model-description name, connector-kind, and
implementation checks. It still requires every declared source to exist and
packages the FMUs. `--allow-missing-fmus` additionally tolerates a missing
declared source; those components keep `resources/<PartDefinition>.fmu`, are
exported without a resource, and are reported as warnings.
