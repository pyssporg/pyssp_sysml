"""Pre-generation validation of FMU interfaces.

``generate_ssp`` fails fast: it writes the SSD first and only then checks each
component's connector names against its FMU. A model author asking what is
wrong needs every problem in one pass and no artifact, so
:func:`check_fmu_interfaces` reports instead of raising.

The connector naming rule is not repeated here. It is read from
:mod:`pyssp_sysml2.artifacts.ssd`, the same helpers that write the SSD, so a
checker can never disagree with the generator about a name.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyssp_standard import FMU

from pycps_sysml2.core.fmi_helpers import fmu_filename
from pycps_sysml2.metadata.fmu_metadata import fmu_metadata
from pycps_sysml2.metadata.roles import is_analysis
from pycps_sysml2.model import Architecture, PartDefinition
from pycps_sysml2.parameters.dialect.composition import (
    component_definitions,
    has_parameter_dialect,
)
from pycps_sysml2.parameters.dialect.declarations import (
    parameter_declarations,
    parameter_interface,
    parameter_items,
)
from pycps_sysml2.parameters.dialect.markers import is_parameter_interface
from pycps_sysml2.parameters.policy import SSP_POLICY

from pyssp_sysml2.artifacts.ssd import (
    _attribute_indices,
    _connector_name,
    _is_scalar_port,
    _port_indices,
)


@dataclass(frozen=True)
class _FmuResource:
    part_def: PartDefinition
    source: Path | None
    resource_name: str


def _resolve_fmu_source(source: str, fmu_root: Path | None) -> Path:
    path = Path(source).expanduser()
    if not path.is_absolute():
        path = (fmu_root or Path.cwd()) / path
    return path.resolve()


def _collect_fmu_resources(
    architecture: Architecture,
    system: PartDefinition,
    fmu_root: Path | None,
    *,
    allow_missing: bool = False,
) -> list[_FmuResource]:
    resources: list[_FmuResource] = []
    for part_def in component_definitions(architecture, system):
        if part_def.parts:
            continue

        metadata = fmu_metadata(architecture, part_def)
        resource_name = fmu_filename(part_def.name)
        if metadata is None or not metadata.source:
            # No FMU authored yet: the design structure leaves the component
            # unpopulated (empty SSD source).
            resources.append(_FmuResource(part_def, None, resource_name))
            continue

        source = _resolve_fmu_source(metadata.source, fmu_root)
        if not source.exists():
            if not allow_missing:
                raise FileNotFoundError(
                    f"FMU source for {part_def.name} does not exist: {source}"
                )
            resources.append(_FmuResource(part_def, None, resource_name))
            continue
        if source.is_file() and source.suffix.lower() != ".fmu":
            raise ValueError(
                f"FMU source for {part_def.name} must be a .fmu file or an "
                f"extracted FMU directory, got: {source}"
            )
        if source.is_dir() and not (source / "modelDescription.xml").is_file():
            raise FileNotFoundError(
                "FMU directory does not contain modelDescription.xml: "
                f"{source}"
            )

        resources.append(
            _FmuResource(
                part_def=part_def,
                source=source,
                resource_name=resource_name,
            )
        )
    return resources


def _expected_connector_names(
    architecture: Architecture,
    part_def: PartDefinition,
    *,
    parameter_model: bool,
    base_index: int,
    flat: bool,
) -> list[str]:
    """The connector names the SSD will declare for one leaf component."""
    expected: list[str] = []
    for port_usage in part_def.ports.values():
        port_def = architecture.resolve_port(port_usage)
        if port_def is None or is_parameter_interface(port_def):
            continue
        scalar = _is_scalar_port(port_def)
        for index in _port_indices(port_usage):
            for attribute in port_def.attributes.values():
                for attribute_index in _attribute_indices(attribute, port_usage):
                    expected.append(
                        _connector_name(
                            port_usage,
                            attribute,
                            flat,
                            index,
                            attribute_index,
                            scalar=scalar,
                        )
                    )

    if parameter_model and parameter_interface(architecture, part_def) is not None:
        for attribute in parameter_declarations(architecture, part_def):
            for item in parameter_items(attribute, base_index):
                expected.append(item.name)
    return expected


def check_fmu_interfaces(
    architecture: Architecture,
    composition: PartDefinition | str,
    fmu_root: Path | None = None,
    *,
    base_index: int = 0,
    flat_connector: bool = False,
) -> tuple[str, ...]:
    """Report every FMU interface problem below ``composition``.

    Each leaf component's ``fmu_meta.source`` is loaded and its declared port
    and parameter connector names are compared with the FMU's
    ``variable_names``. A missing declared source, an unreadable archive, and
    every absent name are returned as human-readable strings; they never raise.

    ``base_index`` is the first array index used for parameter names. Pass the
    same value the generator will use (``--base-index``): parameter lists are
    0-based by default, while OMC-built Modelica FMUs declare them 1-based.
    Data ports keep their FMI-style 1-based indices regardless.

    ``flat_connector`` must match the SSD generator's option: ``True`` expects
    one scalar connector per port member instead of ``port.member`` names.

    Raises:
        ValueError: ``composition`` does not exist or is an Analysis.
    """
    if isinstance(composition, PartDefinition):
        system = composition
    else:
        system = architecture.resolve_part(composition)
        if system is None:
            raise ValueError(f"Unknown composition '{composition}'")
    if is_analysis(architecture, system):
        raise ValueError(
            f"Composition '{system.name}' is an Analysis; analyses are not "
            "exportable as SSPs. Validate its 'part sut : <SspModel>' model "
            "instead."
        )

    try:
        resources = _collect_fmu_resources(
            architecture, system, fmu_root, allow_missing=True
        )
    except (FileNotFoundError, ValueError) as error:
        return (str(error),)

    parameter_model = has_parameter_dialect(
        architecture, system, policy=SSP_POLICY
    )
    problems: list[str] = []
    for resource in resources:
        part_def = resource.part_def
        if resource.source is None:
            metadata = fmu_metadata(architecture, part_def)
            if metadata is None or not metadata.source:
                # Design placeholder: no FMU authored yet, nothing to compare.
                continue
            source = _resolve_fmu_source(metadata.source, fmu_root)
            problems.append(
                f"{part_def.name}: FMU source does not exist: {source}"
            )
            continue

        try:
            with FMU(resource.source, mode="r") as fmu:
                with fmu.model_description as model_description:
                    names = model_description.variable_names
        except Exception as error:  # noqa: BLE001 - report, never abort a check
            problems.append(
                f"{part_def.name}: cannot read FMU {resource.source}: {error}"
            )
            continue

        expected = _expected_connector_names(
            architecture,
            part_def,
            parameter_model=parameter_model,
            base_index=base_index,
            flat=flat_connector,
        )
        for name in sorted(set(expected) - names):
            problems.append(
                f"{part_def.name}: FMU {resource.source} is missing "
                f"variable '{name}'"
            )
    return tuple(problems)
