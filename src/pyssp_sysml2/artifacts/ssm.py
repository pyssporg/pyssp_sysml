"""SSM composition wrapper: load, project the mappings, emit."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from pyssp_standard import SSM

from pycps_sysml2.model import load

from pyssp_sysml2.core.paths import ensure_directory
from pyssp_sysml2.emit.ssm import build_ssm
from pyssp_sysml2.projection import project_mappings


def generate_parameter_mappings(
    architecture_path: Path,
    output_dir: Path,
    composition: str,
    *,
    includes: Sequence[Path | str] = (),
    base_index: int = 0,
) -> list[Path]:
    """Write one SSM file per (set, component usage) explicit mapping.

    Whole-object identity bindings need no SSM; they map to an SSP
    ``ParameterBinding`` with ``prefix="<component>."`` instead.

    ``base_index`` is the first array index emitted in mapping source and
    target names, e.g. 0 -> ``waypoints_x_km[0]`` and 1 -> ``waypoints_x_km[1]``.

    ``includes`` names additional definition roots (files or directories)
    merged into the loaded architecture; pass
    :func:`pycps_sysml2.core_definitions` to supply the dialect core. Empty
    (the default) loads only the model's own declarations.
    """
    architecture = load(architecture_path, *includes)
    system = architecture.get_part_def(composition)

    written: list[Path] = []
    for spec in project_mappings(architecture, system, base_index=base_index):
        if spec.identity:
            continue
        component_name = spec.component_name.replace(".", "_")
        output_path = output_dir / f"{spec.set_name}_{component_name}.ssm"
        ensure_directory(output_dir)
        with SSM(output_path, mode="w") as ssm:
            build_ssm(ssm, spec)
        written.append(output_path)
    return sorted(written)
