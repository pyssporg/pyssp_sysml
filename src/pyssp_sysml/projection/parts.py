"""Project a loaded part hierarchy into the parser-free model.

This module and :mod:`pyssp_sysml.projection.system` are the only places that
call ``effective_members``, ``resolve_part``, ``resolve_port``,
``stored_key``, or read a ``PartDefinition``/``PartUsage``/``PortUsage``.
Everything below the emitters sees :mod:`pyssp_sysml.projection.model`.
"""

from __future__ import annotations

from dataclasses import replace

from pycps_sysml.core.fmi_helpers import fmu_filename
from pycps_sysml.metadata.fmu_metadata import (
    component_implementation,
    component_source,
    fmu_metadata,
)
from pycps_sysml.model import (
    Architecture,
    Attribute as PycpsAttribute,
    Connection as PycpsConnection,
    PartDefinition,
    PortDefinition,
    PortUsage as PycpsPortUsage,
    effective_members,
)
from pycps_sysml.parameters.dialect.declarations import (
    parameter_declarations,
    parameter_interface,
    parameter_items,
)
from pycps_sysml.parameters.dialect.markers import is_parameter_interface

from pyssp_sysml.projection.model import (
    Attribute,
    Connection,
    ParameterItem,
    PartDef,
    PartUsage,
    PortDef,
    PortUsage,
)


def _effective_part(architecture: Architecture, part_def: PartDefinition) -> PartDefinition:
    """A detached view carrying every effective member of *part_def*.

    The parameter dialect resolves declarations from a definition's own fields.
    Handing it this view keeps inherited members visible without mutating the
    loaded architecture.
    """
    members = effective_members(architecture, part_def)
    return replace(
        part_def,
        attributes=dict(members.attributes),
        ports=dict(members.ports),
        parts=dict(members.parts),
        connections=dict(members.connections),
        bindings=list(members.bindings),
        constraints=list(members.constraints),
    )


def _attribute(attribute: PycpsAttribute) -> Attribute:
    return Attribute(
        name=attribute.name,
        type_name=attribute.effective_type_name,
        multiplicity=attribute.multiplicity,
        value=attribute.value,
        direction=attribute.direction,
        doc=attribute.doc,
    )


def _direction(usage: PycpsPortUsage, attribute: PycpsAttribute) -> str:
    """Normalize one resolved member direction the way the SSD writer does."""
    resolved = usage.effective_member_direction(attribute)
    return "out" if resolved == "out" else "in"


