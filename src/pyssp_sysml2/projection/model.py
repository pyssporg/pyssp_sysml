"""Parser-free intermediate model used by every SSP artifact emitter.

The records here are plain dataclasses. They carry no ``pycps_sysml2`` type,
no reference to a loaded architecture, and no resolution step: the projection
layer has already resolved every usage-to-definition pointer and every
inherited member. An emitter may import this module and nothing else from the
SysML side.

Fields are trimmed to what the emitters read. ``PartDef`` deliberately carries
no bindings or constraints: those are resolved into ``MappingSpec`` records by
the projection layer and are never read while writing an artifact.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Attribute:
    """A port member or a parameter-set member, already type-resolved."""

    name: str
    type_name: str | None
    multiplicity: str | None = None
    value: object = None
    direction: str | None = None
    doc: str | None = None


@dataclass(frozen=True)
class AttributeDef:
    """A parameter-set definition: one SSV."""

    name: str
    attributes: Mapping[str, Attribute] = field(default_factory=dict)
    doc: str | None = None


@dataclass(frozen=True)
class PortDef:
    """A port definition with its effective members."""

    name: str
    attributes: Mapping[str, Attribute] = field(default_factory=dict)
    is_parameter_interface: bool = False
    scalar: bool = False


@dataclass(frozen=True)
class PortUsage:
    """A port usage with its resolved direction and definition pointer."""

    name: str
    type_name: str | None = None
    direction: str | None = None
    multiplicity: str | None = None
    conjugated: bool = False
    member_directions: Mapping[str, str | None] = field(default_factory=dict)
    definition: PortDef | None = None


@dataclass(frozen=True)
class PartUsage:
    """A part usage with its pre-resolved definition pointer."""

    name: str
    type_name: str | None = None
    definition: PartDef | None = None


@dataclass(frozen=True)
class ParameterItem:
    """One parameter connector name, indices already expanded."""

    name: str
    type_name: str | None


@dataclass(frozen=True)
class Connection:
    """One connection with both endpoints resolved to port usages."""

    key: str
    source_part: str | None
    source_port: str
    destination_part: str | None
    destination_port: str
    source: PortUsage | None = None
    destination: PortUsage | None = None


@dataclass(frozen=True)
class PartDef:
    """A part definition flattened over its inherited members."""

    name: str
    doc: str | None = None
    ports: Mapping[str, PortUsage] = field(default_factory=dict)
    parts: Mapping[str, PartUsage] = field(default_factory=dict)
    connections: Sequence[Connection] = field(default_factory=tuple)
    is_parameter_interface: bool = False
    parameter_items: Sequence[ParameterItem] = field(default_factory=tuple)
    fmu_declared: bool = False
    fmu_source: str = ""
    fmu_implementation: str | None = None
    fmu_raw_source: str | None = None
    resource_name: str = ""


@dataclass(frozen=True)
class MappingSpec:
    """One set-to-component parameter mapping."""

    set_name: str
    identity: bool
    component_name: str
    entries: Sequence[tuple[str, str]] = field(default_factory=tuple)


@dataclass(frozen=True)
class Experiment:
    """The typed experiment container projected for the SSD."""

    name: str
    start_time: float
    stop_time: float
    step_size: float | None = None
    tolerance: float | None = None


@dataclass(frozen=True)
class SystemModel:
    """A composition ready for SSD or SSP emission."""

    name: str
    root: PartDef
    doc: str | None = None
    is_analysis: bool = False
    ssp_source: str | None = None
    experiment: Experiment | None = None
    parameter_model: bool = False
    parameter_sets: Sequence[AttributeDef] = field(default_factory=tuple)
    mappings: Sequence[MappingSpec] = field(default_factory=tuple)
    components: Sequence[PartDef] = field(default_factory=tuple)


@dataclass(frozen=True)
class AnalysisModel:
    """One Analysis composition ready for descriptor emission."""

    model_name: str
    analysis_name: str
    model_composition: str
    sut: str
    target_ssd: str
    description: str | None
    experiment: Experiment
    scenario_set: AttributeDef | None = None
    scenario_mapping: MappingSpec | None = None
    model_source: str | None = None
