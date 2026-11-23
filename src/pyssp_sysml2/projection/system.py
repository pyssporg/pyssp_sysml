"""Project systems, parameter sets, mappings, and analyses.

All ``pycps_sysml2`` metadata, parameter-dialect, and role calls used by the
SSP generation path live in this module. The emitters never see an
``Architecture``.
"""

from __future__ import annotations

from collections.abc import Iterable

from pycps_sysml2.metadata.roles import (
    Experiment as PycpsExperiment,
    is_analysis,
    is_ssp_model,
    model_usage,
    read_experiment,
    require_resolved_variation,
    validate_role_markers,
)
from pycps_sysml2.metadata.fmu_metadata import require_fmu_metadata
from pycps_sysml2.metadata.ssp_metadata import ssp_metadata
from pycps_sysml2.model import Architecture, AttributeDefinition, PartDefinition
from pycps_sysml2.parameters.dialect.composition import (
    applied_sets,
    component_definitions,
    has_parameter_dialect,
    validate_parameter_dialect,
)
from pycps_sysml2.parameters.dialect.mapping import (
    mapping_specs,
    parameter_sets_for_generation,
    validate_applied_sets,
)
from pycps_sysml2.parameters.dialect.markers import validate_marker_definitions
from pycps_sysml2.parameters.policy import SSP_POLICY
from pycps_sysml2.parameters.variation import (
    require_resolved_attribute_variation,
)

from pyssp_sysml2.projection.model import (
    AnalysisModel,
    Attribute,
    AttributeDef,
    Experiment,
    MappingSpec,
    PartDef,
    SystemModel,
)
from pyssp_sysml2.projection.parts import Projector


def _experiment(experiment: PycpsExperiment | None) -> Experiment | None:
    if experiment is None:
        return None
    return Experiment(
        name=experiment.name,
        start_time=experiment.start_time,
        stop_time=experiment.stop_time,
        step_size=experiment.step_size,
        tolerance=experiment.tolerance,
    )


def _attribute_def(definition: AttributeDefinition) -> AttributeDef:
    return AttributeDef(
        name=definition.name,
        doc=definition.doc,
        attributes={
            name: Attribute(
                name=attribute.name,
                type_name=attribute.primitive_type_str(),
                multiplicity=attribute.multiplicity,
                value=attribute.value,
                direction=attribute.direction,
                doc=attribute.doc,
            )
            for name, attribute in definition.attributes.items()
        },
    )


def _mapping(spec: object) -> MappingSpec:
    return MappingSpec(
        set_name=spec.set_name,
        identity=spec.identity,
        component_name=spec.component_name,
        entries=tuple(tuple(entry) for entry in spec.entries),
    )


def project_composition(
    architecture: Architecture,
    composition: PartDefinition | str,
    *,
    base_index: int = 0,
    validate: bool = True,
    require_resolved: bool = True,
    with_connections: bool = True,
    with_parameter_sets: bool = True,
    with_mappings: bool = True,
    with_experiment: bool = True,
) -> SystemModel:
    """Resolve a composition name, or accept a definition, then project it."""
    if isinstance(composition, PartDefinition):
        system = composition
    else:
        system = architecture.resolve_part(composition)
        if system is None:
            raise ValueError(f"Unknown composition '{composition}'")
    return project_system(
        architecture,
        system,
        base_index=base_index,
        validate=validate,
        require_resolved=require_resolved,
        with_connections=with_connections,
        with_parameter_sets=with_parameter_sets,
        with_mappings=with_mappings,
        with_experiment=with_experiment,
    )


def fmu_implementation_problems(
    architecture: Architecture,
    composition: str,
    implementation: str,
) -> tuple[str, ...]:
    """Report FMU components whose implementation is not the requested one."""
    system = architecture.resolve_part(composition)
    assert system is not None  # the caller validated the composition first
    return require_fmu_metadata(
        architecture,
        component_definitions(architecture, system),
        implementation=implementation,
    )


def project_part(
    architecture: Architecture,
    part_def: PartDefinition,
    *,
    base_index: int = 0,
    parameter_model: bool = False,
    with_connections: bool = False,
) -> PartDef:
    """Project one definition, primarily for interface preflight."""
    projector = Projector(
        architecture,
        base_index=base_index,
        parameter_model=parameter_model,
        with_connections=with_connections,
    )
    return projector.part(part_def)


