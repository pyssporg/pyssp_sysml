"""FMI export left ``pyssp_sysml`` in 0.4.0.

Model descriptions now come from ``pyfmi_interfaces``. The package must not keep a
compatibility export or a dormant ``artifacts.fmi`` module: an importable name
would be a second, unmaintained implementation.
"""

from __future__ import annotations

import importlib

import pytest

import pyssp_sysml
from pyssp_sysml import artifacts


def test_generate_model_descriptions_is_not_exported() -> None:
    assert not hasattr(pyssp_sysml, "generate_model_descriptions")


def test_artifacts_has_no_fmi_module() -> None:
    assert not hasattr(artifacts, "fmi")
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("pyssp_sysml.artifacts.fmi")
