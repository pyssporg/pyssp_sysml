"""Pure SSD emission from the parser-free projection model."""

from __future__ import annotations

from pyssp_standard import (
    Component,
    ParameterBinding,
    SSD,
    SSM,
    System,
)

from pyssp_sysml.emit.values import fixed_count
from pyssp_sysml.projection.model import (
    Attribute,
    MappingSpec,
    PartDef,
    PortDef,
    PortUsage,
    SystemModel,
)


def _port_indices(port_usage: PortUsage) -> tuple[int | None, ...]:
    """Connector indices for one port usage; 1-based to match FMI arrays."""
    if not port_usage.multiplicity:
        return (None,)
    count = fixed_count(port_usage.multiplicity, port_usage.name)
    return tuple(range(1, count + 1))


def _multiplicity_text(port_usage: PortUsage) -> str:
    return f"[{port_usage.multiplicity}]" if port_usage.multiplicity else ""


def _attribute_indices(
    attribute: Attribute, port_usage: PortUsage
) -> tuple[int | None, ...]:
    """Connector indices for one port attribute; 1-based to match FMI arrays."""
    if not attribute.multiplicity:
        return (None,)
    name = f"{port_usage.name}.{attribute.name}"
    try:
        count = fixed_count(attribute.multiplicity, name)
    except ValueError as error:
        raise ValueError(f"Port attribute '{name}': {error}") from None
    return tuple(range(1, count + 1))


def _attribute_text(attribute: Attribute) -> str:
    return f"[{attribute.multiplicity}]" if attribute.multiplicity else ""


def _connector_name(
    port_usage: PortUsage,
    attribute: Attribute,
    flat: bool,
    index: int | None,
    attribute_index: int | None,
    *,
    scalar: bool,
) -> str:
    port = port_usage.name if index is None else f"{port_usage.name}[{index}]"
    if flat or scalar:
        if attribute.multiplicity:
            raise ValueError(
                f"Flat connector naming cannot represent array attribute "
                f"'{port_usage.name}.{attribute.name}"
                f"{_attribute_text(attribute)}'; export without flat_connector"
            )
        return port
    member = (
        attribute.name
        if attribute_index is None
        else f"{attribute.name}[{attribute_index}]"
    )
    return f"{port}.{member}"


def _member_direction(attribute: Attribute, port_usage: PortUsage) -> str:
    """Resolved SysML direction of one port member on this usage."""
    direction = port_usage.member_directions.get(attribute.name)
    return "out" if direction == "out" else "in"


def _connector_kind(direction: str) -> str:
    return "output" if direction == "out" else "input"


def _ports_compatible(source: PortDef, destination: PortDef) -> bool:
    """True when two port definitions describe the same interface.

    Direction is flow metadata, not type: a mirrored definition with the same
    member names and types is a compatible endpoint.
    """
    if source is destination:
        return True
    if source.attributes.keys() != destination.attributes.keys():
        return False
    return all(
        source.attributes[name].type_name
        == destination.attributes[name].type_name
        for name in source.attributes
    )


def _parameter_binding(
    system: System, spec: MappingSpec, parameter_set_prefix: str
) -> ParameterBinding:
    """Attach one parameter binding to *system* and return it."""
    prefix = parameter_set_prefix.strip().strip("/")
    source = f"{prefix}/{spec.set_name}.ssv" if prefix else f"{spec.set_name}.ssv"
    if spec.identity:
        return system.add_parameter_binding(
            source, prefix=f"{spec.component_name}."
        )
    return system.add_parameter_binding(
        source, mapping=SSM.create_mapping(spec.entries)
    )


def _add_part_connectors(
    element: Component | System,
    part: PartDef,
    parameter_model: bool,
    *,
    flat: bool,
) -> None:
    """Append port and parameter connectors for one component or system."""
    for port_usage in part.ports.values():
        port_def = port_usage.definition
        if port_def is None:
            raise ValueError(
                f"Unresolved port definition for "
                f"{part.name}.{port_usage.name}"
            )
        if port_def.is_parameter_interface:
            # Emitted by the parameter branch below, flattened to member names.
            continue
        for index in _port_indices(port_usage):
            for attribute in port_def.attributes.values():
                for attribute_index in _attribute_indices(attribute, port_usage):
                    connector_name = _connector_name(
                        port_usage,
                        attribute,
                        flat,
                        index,
                        attribute_index,
                        scalar=port_def.scalar,
                    )
                    element.add_connector(
                        name=connector_name,
                        kind=_connector_kind(
                            _member_direction(attribute, port_usage)
                        ),
                        type_name=attribute.type_name,
                    )

    if parameter_model and part.is_parameter_interface:
        for item in part.parameter_items:
            element.add_connector(
                name=item.name,
                kind="parameter",
                type_name=item.type_name,
            )


