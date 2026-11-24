"""Projection stage: loaded SysML architecture to parser-free model.

Importing this package is the only way the SSP emission path reaches
``pycps_sysml`` analysis helpers. The records in
:mod:`pyssp_sysml.projection.model` are what the emitters accept.
"""

from pyssp_sysml.projection.model import (
    AnalysisModel,
    Attribute,
    AttributeDef,
    Connection,
    Experiment,
    MappingSpec,
    ParameterItem,
    PartDef,
    PartUsage,
    PortDef,
    PortUsage,
    SystemModel,
)
from pyssp_sysml.projection.system import (
    fmu_implementation_problems,
    project_analysis,
    project_composition,
    project_mappings,
    project_parameter_sets,
    project_part,
    project_system,
)

__all__ = [
    "AnalysisModel",
    "fmu_implementation_problems",
    "Attribute",
    "AttributeDef",
    "Connection",
    "Experiment",
    "MappingSpec",
    "ParameterItem",
    "PartDef",
    "PartUsage",
    "PortDef",
    "PortUsage",
    "SystemModel",
    "project_analysis",
    "project_composition",
    "project_mappings",
    "project_parameter_sets",
    "project_part",
    "project_system",
]
