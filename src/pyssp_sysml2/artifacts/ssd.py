"""SSD composition wrapper: load, select, enforce, project, emit."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pyssp_standard import SSD

from pycps_sysml2.metadata.roles import SSP_ROLES
from pycps_sysml2.model import load
from pycps_sysml2.parameters.constraints import enforce_constraints
from pycps_sysml2.parameters.variation import resolve_selected

from pyssp_sysml2.core.paths import ensure_parent_dir
from pyssp_sysml2.emit.ssd import build_ssd as emit_ssd
from pyssp_sysml2.projection import project_system
from pyssp_sysml2.projection.model import SystemModel


def build_ssd(
    ssd: SSD,
    system: object,
    architecture: object | None = None,
    type_check=True,
    parameter_set_prefix: str = "parameter_sets",
    *,
    base_index: int = 0,
    flat_connector: bool = False,
) -> None:
    """Write one SSD.

    With a :class:`~pyssp_sysml2.projection.model.SystemModel` this is the
    parser-free seam. The legacy form ``build_ssd(ssd, part_def, architecture)``
    remains public: it projects the loaded architecture on the fly and is kept
    for callers that already hold one. New code projects once and calls the
    two-argument form.

    ``flat_connector`` selects the connector naming style: ``False`` (the
    default) emits ``port.member`` names, ``True`` emits one ``port`` name per
    member. Flattening is an export option, never model data, so the same
    architecture can be exported both ways. Flat naming has no slot for a
    per-element index, so a fixed-length attribute array is rejected under it.
    """
    if architecture is None:
        if not isinstance(system, SystemModel):
            raise TypeError(
                "build_ssd takes a SystemModel, or a PartDefinition and its "
                "Architecture"
            )
        model = system
    else:
        model = project_system(
            architecture,
            system,
            base_index=base_index,
            require_resolved=False,
            with_parameter_sets=False,
        )
    emit_ssd(
        ssd,
        model,
        type_check,
        parameter_set_prefix=parameter_set_prefix,
        flat_connector=flat_connector,
    )


def generate_ssd(
    architecture_path: Path,
    output_path: Path,
    composition: str,
    type_check=True,
    parameter_set_prefix: str = "parameter_sets",
    selections: Mapping[str, str] | None = None,
    *,
    includes: Sequence[Path | str] = (),
    base_index: int = 0,
    flat_connector: bool = False,
) -> Path:
    """Write an SSD for one composition.

    ``base_index`` is the first array index emitted in parameter connector
    names, e.g. 0 -> ``waypointX_km[0]`` and 1 -> ``waypointX_km[1]``. Data
    ports keep their FMI-style 1-based indices regardless.

    ``flat_connector`` names each connector for the port alone instead of
    ``port.member``; it is an export option, not model data.

    ``includes`` names additional definition roots (files or directories)
    merged into the loaded architecture; pass
    :func:`pycps_sysml2.core_definitions` to supply the dialect core. Empty
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
    model = project_system(
        architecture,
        system,
        base_index=base_index,
        with_parameter_sets=False,
    )
    ensure_parent_dir(output_path)
    with SSD(output_path, mode="w") as ssd:
        emit_ssd(
            ssd,
            model,
            type_check,
            parameter_set_prefix=parameter_set_prefix,
            flat_connector=flat_connector,
        )
    return output_path
