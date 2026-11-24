"""Pure SSV emission from the parser-free projection model."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from pyssp_standard import SSV

from pyssp_sysml.core.paths import ensure_parent_dir
from pyssp_sysml.emit.values import fixed_count, format_value
from pyssp_sysml.projection.model import Attribute, AttributeDef


def parameter_set_resource(prefix: str, set_name: str) -> str:
    """Archive-relative path of one parameter set inside an SSP."""
    prefix = prefix.strip().strip("/")
    return f"{prefix}/{set_name}.ssv" if prefix else f"{set_name}.ssv"


def populate_parameter_set(
    ssv: SSV,
    parameter_pairs: Iterable[tuple[str, Attribute]],
    *,
    base_index: int = 0,
) -> None:
    for name, attribute in parameter_pairs:
        data_type = attribute.type_name or ""
        if attribute.value is None:
            continue

        if isinstance(attribute.value, (list, tuple)):
            for idx, item in enumerate(attribute.value, start=base_index):
                indexed_name = f"{name}[{idx}]"
                formatted = format_value(data_type, item)
                ssv.add_parameter(indexed_name, formatted, type_name=data_type)
            continue

        formatted = format_value(data_type, attribute.value)
        ssv.add_parameter(name, formatted, type_name=data_type)


def build_ssv(
    ssv: SSV,
    definition: AttributeDef,
    *,
    base_index: int = 0,
) -> None:
    """Write one projected parameter set into an open SSV document."""
    pairs = [
        (name, attribute)
        for name, attribute in definition.attributes.items()
        if attribute.value is not None
    ]
    if not pairs:
        raise ValueError(f"Parameter set '{definition.name}' has no values")
    for name, attribute in pairs:
        if not attribute.multiplicity:
            continue
        count = fixed_count(attribute.multiplicity, name)
        if not isinstance(attribute.value, tuple) or len(attribute.value) != count:
            raise ValueError(
                f"Parameter set member '{name}' must provide {count} values "
                f"for [{attribute.multiplicity}]"
            )

    ssv.xml.name = definition.name
    populate_parameter_set(ssv, pairs, base_index=base_index)


def write_parameter_set(
    definition: AttributeDef,
    output_path: Path,
    *,
    base_index: int = 0,
) -> Path:
    """Write one projected parameter set as an SSV file.

    ``base_index`` is the first array index emitted in parameter names, e.g.
    0 -> ``waypointX_km[0]`` and 1 -> ``waypointX_km[1]``.
    """
    ensure_parent_dir(output_path)
    with SSV(output_path, mode="w") as ssv:
        build_ssv(ssv, definition, base_index=base_index)
    return output_path
