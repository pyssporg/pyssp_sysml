---
id: IMP-017
type: imp
title: Re-pin pycps-sysml2 to the 0.3.0 release
summary: The v0.3.0 wheel is published; pyproject now points at it instead of v0.2.0.
date: 2026-11-20
status: implemented
---

# Re-pin pycps-sysml2 to the 0.3.0 release

`pyssp_sysml2` 0.6.0 is a breaking adaptation to `pycps_sysml2` 0.3.0: typed
experiment containers replace the `pyssp_*` control attributes, the control
metadata plumbing is gone, and flattening moved to the `--flat-connector` export
option.

While `pyproject.toml` pinned the v0.2.0 wheel, a clean install resolved the old
dialect and the adapted imports failed.

**Done.** The dependency points at
`pycps_sysml2-0.3.0-py3-none-any.whl` from the v0.3.0 release, and
`05-operation/local-setup.md` names 0.3.0. The wheel downloads from the pinned
URL, and the suite (`-m "not slow"`) and `ruff check src tests` pass against the
adapted code.
