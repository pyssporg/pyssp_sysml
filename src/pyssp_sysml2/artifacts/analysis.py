"""Analysis composition wrapper: load, select, enforce, project, emit."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path

from pycps_sysml2.metadata.roles import SSP_ROLES
from pycps_sysml2.model import load
from pycps_sysml2.parameters.configuration import scope_analysis_to_root
from pycps_sysml2.parameters.constraints import enforce_constraints
from pycps_sysml2.parameters.selection import analysis_selection
from pycps_sysml2.parameters.variation import resolve_selected

from pyssp_sysml2.emit.analysis import (  # noqa: F401 - documented compatibility name
    AnalysisArtifacts,
)
from pyssp_sysml2.emit.analysis import build_analysis
from pyssp_sysml2.projection import project_analysis


def generate_analysis(
    architecture_path: Path,
    output_dir: Path,
    composition: str,
    *,
    model_name: str,
    target_ssd: str = "SystemStructure.ssd",
    selections: Mapping[str, str] | None = None,
    includes: Sequence[Path | str] = (),
    base_index: int = 0,
) -> AnalysisArtifacts:
    """Write ``analysis.json`` and, for one applied set, its SSV and SSM.

    ``base_index`` is the first array index emitted in SSV entry and SSM
    mapping names, e.g. 0 -> ``waypointX_km[0]`` and 1 -> ``waypointX_km[1]``.

    ``selections`` resolves variation points in the analysis before generation;
    see :func:`pyssp_sysml2.parameters.variation.resolve`. When it is ``None``,
    the analysis's model-level configuration binds the selection, via
    :func:`pyssp_sysml2.parameters.configuration.derived_selection`. The
    ``sut`` usage is then retyped to the configuration's root composition, so
    inherited parts, ports, connections, and binds resolve as before. An
    explicit map wins, so a caller can still force an illegal combination and
    have the constraints reject it. An analysis that carries an unselected
    variation point fails instead of emitting a flat scenario.

    ``includes`` names additional definition roots (files or directories)
    merged into the loaded architecture; pass
    :func:`pycps_sysml2.core_definitions` to supply the dialect core. Empty
    (the default) loads only the model's own declarations.
    """
    architecture = load(architecture_path, *includes)
    if selections is None:
        selections = analysis_selection(architecture, composition, roles=SSP_ROLES)
    scope_analysis_to_root(architecture, composition, roles=SSP_ROLES)
    architecture, canonical = resolve_selected(
        architecture, composition, selections or {}, roles=SSP_ROLES
    )
    enforce_constraints(architecture, composition, canonical)
    model = project_analysis(
        architecture,
        composition,
        model_name=model_name,
        target_ssd=target_ssd,
        base_index=base_index,
    )
    return build_analysis(model, output_dir, base_index=base_index)
