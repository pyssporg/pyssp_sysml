---
id: IMP-017
type: imp
title: Re-pin pycps-sysml2 to the 0.3.0 release
summary: v0.6.0 adapts to dialect 0.3.0, but pyproject still pins the v0.2.0 release wheel; the pin moves when 0.3.0 is published.
date: 2026-11-19
status: selected
---

# Re-pin pycps-sysml2 to the 0.3.0 release

`pyssp_sysml2` 0.6.0 is a breaking adaptation to `pycps_sysml2` 0.3.0: typed
experiment containers replace the `pyssp_*` control attributes, the control
metadata plumbing is gone, and flattening moved to the `--flat-connector` export
option.

`pyproject.toml` still pins the v0.2.0 release wheel URL. Development uses the
editable sibling checkout, so the workspace runs the new dialect, but a clean
install resolves the old wheel and the adapted imports fail.

**Candidate.**

- Publish `pycps_sysml2` 0.3.0, then point the dependency at the v0.3.0 wheel.
- Do not edit the pin as part of the adaptation; the release chore owns it.
- Verify with a no-deps editable install of the published wheel and this suite.
