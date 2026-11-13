# Stage 1/15: CHME3 priority scheme source-edge audit (2026-11-10)

**Status: IN_PROGRESS, not a source-approval or feature-completion certificate.** Read-only donor: `DomEnota-hub/Test-` at `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Only Beta audit branch changed.

## Verified scope and its limitations

Three highest-volume unresolved scheme targets account for **222 of 610** CHME3 unresolved source/variant/target triples: `CHME3-SCH-PNEUMATIC` (84: 28 per CHME3/CHME3T/CHME3E), `CHME3-SCH-CONTROL` (72: 24 each), and `CHME3-SCH-TRACTION` (66: 22 each). All **222 original source→variant→target tuples** can be compared one-for-one with the existing non-runtime `raw-target-evidence.candidate.json` source groups and the pinned source-audit mappings.

For each target, an original **donor-authored training/navigation scheme object** survives in the preserved `docs/locomotives/chme3/atlas_schemes_functional.json` snapshot, at `/records/6`, `/records/8`, and `/records/7`, respectively. The original donor document Git blob is `ec31051ec39e0053141d173729913e3abcabd1e5`; the three exact object SHA-256 digests and original source IDs are pinned in `chme3-priority-scheme-evidence.candidate.json`. The original objects explicitly say `evidenceStatus=TRAINING_REFERENCE`, `actionAuthority=INFORMATION_ONLY`. The donor's own disclaimer states these are logical atlas navigation schemes, **not the electrical/pneumatic principle drawings for a particular locomotive**.

This is **preservation and referential identity**, not validation of the original bibliography, manufacturer-approved diagrams, current edition, physical installation, exact wire/terminal numbers, operating limits, or authorized crew actions. Matching a shared donor object to all three series does **not** prove that its implementation is identical across all three variants. No runtime links are created, no candidate is promoted, and **all 610 CHME3 unresolved references remain quarantined**. Ermak's 548 unresolved occurrences and other Stage 1 blockers remain unchanged.

## Reproducible checks

- `qa/validate_chme3_priority_schemes.py`: independently recomputes 222 triples from pinned source-audit and raw source groups; checks exact donor mappings and per-variant distribution; resolves original JSON pointers and verifies three object SHA-256 values; enforces `TRAINING_REFERENCE`, `INFORMATION_ONLY`, false manufacturer/current-authority/installation gates and zero runtime publication.
- `qa/test_chme3_priority_schemes.py`: **17** regression cases including false authority, wrong variant counts with unchanged totals, lost/forged source edges, broken source mapping, object/blob modification and unsafe promotion.
- `.github/workflows/stage1-source-link-triage.yml`: runs these checks alongside existing quarantine validation. **Do not mark the tests verified until the workflow is terminal SUCCESS on the final branch HEAD.**

## Next concrete work

Find manufacturer-issued original pneumatic, control and traction circuit diagrams with **edition, exact page/sheet and series/variant applicability**; independently confirm each `evidenceRefs` identity and current authority. Only then reconsider individual source triples, under the safety gate and with a negative regression test. Keep all unverified links out of runtime. Stage 2 must not begin solely because the 222 source identities are reconciled.
