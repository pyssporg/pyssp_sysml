# Case: `core-definitions`

Input for the generator and CLI tests that opt into the bundled dialect core
definitions: a model that uses `SspModel` without declaring it, so the default
load leaves the marker unresolved and the opted-in load merges it from
`pycps_sysml2.core_definitions()`.

## Artifacts

| Path | Behaviour |
| --- | --- |
| `marker-user.sysml` | composition marked `:> SspModel` with no local marker definition, importing `PysspCore` for visibility |

## What this case proves

The file has no local marker definitions and imports `PysspCore`, so
`generate_ssd` fails with empty `includes` and succeeds once the caller passes
`includes=[pycps_sysml2.core_definitions()]`. A CLI test proves
`--core-definitions` is accepted and forwarded as that include; another proves
a repeated `--architecture` supplies a definition root directly, with the model
importing that root's package.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-05 | Case record and `marker-user.sysml` added | The generator option needs a marker-free model as reviewable SysML, not a Python literal |
| 2026-11-20 | Import `PysspCore` in `marker-user.sysml` | Package-scoped visibility after the pycps dialect-inheritance merge requires an explicit import |
