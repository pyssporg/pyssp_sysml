"""Emission stage: parser-free projection model to SSP-family artifacts.

Every ``build_*`` function here accepts a
:mod:`pyssp_sysml.projection.model` record and writes one artifact. Nothing
in this package imports ``pycps_sysml``; loading, selection, and projection
happen in the ``artifacts`` composition wrappers.
"""

from pyssp_sysml.emit.analysis import AnalysisArtifacts, build_analysis
from pyssp_sysml.emit.ssd import build_ssd, expected_connector_names
from pyssp_sysml.emit.ssm import build_ssm
from pyssp_sysml.emit.ssp import build_ssp
from pyssp_sysml.emit.ssv import build_ssv, parameter_set_resource, write_parameter_set

__all__ = [
    "AnalysisArtifacts",
    "build_analysis",
    "build_ssd",
    "build_ssm",
    "build_ssp",
    "build_ssv",
    "expected_connector_names",
    "parameter_set_resource",
    "write_parameter_set",
]
