"""SSV composition wrapper: load, project the selected sets, emit."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from pathlib import Path

from pycps_sysml2.model import load

from pyssp_sysml2.core.paths import ensure_directory
from pyssp_sysml2.emit.ssv import (  # noqa: F401 - documented compatibility names
    parameter_set_resource,
    populate_parameter_set,
    write_parameter_set,
)
from pyssp_sysml2.projection import project_parameter_sets


def generate_parameter_sets(
    architecture_path: Path,
    output_dir: Path,
    composition: str,
    *,
    set_names: Iterable[str] | None = None,
    all_sets: bool = False,
    output_path: Path | None = None,
    includes: Sequence[Path | str] = (),
    base_index: int = 0,
) -> list[Path]:
    """Generate one SSV per parameter-set definition.

    With ``output_path`` exactly one set may be selected. Otherwise files are
    written as ``<output_dir>/<SetName>.ssv``.

    ``base_index`` is the first array index emitted in parameter names, e.g.
    0 -> ``waypointX_km[0]`` and 1 -> ``waypointX_km[1]``.

    ``includes`` names additional definition roots (files or directories)
    merged into the loaded architecture; pass
    :func:`pycps_sysml2.core_definitions` to supply the dialect core. Empty
    (the default) loads only the model's own declarations.
    """
    architecture = load(architecture_path, *includes)
    system = architecture.get_part_def(composition)
    definitions = project_parameter_sets(
        architecture,
        system,
        set_names=set_names,
        all_sets=all_sets,
    )
    if not definitions:
        return []

    if output_path is not None:
        if len(definitions) != 1:
            raise ValueError(
                "A single --output file requires exactly one parameter set; "
                f"selected {len(definitions)}"
            )
        return [write_parameter_set(definitions[0], output_path, base_index=base_index)]

    ensure_directory(output_dir)
    return [
        write_parameter_set(
            definition, output_dir / f"{definition.name}.ssv", base_index=base_index
        )
        for definition in definitions
    ]
