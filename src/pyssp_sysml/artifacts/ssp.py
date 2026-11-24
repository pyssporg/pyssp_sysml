"""SSP composition wrapper: load, select, enforce, project, package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pycps_sysml.metadata.roles import SSP_ROLES
from pycps_sysml.model import load
from pycps_sysml.parameters.constraints import enforce_constraints
from pycps_sysml.parameters.variation import resolve_selected

from pyssp_sysml.emit.ssp import (  # noqa: F401 - documented compatibility names
    DEFAULT_PARAMETER_SET_PREFIX,
    SELECTION_ENTRY,
)
from pyssp_sysml.emit.ssp import build_ssp
from pyssp_sysml.projection import project_system


def generate_ssp(
    architecture_path: Path,
    output_path: Path,
    composition: str,
    *,
    parameter_set_prefix: str = DEFAULT_PARAMETER_SET_PREFIX,
    fmu_root: Path | None = None,
    type_check: bool = True,
    validate_fmus: bool = True,
    allow_missing_fmus: bool = False,
    selections: Mapping[str, str] | None = None,
    configuration: str | None = None,
    includes: Sequence[Path | str] = (),
    base_index: int = 0,
) -> Path:
    """Build an ``.ssp`` archive from a SysML architecture and its built FMUs.

    ``base_index`` is the first array index emitted in SSD parameter connector
    names and SSV entry names, e.g. 0 -> ``waypointX_km[0]`` and 1 ->
    ``waypointX_km[1]``. Data ports keep their FMI-style 1-based indices
    regardless.

    Relative ``fmu_meta.source`` paths are resolved against ``fmu_root`` (the
    current working directory when omitted). ``SSD`` parameter bindings and
    packaged SSVs share ``parameter_set_prefix``.

    When ``validate_fmus`` is true (the default), each FMU's
    ``modelDescription.xml`` is checked against the generated SSD connector
    names and the requested ``fmu_meta.implementation``.

    A leaf component without ``fmu_meta.source`` has no FMU yet: it is exported
    with an empty SSD ``source`` and no resource. The archive is then a design
    artifact until the FMUs are attached with ``SSP.attach_fmu``.

    When ``allow_missing_fmus`` is true, a component whose declared
    ``fmu_meta.source`` does not exist on disk is exported the same way, with
    its expected ``resources/<name>`` source and no packaged FMU. Without the
    flag, a missing declared source is an error.

    ``selections`` resolves variation points before generation; see
    :func:`pyssp_sysml.parameters.variation.resolve`. A non-empty mapping is also
    recorded in the archive at ``extra/org.pyssp/selection.json``; the record
    names the configuration that produced the selection via ``configuration``,
    and omits it when the build composes the root.

    ``includes`` names additional definition roots (files or directories)
    merged into the loaded architecture; pass
    :func:`pycps_sysml.core_definitions` to supply the dialect core. Empty
    (the default) loads only the model's own declarations.
    """
    architecture = load(architecture_path, *includes)
    system = architecture.get_part_def(composition)
    canonical = None
    if selections:
        architecture, canonical = resolve_selected(
            architecture, system, selections, roles=SSP_ROLES
        )
        system = architecture.get_part_def(composition)
    enforce_constraints(architecture, composition, canonical)
    model = project_system(architecture, system, base_index=base_index)
    if model.is_analysis:
        raise ValueError(
            f"Composition '{composition}' is an Analysis; analyses are not "
            "exportable as SSPs. Export its 'part sut : <SspModel>' model "
            "instead."
        )
    if model.ssp_source is not None:
        raise ValueError(
            f"Composition '{composition}' selects an external SSP source via "
            "'ssp_meta'; it is an analysis-only boundary and cannot be exported. "
            "Generate its analysis instead."
        )
    return build_ssp(
        model,
        output_path,
        parameter_set_prefix=parameter_set_prefix,
        fmu_root=fmu_root,
        type_check=type_check,
        validate_fmus=validate_fmus,
        allow_missing_fmus=allow_missing_fmus,
        selections=selections,
        configuration=configuration,
        base_index=base_index,
    )