class Projector:
    """Build the projection graph once per (architecture, base index) pair."""

    def __init__(
        self,
        architecture: Architecture,
        *,
        base_index: int = 0,
        parameter_model: bool = False,
        with_connections: bool = True,
    ) -> None:
        self.architecture = architecture
        self.base_index = base_index
        self.parameter_model = parameter_model
        self.with_connections = with_connections
        self.components: list[PartDef] = []
        self._parts: dict[str, PartDef] = {}
        self._ports: dict[str, PortDef] = {}
        self._component_keys: set[str] = set()

    def part(
        self,
        definition: PartDefinition,
        ancestors: frozenset[str] = frozenset(),
        *,
        usage_name: str | None = None,
    ) -> PartDef:
        key = self.architecture.stored_key(definition)
        if key in ancestors:
            raise ValueError(
                f"Recursive part hierarchy at '{usage_name}' ({key})"
            )
        cached = self._parts.get(key)
        if cached is not None:
            return cached

        members = effective_members(self.architecture, definition)
        ports = {
            name: self._port_usage(usage, definition.name)
            for name, usage in members.ports.items()
        }

        parameter_part = _effective_part(self.architecture, definition)
        has_interface = (
            parameter_interface(self.architecture, parameter_part) is not None
        )
        items: tuple[ParameterItem, ...] = ()
        if self.parameter_model and has_interface:
            items = tuple(
                ParameterItem(item.name, item.type_name)
                for attribute in parameter_declarations(
                    self.architecture, parameter_part
                )
                for item in parameter_items(
                    attribute, base_index=self.base_index
                )
            )

        parts: dict[str, PartUsage] = {}
        for name, usage in members.parts.items():
            child = self.architecture.resolve_part(usage)
            if child is None:
                raise ValueError(
                    f"Unresolved part definition for {usage.name}"
                )
            projected = self.part(
                child, ancestors | {key}, usage_name=usage.name
            )
            parts[name] = PartUsage(name, usage.type_name, projected)

        if not members.parts and key not in self._component_keys:
            self._component_keys.add(key)

        connections = (
            tuple(
                self._connection(definition, ports, parts, connection)
                for connection in members.connections.values()
            )
            if self.with_connections
            else ()
        )

        part = PartDef(
            name=definition.name,
            doc=definition.doc,
            ports=ports,
            parts=parts,
            connections=connections,
            is_parameter_interface=has_interface,
            parameter_items=items,
            **self._fmu(definition),
        )
        self._parts[key] = part
        if not members.parts and key in self._component_keys:
            self.components.append(part)
        return part

    def _fmu(self, definition: PartDefinition) -> dict[str, object]:
        metadata = fmu_metadata(self.architecture, definition)
        return {
            "fmu_declared": metadata is not None,
            "fmu_source": component_source(definition, metadata),
            "fmu_implementation": component_implementation(metadata),
            "fmu_raw_source": metadata.source if metadata is not None else None,
            "resource_name": fmu_filename(definition.name),
        }

    def _port_def(self, definition: PortDefinition) -> PortDef:
        key = self.architecture.stored_key(definition)
        cached = self._ports.get(key)
        if cached is not None:
            return cached
        attributes = {
            name: _attribute(attribute)
            for name, attribute in effective_members(
                self.architecture, definition
            ).attributes.items()
        }
        projected = PortDef(
            name=definition.name,
            attributes=attributes,
            is_parameter_interface=is_parameter_interface(
                self.architecture, definition
            ),
            scalar=tuple(attributes) == ("value",),
        )
        self._ports[key] = projected
        return projected

    def _port_usage(
        self, usage: PycpsPortUsage, part_name: str
    ) -> PortUsage:
        definition = self.architecture.resolve_port(usage)
        if definition is None:
            raise ValueError(
                f"Unresolved port definition for {part_name}.{usage.name}"
            )
        port_def = self._port_def(definition)
        members = effective_members(
            self.architecture, definition
        ).attributes
        return PortUsage(
            name=usage.name,
            type_name=usage.type_name,
            direction=usage.direction,
            multiplicity=usage.multiplicity,
            conjugated=usage.conjugated,
            member_directions={
                name: _direction(usage, attribute)
                for name, attribute in members.items()
            },
            definition=port_def,
        )

    def _endpoint(
        self,
        system: PartDefinition,
        ports: dict[str, PortUsage],
        parts: dict[str, PartUsage],
        part_name: str | None,
        port_name: str,
    ) -> PortUsage:
        if part_name is None:
            usage = ports.get(port_name)
            if usage is None:
                raise ValueError(
                    f"Unknown boundary port '{port_name}' in connection; "
                    f"declare it as a port of '{system.name}'"
                )
        else:
            part_usage = parts.get(part_name)
            if part_usage is None:
                raise ValueError(
                    f"Unknown part '{part_name}' in connection"
                )
            if part_usage.definition is None:
                raise ValueError(
                    f"Unresolved part definition for {part_name}"
                )
            usage = part_usage.definition.ports.get(port_name)
            if usage is None:
                raise ValueError(
                    f"Unknown port '{part_name}.{port_name}' in connection"
                )
        if usage.definition is None:
            raise ValueError("Port definition not connected")
        if usage.definition.is_parameter_interface:
            label = port_name if part_name is None else f"{part_name}.{port_name}"
            raise ValueError(
                f"Parameter port '{label}' cannot be connected; "
                "apply a parameter set with 'bind'"
            )
        return usage

    def _connection(
        self,
        system: PartDefinition,
        ports: dict[str, PortUsage],
        parts: dict[str, PartUsage],
        connection: PycpsConnection,
    ) -> Connection:
        if connection.source_part is None and connection.destination_part is None:
            raise ValueError(
                f"Connection '{connection.key}' links two boundary ports of "
                f"'{system.name}'; a connection must cross into a subpart"
            )
        source = self._endpoint(
            system,
            ports,
            parts,
            connection.source_part,
            connection.source_port,
        )
        destination = self._endpoint(
            system,
            ports,
            parts,
            connection.destination_part,
            connection.destination_port,
        )
        self._check_boundary_direction(
            system, connection.source_part, source, "in"
        )
        self._check_boundary_direction(
            system, connection.destination_part, destination, "out"
        )
        return Connection(
            key=connection.key,
            source_part=connection.source_part,
            source_port=connection.source_port,
            destination_part=connection.destination_part,
            destination_port=connection.destination_port,
            source=source,
            destination=destination,
        )

    def _check_boundary_direction(
        self,
        system: PartDefinition,
        part_name: str | None,
        usage: PortUsage,
        expected: str,
    ) -> None:
        if part_name is not None:
            return
        side = "start" if expected == "in" else "end"
        attributes = usage.definition.attributes if usage.definition else {}
        if attributes:
            for name, attribute in attributes.items():
                direction = usage.member_directions.get(name)
                direction = "out" if direction == "out" else "in"
                if direction != expected:
                    raise ValueError(
                        f"Boundary port '{usage.name}' of '{system.name}' "
                        f"member '{attribute.name}' is declared as "
                        f"'{direction}' but is used as the {side} of a "
                        "connection; boundary ports are inputs at the start "
                        "and outputs at the end"
                    )
            return
        if usage.direction != expected:
            raise ValueError(
                f"Boundary port '{usage.name}' of '{system.name}' is declared "
                f"as '{usage.direction}' but is used as the {side} of a "
                "connection; boundary ports are inputs at the start and "
                "outputs at the end"
            )
