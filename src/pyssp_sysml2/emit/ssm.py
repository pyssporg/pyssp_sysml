"""Pure SSM emission from the parser-free projection model."""

from __future__ import annotations

from pyssp_standard import SSM

from pyssp_sysml2.projection.model import MappingSpec


def build_ssm(ssm: SSM, mapping: MappingSpec) -> None:
    """Write one projected parameter mapping into an open SSM document."""
    for source, target in mapping.entries:
        ssm.add_mapping(source, target)