def project_system(
    architecture: Architecture,
    system: PartDefinition,
    *,
    base_index: int = 0,
    validate: bool = True,
    require_resolved: bool = True,
    with_connections: bool = True,
    with_parameter_sets: bool = True,
    with_mappings: bool = True,
    with_experiment: bool = True,
) -> SystemModel:
    """Project a loaded, post-selection composition for artifact emission."""
    if validate:
        validate_role_markers(architecture)
        if require_resolved:
            require_resolved_variation(architecture, system)
            require_resolved_attribute_variation(architecture, system)
        validate_parameter_dialect(architecture, system, policy=SSP_POLICY)

    parameter_model = has_parameter_dialect(
        architecture, system, policy=SSP_POLICY
    )
    mappings = (
        tuple(
            _mapping(spec)
            for spec in mapping_specs(
                architecture,
                system,
                policy=SSP_POLICY,
                base_index=base_index,
            )
        )
        if with_mappings and parameter_model
        else ()
    )
    parameter_sets = (
        tuple(
            _attribute_def(definition)
            for definition in parameter_sets_for_generation(
                architecture, system, policy=SSP_POLICY
            )
        )
        if with_parameter_sets and parameter_model
        else ()
    )

    projector = Projector(
        architecture,
        base_index=base_index,
        parameter_model=parameter_model,
        with_connections=with_connections,
    )
    root = projector.part(system)
    experiment = (
        _experiment(read_experiment(architecture, system, required=False))
        if with_experiment
        else None
    )
    source = ssp_metadata(architecture, system)
    return SystemModel(
        name=system.name,
        root=root,
        doc=system.doc,
        is_analysis=is_analysis(architecture, system),
        ssp_source=source.source if source is not None else None,
        experiment=experiment,
        parameter_model=parameter_model,
        parameter_sets=parameter_sets,
        mappings=mappings,
        components=tuple(projector.components),
    )


def project_parameter_sets(
    architecture: Architecture,
    system: PartDefinition,
    *,
    set_names: Iterable[str] | None = None,
    all_sets: bool = False,
) -> tuple[AttributeDef, ...]:
    """Project the parameter sets selected for SSV generation."""
    validate_marker_definitions(architecture)
    validate_parameter_dialect(architecture, system, policy=SSP_POLICY)
    validate_applied_sets(architecture, system, policy=SSP_POLICY)
    definitions = parameter_sets_for_generation(
        architecture,
        system,
        set_names=list(set_names) if set_names else None,
        all_sets=all_sets,
        policy=SSP_POLICY,
    )
    return tuple(_attribute_def(definition) for definition in definitions)


def project_mappings(
    architecture: Architecture,
    system: PartDefinition,
    *,
    base_index: int = 0,
) -> tuple[MappingSpec, ...]:
    """Project explicit parameter mappings for SSM emission."""
    return tuple(
        _mapping(spec)
        for spec in mapping_specs(
            architecture,
            system,
            policy=SSP_POLICY,
            base_index=base_index,
        )
    )


def project_analysis(
    architecture: Architecture,
    composition: str,
    *,
    model_name: str,
    target_ssd: str = "SystemStructure.ssd",
    base_index: int = 0,
) -> AnalysisModel:
    """Project one Analysis composition after selection and constraints."""
    analysis = architecture.get_part_def(composition)
    validate_role_markers(architecture)
    if not is_analysis(architecture, analysis):
        raise ValueError(
            f"Composition '{composition}' is not marked ':> Analysis'"
        )

    model_part_usage, model_definition = model_usage(architecture, analysis)
    if not is_ssp_model(architecture, model_definition):
        raise ValueError(
            f"Analysis '{composition}' composes '{model_part_usage.type_name}', "
            "which is not marked ':> SspModel'"
        )

    validate_marker_definitions(architecture)
    validate_parameter_dialect(architecture, analysis, policy=SSP_POLICY)
    sets = parameter_sets_for_generation(
        architecture, analysis, policy=SSP_POLICY
    )
    if len(sets) > 1:
        names = ", ".join(definition.name for definition in sets) or "none"
        raise ValueError(
            f"Analysis '{composition}' must apply at most one scenario parameter "
            f"set; found {names}"
        )

    model_applications = applied_sets(
        architecture, model_definition, policy=SSP_POLICY
    )
    if model_applications and sets:
        raise ValueError(
            f"Analysis '{composition}' applies a scenario set, but its sut "
            f"'{model_definition.name}' already applies one. A model-owned "
            "scenario is fixed for all analyses; remove the analysis set or move "
            "the scenario to the analysis."
        )

    experiment = read_experiment(architecture, analysis, required=True)
    assert experiment is not None
    metadata = ssp_metadata(architecture, model_definition)

    scenario_set = _attribute_def(sets[0]) if sets else None
    scenario_mapping = None
    prefix = f"{model_part_usage.name}."
    if scenario_set is not None:
        entries: list[tuple[str, str]] = []
        for spec in mapping_specs(
            architecture,
            analysis,
            policy=SSP_POLICY,
            base_index=base_index,
        ):
            for source, target in spec.entries:
                if not target.startswith(prefix):
                    raise ValueError(
                        f"Analysis mapping target '{target}' is not below "
                        f"'{model_part_usage.name}'"
                    )
                entries.append((source, target[len(prefix) :]))
        scenario_mapping = MappingSpec(
            set_name=scenario_set.name,
            identity=False,
            component_name=model_part_usage.name,
            entries=tuple(entries),
        )

    return AnalysisModel(
        model_name=model_name,
        analysis_name=composition,
        model_composition=model_definition.name,
        sut=model_part_usage.name,
        target_ssd=target_ssd,
        description=analysis.doc,
        experiment=_experiment(experiment),
        scenario_set=scenario_set,
        scenario_mapping=scenario_mapping,
        model_source=metadata.source if metadata is not None else None,
    )
