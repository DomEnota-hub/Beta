# Stage 1/15: CHME3T serial-dependent electrical scheme gate (2026-11-10)

**Status: IN_PROGRESS. Historical source warning, not a manufacturer approval or an implemented Android feature.**

Read-only donor: `Test-` at `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Only Beta audit artifacts are changed.

## New documentary distinction

Z. Kh. Notik, *Тепловозы ЧМЭ3, ЧМЭ3Т, ЧМЭ3Э*, 2nd edition, Transport, 1996, 444 pages, explicitly states in its preface that the **CHME3T electrical circuit was modified beginning with locomotive No. 6245**. The same preface distinguishes the CHME3T and CHME3E diagrams, and the table of contents separates their circuit descriptions (CHME3T chapter XVI §§81–91, CHME3E chapter XVII §§92–100). Evidence: https://pomogala.ru/books_4_teplovoz/notik_chme3_96.html ; bibliographic cross-check https://dntb-centr.ru/b/424 .

This is a **historical secondary publication**, not a currently valid factory drawing. The threshold is a **reason to require unit-specific verification**, not permission to automatically classify a locomotive's installed equipment. Serial number alone does not rule out later modifications. No exact factory drawing, sheet, revision, installation or current normative authority was confirmed.

## Audit impact and safe handling

The existing pinned donor audit contains **54 CHME3T-labelled unresolved electrical scheme edges** in three groups that cite `CHME3-SRC-NOTIK-1996`: `CHME3-SCH-CONTROL` (24), `CHME3-SCH-TRACTION` (22), `CHME3T-SCH-EDB` (8). These counts are independently checked against `source-audit.json`, the 222-edge priority ledger and 388-edge remaining ledger. The separate CHME3T EDB cross-variant mismatch remains blocked.

New non-runtime evidence: `chme3t-serial-revision-evidence.candidate.json`. Validator and **17 negative regression tests** reject a changed 6245 threshold, wrong series, false factory approval, missing serial/modernization gate, altered source identity, lost edges, crew-action promotion and runtime publication. This does not assert that all 54 edges refer to components affected by the historical modification. It only identifies where a **serial-aware source check** is required before approval.

**Quarantine unchanged: 610/610 CHME3 unresolved, 548 Ermak unresolved.** No candidate is promoted; no repair or high-voltage instruction is issued.

## Next concrete action

Obtain manufacturer-issued electrical drawings with document number, edition, sheet and explicit CHME3T applicability before/after 6245; verify actual unit number and modernization, and compare individual edges. Independently acquire corresponding CHME3 and CHME3E factory drawings and pneumatic documentation. Keep the stage open until original source authority and all other parity gates are demonstrably met.
