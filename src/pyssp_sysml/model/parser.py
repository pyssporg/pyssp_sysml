"""Compatibility shim for :mod:`pycps_sysml.model.parser`.

The parser lives in ``pycps_sysml``; this module keeps the old import path
resolvable. Shims stay in the package until a deliberate layout change retires
them: ``tests/test_module_layout.py`` ratchets each one to a docstring plus a
single ``import *``, so no removal release is scheduled and no shim carries
logic. Import the owning module directly in new code.
"""

from pycps_sysml.model.parser import *  # noqa: F403
