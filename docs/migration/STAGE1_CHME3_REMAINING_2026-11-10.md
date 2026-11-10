# Stage 1/15: remaining CHME3 source-edge audit (2026-11-10)

**IN_PROGRESS, NOT a source-approval or runtime-publishing certificate.** Donor `Test-` is read-only at `3176d6ee228f0ed4b78371f45209e10c1c724eff`.

The earlier three priority groups account for 222 of 610 unresolved source/variant/target triples. This pass independently cross-checks the **remaining 388 triples** across **16 targets**: CHME3 100, CHME3E 184, CHME3T 104. Each source edge must match the pinned source audit, a raw donor evidence group, its source variant, and a canonical mapping. All surviving source objects are located by JSON pointer and checked against their pinned SHA-256 and original document Git blob. The separate CHME3T electrodynamic-brake targets retain **8 cross-variant conflicts**; these are *not* approved by their presence in the donor.

The 16 targets include shared training/navigation diagrams, CHME3E-only technical views, and CHME3T EDB materials. Several CHME3E objects have no explicit `evidenceStatus` field; their `INFORMATION_ONLY` status is **not** manufacturer or current normative authority. An object with `REQUIRES_PROFILE_CHECK` is never silently downgraded to a crew action. Every one of the 610 unresolved links remains quarantined. No Android runtime data, UI, or diagnostic guidance is changed.

Machine-checkable non-runtime ledger: `chme3-remaining-scheme-evidence.candidate.json`. Validator: `qa/validate_chme3_remaining_schemes.py`. Negative regression suite: `qa/test_chme3_remaining_schemes.py` (**21 tests**). The stage-1 source-link workflow runs both checks. This is preservation of original identity, **not** verification of factory drawings, current edition, specific installation, page/sheet locator or permission for maintenance actions.

**Next evidence:** obtain manufacturer-issued schematics and verified revisions for each series/variant; match individual links to precise source pages/sheets. Resolve neither the 388 links nor the 222 priority links by name matching alone. Ermak 548 occurrences, exam question publication rights and history migration implementation remain separate blockers. Stage 2 must not start until Stage 1 is demonstrably complete.
