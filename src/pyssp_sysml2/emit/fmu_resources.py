"""Resolve the FMU resources named by a projected composition."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pyssp_sysml2.projection.model import PartDef, SystemModel


@dataclass(frozen=True)
class _FmuResource:
    part_def: PartDef
    source: Path | None
    resource_name: str


def resolve_fmu_source(source: str, fmu_root: Path | None) -> Path:
    path = Path(source).expanduser()
    if not path.is_absolute():
        path = (fmu_root or Path.cwd()) / path
    return path.resolve()


def collect_fmu_resources(
    model: SystemModel,
    fmu_root: Path | None,
    *,
    allow_missing: bool = False,
) -> list[_FmuResource]:
    resources: list[_FmuResource] = []
    for part in model.components:
        resource_name = part.resource_name
        if not part.fmu_raw_source:
            # No FMU authored yet: the design structure leaves the component
            # unpopulated (empty SSD source).
            resources.append(_FmuResource(part, None, resource_name))
            continue

        source = resolve_fmu_source(part.fmu_raw_source, fmu_root)
        if not source.exists():
            if not allow_missing:
                raise FileNotFoundError(
                    f"FMU source for {part.name} does not exist: {source}"
                )
            resources.append(_FmuResource(part, None, resource_name))
            continue
        if source.is_file() and source.suffix.lower() != ".fmu":
            raise ValueError(
                f"FMU source for {part.name} must be a .fmu file or an "
                f"extracted FMU directory, got: {source}"
            )
        if source.is_dir() and not (source / "modelDescription.xml").is_file():
            raise FileNotFoundError(
                "FMU directory does not contain modelDescription.xml: "
                f"{source}"
            )

        resources.append(
            _FmuResource(
                part_def=part,
                source=source,
                resource_name=resource_name,
            )
        )
    return resources
