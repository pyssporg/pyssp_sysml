"""Pure SSP packaging from the parser-free projection model."""

from __future__ import annotations

import json
import tempfile
import warnings
from collections.abc import Mapping
from pathlib import Path, PurePosixPath

from pyssp_standard import (
    Component,
    FMU,
    SSD,
    SSP,
    System,
    copy_resource_directory,
    validate_component_fmu,
)

from pyssp_sysml.core.paths import ensure_parent_dir
from pyssp_sysml.emit.fmu_resources import _FmuResource, collect_fmu_resources
from pyssp_sysml.emit.ssd import build_ssd
from pyssp_sysml.emit.ssv import parameter_set_resource, write_parameter_set
from pyssp_sysml.projection.model import SystemModel

DEFAULT_PARAMETER_SET_PREFIX = "resources/parameter_sets"
SELECTION_ENTRY = "extra/org.pyssp/selection.json"


def _iter_components(system: System):
    for element in system.elements:
        if isinstance(element, System):
            yield from _iter_components(element)
        elif isinstance(element, Component):
            yield element


def _validate_ssd_components(
    system: System,
    resources: dict[str, Path | None],
) -> None:
    resources_by_source = {
        f"resources/{resource_name}": source
        for resource_name, source in resources.items()
    }
    model_descriptions: dict[Path, object] = {}

    for component in _iter_components(system):
        if not component.source:
            # Design-first export: the component has no FMU yet.
            continue
        if component.source not in resources_by_source:
            raise ValueError(
                f"SSD component '{component.name}' references unknown FMU "
                f"resource '{component.source}'"
            )
        source = resources_by_source[component.source]
        if source is None:
            # Design-first export: the resource is intentionally not packaged.
            continue
        if source not in model_descriptions:
            with FMU(source, mode="r") as fmu:
                with fmu.model_description as md:
                    model_descriptions[source] = md.xml
        validate_component_fmu(
            component,
            model_descriptions[source],
            source=str(source),
        )


def _unique_resources(resources: list[_FmuResource]) -> dict[str, Path | None]:
    unique: dict[str, Path | None] = {}
    for resource in resources:
        if (
            resource.resource_name in unique
            and unique[resource.resource_name] != resource.source
        ):
            raise ValueError(
                f"FMU resource name '{resource.resource_name}' is used by "
                f"{resource.part_def.name} and another part definition with a "
                "different source"
            )
        unique[resource.resource_name] = resource.source
    return unique


def _add_fmu_resource(
    archive: SSP, source: Path, resource_name: str
) -> None:
    if source.is_dir():
        copy_resource_directory(
            source,
            archive.runtime.resolve("resources"),
            resource_name,
        )
    else:
        archive.runtime.add_file(source, target_name=f"resources/{resource_name}")


def _normalise_parameter_set_prefix(prefix: str) -> str:
    cleaned = str(prefix).strip().strip("/")
    if not cleaned:
        return ""
    if "\\" in cleaned:
        raise ValueError(
            "parameter_set_prefix must use '/' separators inside the archive"
        )
    path = PurePosixPath(cleaned)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(
            "parameter_set_prefix must be a relative archive path without '..'"
        )
    return path.as_posix()


def _selection_document(
    composition: str,
    selections: Mapping[str, str],
    configuration: str | None = None,
) -> str:
    """Deterministic JSON record of one build's variant selection."""
    document: dict[str, object] = {"composition": composition}
    if configuration:
        document["configuration"] = configuration
    document["selections"] = dict(sorted(selections.items()))
    return json.dumps(document, indent=2) + "\n"


def build_ssp(
    model: SystemModel,
    output_path: Path,
    *,
    parameter_set_prefix: str = DEFAULT_PARAMETER_SET_PREFIX,
    fmu_root: Path | None = None,
    type_check: bool = True,
    validate_fmus: bool = True,
    allow_missing_fmus: bool = False,
    selections: Mapping[str, str] | None = None,
    configuration: str | None = None,
    base_index: int = 0,
) -> Path:
    """Package one projected composition and its built FMUs as an SSP."""
    parameter_set_prefix = _normalise_parameter_set_prefix(parameter_set_prefix)
    fmu_resources = collect_fmu_resources(
        model, fmu_root, allow_missing=allow_missing_fmus
    )
    for resource in fmu_resources:
        if resource.source is None:
            warnings.warn(
                f"{resource.part_def.name}: FMU source is missing; the "
                "component is exported without its FMU (design structure)",
                stacklevel=2,
            )
    unique_resources = _unique_resources(fmu_resources)

    ensure_parent_dir(output_path)

    with tempfile.TemporaryDirectory(prefix="pyssp_ssp_") as temp_dir:
        temp_path = Path(temp_dir)
        ssd_path = temp_path / "SystemStructure.ssd"
        with SSD(ssd_path, mode="w") as ssd:
            build_ssd(
                ssd,
                model,
                type_check,
                parameter_set_prefix=parameter_set_prefix,
            )
            if validate_fmus:
                assert ssd.system is not None
                _validate_ssd_components(ssd.system, unique_resources)

        ssv_paths = []
        for definition in model.parameter_sets:
            ssv_path = write_parameter_set(
                definition,
                temp_path / f"{definition.name}.ssv",
                base_index=base_index,
            )
            ssv_paths.append((definition, ssv_path))

        with SSP(output_path, mode="w") as archive:
            archive.runtime.add_file(ssd_path, target_name="SystemStructure.ssd")
            if selections:
                selection_path = temp_path / "selection.json"
                selection_path.write_text(
                    _selection_document(model.name, selections, configuration),
                    encoding="utf-8",
                )
                archive.runtime.add_file(
                    selection_path, target_name=SELECTION_ENTRY
                )
            for resource_name, source in sorted(unique_resources.items()):
                if source is None:
                    continue
                _add_fmu_resource(archive, source, resource_name)
            for definition, ssv_path in ssv_paths:
                archive.runtime.add_file(
                    ssv_path,
                    target_name=parameter_set_resource(
                        parameter_set_prefix, definition.name
                    ),
                )

    return output_path