def _add_connections(
    target_system: System,
    part: PartDef,
    type_check: bool,
    *,
    flat: bool,
) -> None:
    """Append this system level's connections to an SSD system."""
    for connection in part.connections:
        src_port_usage = connection.source
        dst_port_usage = connection.destination
        assert src_port_usage is not None and dst_port_usage is not None
        src_port_def = src_port_usage.definition
        dst_port_def = dst_port_usage.definition
        assert src_port_def is not None and dst_port_def is not None
        if type_check and not _ports_compatible(src_port_def, dst_port_def):
            raise ValueError(
                f"Src {connection.source_port} and dest port "
                f"{connection.destination_port} must be same type"
            )

        src_indices = _port_indices(src_port_usage)
        dst_indices = _port_indices(dst_port_usage)
        if src_indices != dst_indices:
            raise ValueError(
                f"Connection '{connection.key}' joins ports with different "
                f"multiplicity: {src_port_usage.name}"
                f"{_multiplicity_text(src_port_usage)} and "
                f"{dst_port_usage.name}{_multiplicity_text(dst_port_usage)}"
            )
        src_attributes = src_port_def.attributes
        dst_attributes = dst_port_def.attributes
        for index in src_indices:
            for src_attribute in src_attributes.values():
                dst_attribute = dst_attributes.get(src_attribute.name)
                if dst_attribute is None:
                    # Different port types: keep naming by the source member.
                    dst_attribute = src_attribute
                    dst_attribute_indices = _attribute_indices(src_attribute, src_port_usage)
                else:
                    dst_attribute_indices = _attribute_indices(dst_attribute, dst_port_usage)
                src_attribute_indices = _attribute_indices(src_attribute, src_port_usage)
                if src_attribute_indices != dst_attribute_indices:
                    raise ValueError(
                        f"Connection '{connection.key}' joins attributes with "
                        f"different multiplicity: "
                        f"{src_port_usage.name}.{src_attribute.name}"
                        f"{_attribute_text(src_attribute)} and "
                        f"{dst_port_usage.name}.{dst_attribute.name}"
                        f"{_attribute_text(dst_attribute)}"
                    )
                for attribute_index in src_attribute_indices:
                    target_system.add_connection(
                        start_element=connection.source_part,
                        start_connector=_connector_name(
                            src_port_usage,
                            src_attribute,
                            flat,
                            index,
                            attribute_index,
                            scalar=src_port_def.scalar,
                        ),
                        end_element=connection.destination_part,
                        end_connector=_connector_name(
                            dst_port_usage,
                            dst_attribute,
                            flat,
                            index,
                            attribute_index,
                            scalar=dst_port_def.scalar,
                        ),
                    )


def _write_elements(
    parent: System,
    part: PartDef,
    *,
    parameter_model: bool,
    type_check: bool,
    flat: bool,
) -> None:
    """Recursively write nested systems and leaf FMU components."""
    for part_name, part_usage in part.parts.items():
        child = part_usage.definition
        if child is None:
            raise ValueError(
                f"Unresolved part definition for {part_usage.name}"
            )
        if child.parts:
            if child.fmu_declared:
                raise ValueError(
                    f"{child.name} has both subparts and 'fmu_meta' metadata; "
                    "a nested system cannot also be an FMU component"
                )
            nested = parent.add_subsystem(part_name)
            _add_part_connectors(
                nested,
                child,
                parameter_model,
                flat=flat,
            )
            _write_elements(
                nested,
                child,
                parameter_model=parameter_model,
                type_check=type_check,
                flat=flat,
            )
            continue

        component = parent.add_component(
            part_name,
            source=child.fmu_source,
            component_type="application/x-fmu-sharedlibrary",
            implementation=child.fmu_implementation,
        )
        _add_part_connectors(
            component,
            child,
            parameter_model,
            flat=flat,
        )

    _add_connections(parent, part, type_check, flat=flat)


def expected_connector_names(
    part: PartDef,
    *,
    parameter_model: bool,
    flat: bool,
) -> list[str]:
    """The connector names the SSD will declare for one leaf component."""
    expected: list[str] = []
    for port_usage in part.ports.values():
        port_def = port_usage.definition
        if port_def is None or port_def.is_parameter_interface:
            continue
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
                            scalar=port_def.scalar,
                        )
                    )

    if parameter_model and part.is_parameter_interface:
        expected.extend(item.name for item in part.parameter_items)
    return expected


def build_ssd(
    ssd: SSD,
    model: SystemModel,
    type_check: bool = True,
    parameter_set_prefix: str = "parameter_sets",
    *,
    flat_connector: bool = False,
) -> None:
    """Write one SSD from a projection model.

    ``flat_connector`` selects the connector naming style: ``False`` (the
    default) emits ``port.member`` names, ``True`` emits one ``port`` name per
    member. Flattening is an export option, never model data.
    """
    if model.is_analysis:
        raise ValueError(
            f"Composition '{model.name}' is an Analysis; analyses generate scenario "
            "data and are never exported as an SSD or SSP"
        )
    if model.ssp_source is not None:
        raise ValueError(
            f"Composition '{model.name}' selects an external SSP source via "
            "'ssp_meta'; it is an analysis-only boundary and cannot be exported"
        )
    top = ssd.new_system(model.name)
    ssd.rename(model.name)

    if model.root.is_parameter_interface:
        raise ValueError(
            "Top-level composition parameter interfaces are not supported; "
            "attach parameter interfaces to component usages"
        )

    _add_part_connectors(
        top,
        model.root,
        model.parameter_model,
        flat=flat_connector,
    )
    _write_elements(
        top,
        model.root,
        parameter_model=model.parameter_model,
        type_check=type_check,
        flat=flat_connector,
    )

    experiment = model.experiment
    ssd.set_default_experiment(
        start_time=experiment.start_time if experiment is not None else 0,
        stop_time=experiment.stop_time if experiment is not None else 3600,
    )

    if model.parameter_model:
        for spec in model.mappings:
            _parameter_binding(top, spec, parameter_set_prefix)
