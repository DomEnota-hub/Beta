# Stage 1/15: Ermak RE1 public mirror, source identity still unresolved (2026-11-10)

**Status:** IN_PROGRESS. Non-runtime bibliographic research. Donor `Test-` remains pinned and read-only.

## Verified publication locator
The third-party index at https://www.rcit.su/techinfoV5.html lists **ИДМБ.661142.009РЭ1 / 3ТС.001.012РЭ1**, book 1, electrical circuits for 2ЭС5К/3ЭС5К, attributed to ОАО ВЭлНИИ. It states the mirrored edition is valid as of **01.11.2007** and explicitly warns that the book may diverge from manuals supplied with individual locomotives and may include equipment removed in later builds. The public text at https://www.rcit.su/techinfoV51.html includes §6.8 (МСУД-Н) and §7 (diagnostic information of МСУД-Н).

**This establishes the existence and historical subject of a publicly accessible RE1 mirror.** It does not establish that the internal ID `ER-AUDIT-MFR-RE1-PUBLIC` refers to precisely this publication, the correct edition for a specific locomotive, current validity in 2026, or applicability to later **МСУД-015**.

## Source-audit impact
The pinned Ermak audit and triage both retain `ER-AUDIT-MFR-RE1-PUBLIC` as **SOURCE_GAP / 56 occurrences**. This count is **unchanged**. The new `ermak-re1-public-mirror-evidence.candidate.json` records the external locator without mapping any individual diagnostic card, permitting actions, or publishing runtime content.

`qa/validate_ermak_re1_public_mirror.py` and 12 negative/positive regression tests reject a false edition upgrade, source-ID match, runtime promotion, MSUD-015 applicability, and loss of the 56 unresolved occurrences. The existing stage-1 triage workflow runs them alongside previous gates.

## Next evidence required
Obtain the original manufacturer-issued RE1 copy and amendment history **for the exact execution**; recover the original source-ID registry mapping for `ER-AUDIT-MFR-RE1-PUBLIC`; then compare clauses against the affected diagnostic cards and their safety classification. Only a reviewed, evidence-backed subset may later leave quarantine.

No Android runtime/UI/diagnostic behavior was modified. Stage 1 remains open.
