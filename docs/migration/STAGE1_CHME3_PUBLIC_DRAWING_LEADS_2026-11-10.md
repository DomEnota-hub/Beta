# Stage 1/15: CHME3 electrical drawing archive leads (2026-11-10)

**Status: IN_PROGRESS. This is a non-runtime source-acquisition lead, not an approved factory drawing or completed migration.**

Read-only donor: `DomEnota-hub/Test-` at `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Target: Beta branch `audit/information-block-gaps-20261014`.

## What was actually verified
The public catalog of the third-party site "ЛокомотивщиК" has two separately labeled listings, both dated 31 July 2012: CHME3T electrical schemes (advertised RAR/GIF) and CHME3E electrical scheme (advertised RAR/GIF). Their detail pages exist. This is **only proof that catalog entries exist**. The archives themselves were **not acquired or hashed**; neither publisher, factory drawing number, sheet, revision, serial range, modernization nor distribution rights were verified.

Catalog pages:
- CHME3T: https://lokomotivishim.ucoz.ru/load/skhemy_teplovoza/chmeh3_v_s/chmeh3t_skhemy_ehlektricheskie/163-1-0-1802
- CHME3E: https://lokomotivishim.ucoz.ru/load/skhemy_teplovoza/chmeh3_v_s/chmeh3eh_skhema_ehlektricheskaja/163-1-0-1803

`chme3-public-drawing-leads.candidate.json` records **two leads and six search-target associations**, not resolved source edges. `qa/validate_chme3_public_drawing_leads.py` and 12 regression tests prevent source claims, wrong variant links, invented drawing identifiers, unauthorized runtime import, or loss of quarantine. No candidate files are placed in Android assets.

## Gates before any source-link promotion
1. Obtain original archives legally, record SHA-256, inspect each drawing title block and original issuer.
2. Record factory document number, sheet, revision and unit/serial/modernization applicability.
3. Cross-check each candidate against the exact source target and pinned donor source audit; do not infer equivalence between CHME3, CHME3T and CHME3E.
4. Verify current authority and crew safety gate. Until then all **610 CHME3** source edges and **548 Ermak** source occurrences remain quarantined. History migration and 329-question licensing/pack remain open.

## Verification
This change adds a CI gate to `stage1-source-link-triage.yml`. Terminal CI results must be recorded separately in Issue #4; do not claim success before checking workflow conclusions. No Android UI or runtime content was changed.
