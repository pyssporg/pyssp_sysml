# Case: `inheritance`

The fixture record for this directory. It says what the bytes cannot: why the
case exists, which oracle proves it, and how the output may be normalized.

- **Conversion:** `architecture.sysml` (SysML v2) → `SystemStructure.ssd`
- **Requirement / fault:** a `part def DerivedLink :> BaseLink` must export the
  ports and connections it inherits before the members it declares, and a
  `port def ExtraSignal :> Signal` must export the inherited `value` member
  before `flag`. Reading only directly declared members drops the inherited
  interface and the nested system, while the remaining document still
  validates.
- **Level:** component
- **Input:** `architecture.sysml` — synthetic, authored for this case
  (package `InheritanceGolden`, composition `InheritanceComposition`); no
  external source, no licence obligation
- **Expected:** the committed artifact listed under *Artifacts* below
- **Independent oracle:** `pyssp_standard` facade — `SSD` re-parses the document
  and runs `check_compliance()` (XSD plus semantic validators). The writer is
  this repository; the checker is not.
- **Comparison:** exact bytes against the committed file (unified diff on
  mismatch), plus parsed structure through the facade for both the generated and
  the committed copy
- **Normalization:** none; the writer is deterministic
- **Volatile fields:** none. `guid` is `uuid5` of `pyssp_sysml2/<package>/<part>`,
  not random.
- **Update policy:** `UPDATE_GOLDENS=1`, read the diff, commit inputs and outputs
  together; refused when `CI` is set
- **Notes:** the derived definition has no parameters and no declared ports at
  the composition level, so the SSD isolates the inheritance effect: one nested
  system whose connectors and connections come from an ancestor, then its own.

## Artifacts

Generated from `architecture.sysml`; every path is relative to this directory.

| Path | Kind |
| --- | --- |
| `SystemStructure.ssd` | SSD system structure, inherited and own connectors/connections |

`architecture.sysml` and this file are inputs and provenance, not goldens.

## What this case proves

If the case is deleted, a regression to declared-member-only enumeration has no
byte-level evidence: the inherited ports `u` and `y`, the inherited connection
`u -> sink.u`, and the inherited `ExtraSignal.value` member would disappear
without any remaining document becoming invalid.

## Update history

| Date | Change | Reason |
| --- | --- | --- |
| 2026-11-19 | Created | A derived part def must emit effective, inherited members |
