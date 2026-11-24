---
id: INFO-020
type: info
title: Local setup
summary: Create a virtual environment, install the two direct-URL dependencies, and install the package editable; sysmlpy is transitive.
date: 2026-11-05
status: current
---

# Local setup

Standard setup:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install -e .
```

`requirements-dev.txt` is a single `-e ".[dev]"` line. It installs the runtime
dependencies from the release wheels pinned in `pyproject.toml`; to develop
against the `pyssp_standard_exp` sibling checkout, install that tree
editable after it as an override (the flat ecosystem workspace keeps it one
level above this repository):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
python3 -m pip install -e ../pyssp_standard_exp
```

`pyproject.toml` declares two direct-URL wheels:

- `pycps-sysml` 0.4.0, which pins `sysmlpy==0.96.4` itself and depends on
  `pyssp-sysml-definitions`;
- `experimental-pyssp-standard` 0.9.4.dev0.

`sysmlpy` is no longer a direct dependency: this package never imports the
grammar (`AD-004`). The editable install provides the `pyssp` console script.
Without it, run `PYTHONPATH=src python3 -m pyssp_sysml.cli`.
