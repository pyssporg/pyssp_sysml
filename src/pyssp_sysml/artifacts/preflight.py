"""Pre-generation validation of FMU interfaces.

``generate ssp`` fails fast: it writes the SSD first and only then checks each
component's connector names against its FMU. A model author asking what is
wrong needs every problem in one pass and no artifact, so
:func:`check_fmu_interfaces` reports instead of raising.

The connector naming rule is not repeated here. It is read from
:mod:`pyssp_sysml.emit.ssd`, the same helpers that write the SSD, so a
checker can never disagree with the generator about a name.
"""

from __future__ import annotations

from pathlib import Path

from pyssp_standard import FMU

from pyssp_sysml.emit.fmu_resources import (
    collect_fmu_resources,
    resolve_fmu_source,
)
from pyssp_sysml.emit.ssd import expected_connector_names
from pyssp_sysml.projection import project_composition, project_part
from pyssp_sysml.projection.model import PartDef


def _expected_connector_names(
    architecture: object,
    part_def: object,
    *,
    parameter_model: bool,
    base_index: int,
    flat: bool,
) -> list[str]:
    """The connector names the SSD will declare for one part definition."""
    part = project_part(
        architecture,
        part_def,
        base_index=base_index,
        parameter_model=parameter_model,
        with_connections=False,
    )
    return _names(part, parameter_model=parameter_model, flat=flat)


def _names(
    part: PartDef,
    *,
    parameter_model: bool,
    flat: bool,
) -> list[str]:
    return expected_connector_names(
        part,
        parameter_model=parameter_model,
        flat=flat,
    )


def check_fmu_interfaces(
    architecture: object,
    composition: object,
    fmu_root: Path | None = None,
    *,
    base_index: int = 0,
    flat_connector: bool = False,
) -> tuple[str, ...]:
    """Report every FMU interface problem below ``composition``.

    Each leaf component's ``fmu_meta.source`` is loaded and its declared port
    and parameter connector names are compared with the FMU's variable names.
    A missing declared source, an unreadable archive, and every absent name are
    returned as human-readable strings; they never raise.

    ``base_index`` is the first array index used for parameter names. Pass the
    same value the generator will use (``--base-index``): parameter lists are
    0-based by default, while OMC-built Modelica FMUs declare them 1-based.
    Data ports keep their FMI-style 1-based indices regardless.

    ``flat_connector`` must match the SSD generator's option: ``True`` expects
    one scalar connector per port member instead of ``port.member`` names.

    Raises:
        ValueError: ``composition`` does not exist or is an Analysis.
    """
    model = project_composition(
        architecture,
        composition,
        base_index=base_index,
        validate=False,
        with_connections=False,
        with_parameter_sets=False,
        with_mappings=False,
        with_experiment=False,
    )
    if model.is_analysis:
        raise ValueError(
            f"Composition '{model.name}' is an Analysis; analyses are not "
            "exportable as SSPs. Validate its 'part sut : <SspModel>' model "
            "instead."
        )

    try:
        resources = collect_fmu_resources(
            model, fmu_root, allow_missing=True
        )
    except (FileNotFoundError, ValueError) as error:
        return (str(error),)

    problems: list[str] = []
    for resource in resources:
        part = resource.part_def
        if resource.source is None:
            if not part.fmu_raw_source:
                # Design placeholder: no FMU authored yet, nothing to compare.
                continue
            source = resolve_fmu_source(part.fmu_raw_source, fmu_root)
            problems.append(
                f"{part.name}: FMU source does not exist: {source}"
            )
            continue

        try:
            with FMU(resource.source, mode="r") as fmu:
                with fmu.model_description as model_description:
                    names = model_description.variable_names
        except Exception as error:  # noqa: BLE001 - report, never abort a check
            problems.append(
                f"{part.name}: cannot read FMU {resource.source}: {error}"
            )
            continue

        expected = _names(
            part,
            parameter_model=model.parameter_model,
            flat=flat_connector,
        )
        for name in sorted(set(expected) - names):
            problems.append(
                f"{part.name}: FMU {resource.source} is missing "
                f"variable '{name}'"
            )
    return tuple(problems)
