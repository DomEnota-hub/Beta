# Diagnostic corpus review before version authoring

Scope: the pinned `Test-@3176d6ee228f0ed4b78371f45209e10c1c724eff` diagnostic material already preserved in Beta. The [340-row inventory](data-migration/diagnostic-corpus-analysis.json) records each canonical scenario, exact donor path/blob (or VL80S runtime snapshot), graph shape and reachability, source references, variant applicability, extended donor routing and original candidate record profiles. It is reproduced by `qa/analyze_diagnostic_corpus.py --check`. The six unique donor blobs behind Ermak/CHME3/TEM2 scenario packs were also compared locally with the pinned Git tree; all matched. This is a structural and provenance inventory, **not** an editorial or current-rule approval.

| Model package | Unique scenarios | Preserved graph nodes | Source-backed extended candidate records | Donor says no additional method | No scenario-specific extended routing |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2ЭС5К/3ЭС5К Ермак | 136 | 2,535 | 0 | 0 | 136 |
| ЧМЭ3/Т/Э | 68 | 898 | 54 | 14 | 0 |
| ТЭМ2/У | 33 canonical projections of 24 original scenarios | 151 | 31 projections of 22 originals | 2 | 0 |
| ВЛ80С | 103 | 318 questions | 0 in the shared extended donor | 0 | 103 |

The original 2,535 + 898 + 151 graph nodes and 318 VL80S questions have no missing targets or unreachable nodes in this structural pass. That says nothing by itself about useful fault discrimination, safety, source currency, or which version should show a node. The previously counted 44 VL80S recommended and 59 `EXTENDED` pack entries are **103 separate original scenarios**, not 44 scenarios plus 59 extended branches. One VL80S pantograph scenario has a separately preserved framework-v2 module and reference pack; this is still one original route, not an authored version pair.

## Source and applicability findings

- All 68 CHME3 entries have a documentary source relation, but the relation explicitly means ID/title match only; none of their original graph objects carries a `sourceRefs` list. In the shared extended donor, 54 records exist (53 scoped to `chme3-base`, one to `chme3t-rheostatic`), while 14 routes explicitly report no additional method. Of the 54 candidate-bearing canonical entries, 53 include other variants whose separate extended applicability is not established by the base-profile record. Do not inherit these records to ЧМЭ3Т/Э.
- TEM2 has 24 original Stage-3 scenario identities and 33 variant-specific canonical entries. Its shared extended donor has 23 original records covering 22 original scenarios; the 31 canonical projections with candidate records must retain exact profiles. Eight ТЭМ2У-only entries have only a `tem2-base` extended record and therefore **no applicable candidate record**. Another 13 shared-variant entries have a base-only extended record. Two original routes explicitly report no additional method. A record ID match across projections does not prove TEM2U applicability.
- Ermak scenarios have 675 recorded source-reference links, including historical, profile-dependent and review-required labels in the preserved data; those labels must be evaluated per assertion. The separately known five undefined numbered source identities, `ER-SRC-039` ambiguity and the Stage-7 omission of `ER-DIAG-136` remain open. Only the last appears directly in this scenario-ID inventory; the others cannot be assigned to a scenario merely by title or broad source ownership.
- All 103 VL80S runtime scenarios carry a donor `sourceNote`, but the runtime source does not provide two independently authored route versions or a scenario-specific extended branch. The 59 `EXTENDED` pack entries must not be paired by category or title with recommended entries.

## Review queue derived from the source records

| Evidence position | Scenario entries | Next source review |
| --- | ---: | --- |
| Extended candidate has an exact variant match | 11 | Check each claim and decide the two version-specific presentations. This is **not** publication or action approval. |
| Candidate covers only some variants in the same entry | 66 | Split applicability at the profile boundary before authoring the other variants. |
| Candidate profile is disjoint from the entry | 8 | Keep the ТЭМ2У projection unbound; look for its own source. |
| Donor explicitly found no additional method | 16 | Review whether independently evidenced extended knowledge exists; do not invent a method. |
| No scenario-specific extended source in the pinned shared donor | 239 | Locate and verify a source before writing an extended branch. |

These five classes partition all 340 entries. They are **evidence positions**, not a claim that the 11 matched entries are already safe or easy to publish. For a small first authoring trial, the separately preserved VL80S pantograph framework/reference pack and an exact-profile candidate entry are concrete material to inspect; the trial should establish how short and detailed versions differ before repeating it across models.

## What can be written next

Every scenario still needs an independently reviewed short and detailed route, with a separately authored extended branch for each version: **680 route versions and 680 extension positions**, not necessarily 680 new documents or 680 distinct source publications. A donor candidate record may provide evidence for more than one version, but the selection of nodes, explanations and applicability must be established per scenario and version. `DONOR_REPORTS_NO_ADDITIONAL_METHOD` is an explicit research result, not a procedure to fill in.

Before authoring a batch, review its graph against the source object and profile, trace individual claims to exact evidence, classify executable actions separately, then decide what belongs in short, detailed and warned extended views. Start with a small, source-rich slice and verify the route behavior before repeating the method. Keep the source gaps visible; do not publish a synthetic branch just to satisfy a count. This review does not change candidate publication or runtime imports, and no scenario text was generated by the inventory.
