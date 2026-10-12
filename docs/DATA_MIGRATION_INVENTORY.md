# Data migration source inventory — discovery checkpoint

Pinned donor: `DomEnota-maker/Test-` @ `3176d6ee228f0ed4b78371f45209e10c1c724eff`. Destination: `DomEnota-maker/Beta:modular-rebuild`. All hashes below are Git **blob SHA-1**, not SHA-256 of uncompressed content. Source counts are top-level array lengths; nested objects/fields remain inside those objects and are **not** counted as migrated.

## Coverage and status

- Donor tree: **738 blobs**. Discovery ledger covers all 738 paths and additionally three inspected ZIP members; 837 rows because a file can contain several arrays.
- 169 `patch/app` paths have the exact same blob SHA as `app/` and are tagged duplicate source mirrors, not independent content. The donor README says CI starts from `RailBrakeCalculator.zip` and overlays `patch/`; root `app/` is a mirror, not the standalone assembled build.
- This is an **intermediate source inventory**. `PENDING_MAPPING`, `PENDING_EXTRACTION` and `DUPLICATE_SOURCE_MIRROR` are discovery-only statuses, not final migration dispositions. They must be replaced by exactly one of the six dispositions from the addendum for each object before final acceptance. No source was declared migrated solely from file presence.
- `exam_questions.json` is an AES/CBC encoded payload; the pinned `ExamPayloadCodec` decoded it read-only to **329 unique IDs** in blocks 164/29/72/64. Individual question ownership, access policy and links still need review. The ZIP contains 60 files; its HistoryRepository and the two raster scheme sources are called out, and the rest require member-by-member comparison.
- Source-derived Kotlin, generator scripts (`.github/scripts/`, `qa/`, `tools/`), source documents, binary media and the assembled ZIP remain in scope. Their individual object counts are open, rather than silently excluded.

## Primary technical assets (read-only donor)

| Owner guess | Source file | Blob SHA | Observed top-level arrays |
|---|---|---|---|
| chme3-family | `app/src/main/assets/technical/chme3_chme3_catalog.json.gz` | `fa63f0ca6bf4` | entries: 306 |
| chme3-family | `app/src/main/assets/technical/chme3_chme3_diagnostics.json.gz` | `6a6068ad1ea5` | scenarios: 55 |
| chme3-family | `app/src/main/assets/technical/chme3_chme3e_catalog.json.gz` | `095e3230dd40` | entries: 428 |
| chme3-family | `app/src/main/assets/technical/chme3_chme3e_diagnostics.json.gz` | `1ab9ae40bc90` | scenarios: 67 |
| chme3-family | `app/src/main/assets/technical/chme3_chme3t_catalog.json.gz` | `3682ce0b3a86` | entries: 319 |
| chme3-family | `app/src/main/assets/technical/chme3_chme3t_diagnostics.json.gz` | `41809c646411` | scenarios: 56 |
| mixed (requires per-object review) | `app/src/main/assets/technical/diagnostic_framework_v2.json` | `ab2ecd3f5825` | modules: 1 |
| ermak | `app/src/main/assets/technical/ermak_diagnostics.json.gz` | `c3a22c62db42` | categoryOrder: 14, navigationModes: 6, scenarios: 136 |
| ermak | `app/src/main/assets/technical/ermak_equipment.json.gz` | `47a8d2424d69` | openWork: 4, records: 111 |
| ermak | `app/src/main/assets/technical/ermak_knowledge.json.gz` | `08d164fc11c3` | articles: 138 |
| ermak | `app/src/main/assets/technical/ermak_links.json.gz` | `432eb86db028` | canonicalInputs: 6, explicitNonBlockingGaps: 1 |
| ermak | `app/src/main/assets/technical/ermak_schemes.json.gz` | `33b1f6016308` | principles: 5, schemes: 22 |
| ermak | `app/src/main/assets/technical/ermak_system_map.json.gz` | `bd1746833226` | criticalLinks: 16, evidenceLevels: 4, openQuestions: 7, sourceIds: 13, systems: 15 |
| mixed (requires per-object review) | `app/src/main/assets/technical/extended_emergency_policy.json` | `60f132caa036` | actionDispositions: 3, provenanceClasses: 4, requiredScenarioMetadata: 7 |
| mixed (requires per-object review) | `app/src/main/assets/technical/extended_emergency_runtime.json` | `24e5415a4d4e` | records: 77, scenarioRouting: 92 |
| mixed (requires per-object review) | `app/src/main/assets/technical/scheme_layout_metadata.json` | `ad34505c73ea` | layouts: 55 |
| mixed (requires per-object review) | `app/src/main/assets/technical/scheme_semantic_palette.json` | `14db2ce63a85` | flowTokens: 19 |
| mixed (requires per-object review) | `app/src/main/assets/technical/scheme_view_contract.json` | `15789a897e07` | $: 1 |
| mixed (requires per-object review) | `app/src/main/assets/technical/source_presentations.json` | `6dde42099f5c` | $: 1 |
| mixed (requires per-object review) | `app/src/main/assets/technical/stepwise_scheme_flows.json` | `ccda6a1384f3` | researchGaps: 3, sequences: 55 |
| tem2-family | `app/src/main/assets/technical/tem2_scheme_layout_metadata.json` | `10b70f964401` | layouts: 17 |
| tem2-family | `app/src/main/assets/technical/tem2_stepwise_scheme_flows.json` | `526e7301e090` | sequences: 17 |
| tem2-family | `app/src/main/assets/technical/tem2_tem2_catalog.json` | `c7a94c1cd268` | entries: 122 |
| tem2-family | `app/src/main/assets/technical/tem2_tem2_diagnostics.json` | `93b3e9b79ab5` | scenarios: 22 |
| tem2-family | `app/src/main/assets/technical/tem2_tem2u_catalog.json` | `766ac526fa4b` | entries: 131 |
| tem2-family | `app/src/main/assets/technical/tem2_tem2u_diagnostics.json` | `360ced5392b4` | scenarios: 24 |
| vl80s | `app/src/main/assets/technical/vl80s_acceptance.json.gz` | `5174e8fa343b` | designPrinciples: 6, gates: 3, items: 66, routes: 7, zones: 9 |
| vl80s | `app/src/main/assets/technical/vl80s_diagnostics.json.gz` | `6ffdfdabf2f4` | acceptanceHintCorrections: 7, edges: 1181, integrationExceptions: 2, scenarios: 103 |
| vl80s | `app/src/main/assets/technical/vl80s_electrical.json.gz` | `6891068a9aeb` | baseSchemes: 8, candidateVariantFragments: 2, modeOverlays: 8, schemeIndex: 8, variantOverlays: 8 |
| vl80s | `app/src/main/assets/technical/vl80s_electrical_variants.json.gz` | `f9f7956f871c` | candidateVariantFragments: 2, renderPolicy: 6, variantOverlays: 8 |
| vl80s | `app/src/main/assets/technical/vl80s_equipment.json.gz` | `a6d00459e18c` | records: 89, zones: 3 |
| vl80s | `app/src/main/assets/technical/vl80s_pantograph_reference_pack.json` | `2256a734d3cd` | conflictGroups: 3, entries: 19, sourceRegistry: 12, variantIds: 1 |
| vl80s | `app/src/main/assets/technical/vl80s_pneumatic.json.gz` | `6adafce63074` | referenceBenchmarks: 5, states: 13, views: 8 |
| vl80s | `app/src/main/assets/technical/vl80s_pneumatic_variants.json.gz` | `3899e9e653f1` | stateApplicability: 13 |
| vl80s | `app/src/main/assets/technical/vl80s_variants.json.gz` | `9a35df3df981` | experimentalOverrides: 4, nonMergeRules: 6, physicalBuckets: 9, sourceReferenceTags: 1 |

## Source model documents

The following source JSON files are separate object groups, some of which may duplicate the assembled technical assets. Every file is pinned by its full Git blob SHA in the donor commit. Counts are observations, not a sum of unique entities.

| Owner guess | Source path | Groups (top-level) |
|---|---|---|
| chme3-family | `docs/locomotives/chme3/acceptance_contract_pass4.json` | profileRules: 3, routes: 7, sourceRefs: 3 |
| chme3-family | `docs/locomotives/chme3/acceptance_required_pass4.json` | items: 21 |
| chme3-family | `docs/locomotives/chme3/acceptance_source_registry_addendum.json` | sources: 4 |
| chme3-family | `docs/locomotives/chme3/atlas_cards_electric_brake.json` | records: 14 |
| chme3-family | `docs/locomotives/chme3/atlas_cards_engine_control_remaining.json` | records: 18 |
| chme3-family | `docs/locomotives/chme3/atlas_cards_powerplant.json` | records: 11 |
| chme3-family | `docs/locomotives/chme3/atlas_cards_running_auxiliary.json` | records: 18 |
| chme3-family | `docs/locomotives/chme3/atlas_cards_scheme_equipment.json` | equipment: 9 |
| chme3-family | `docs/locomotives/chme3/atlas_id_contract.json` | canonicalMappings: 11, notes: 3, reservedEquipmentIds: 11 |
| chme3-family | `docs/locomotives/chme3/atlas_index.json` | equipment: 60, sourceRefs: 2, systems: 13 |
| chme3-family | `docs/locomotives/chme3/atlas_index_extension.json` | equipment: 10, evidenceRefs: 4 |
| chme3-family | `docs/locomotives/chme3/atlas_scheme_designations.json` | variantNotes: 3 |
| chme3-family | `docs/locomotives/chme3/atlas_schemes_extension.json` | records: 2 |
| chme3-family | `docs/locomotives/chme3/atlas_schemes_functional.json` | records: 10 |
| chme3-family | `docs/locomotives/chme3/diagnostic_field_observations.json` | observations: 10 |
| chme3-family | `docs/locomotives/chme3/diagnostic_research_sources_2026.json` | records: 4 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch1.json` | scenarios: 6 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch2.json` | scenarios: 6 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch3.json` | scenarios: 6 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch4.json` | scenarios: 4 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch5.json` | scenarios: 8 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch6.json` | scenarios: 6 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch7.json` | scenarios: 7 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch8.json` | scenarios: 7 |
| chme3-family | `docs/locomotives/chme3/diagnostic_runtime_graphs_v2_batch9.json` | scenarios: 6 |
| chme3-family | `docs/locomotives/chme3/diagnostic_search_vocabulary_addendum.json` | asrCandidates: 5, regressionPairs: 5, terms: 12 |
| chme3-family | `docs/locomotives/chme3/diagnostic_source_matrix.json` | coverageClusters: 11, fieldMaterialCandidates: 2, sourceLayers: 4 |
| chme3-family | `docs/locomotives/chme3/diagnostic_source_registry_addendum.json` | sources: 10 |
| chme3-family | `docs/locomotives/chme3/diagnostics_996r_detail_pass3.json` | scenarios: 6 |
| chme3-family | `docs/locomotives/chme3/diagnostics_brake_aux_pass3.json` | scenarios: 8 |
| chme3-family | `docs/locomotives/chme3/diagnostics_electrical_control_pass3.json` | scenarios: 10 |
| chme3-family | `docs/locomotives/chme3/diagnostics_extended_pass3.json` | scenarios: 20 |
| chme3-family | `docs/locomotives/chme3/diagnostics_powerplant_pass3.json` | scenarios: 12 |
| chme3-family | `docs/locomotives/chme3/profiles.json` | profileDimensions: 3, profiles: 3 |
| chme3-family | `docs/locomotives/chme3/search_vocabulary.json` | componentCandidates: 17, generalConversationalPatternsAlreadySupported: 14, seriesAliases: 3, sources: 3 |
| chme3-family | `docs/locomotives/chme3/search_vocabulary_diagnostics_996r_pass3.json` | negativeDisambiguation: 2, rules: 12 |
| chme3-family | `docs/locomotives/chme3/search_vocabulary_diagnostics_extended_pass3.json` | negativeDisambiguation: 4, rules: 37 |
| chme3-family | `docs/locomotives/chme3/search_vocabulary_diagnostics_pass3.json` | negativeDisambiguation: 4, rules: 38 |
| chme3-family | `docs/locomotives/chme3/source_registry.json` | sources: 12, statusVocabulary: 9 |
| chme3-family | `docs/locomotives/chme3/source_registry_addendum_atlas.json` | sources: 4 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3/interactive_schemes.json` | profileViews: 2, sharedViewRefs: 9 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/acceptance_stage4.json` | profileExtendedChecks: 4 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/assistant_semantics_stage3.json` | entities: 12, normalization: 8, oppositeEventPairs: 8, profileMismatchRules: 1, scenarioRouting: 12, spokenCorpus: 12 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/atlas_cards_electronic.json` | records: 24 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/atlas_cards_preheat_remote.json` | records: 9 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/atlas_variant.json` | equipment: 33, systems: 3 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/diagnostic_runtime_graphs_v2.json` | scenarios: 12 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/diagnostics_stage3.json` | scenarios: 12 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/inheritance.json` | explicitVariantOverrides: 6, hardExclusions: 5 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/interactive_schemes.json` | explicitExclusions: 4, profileViews: 6, sharedViewRefs: 9 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/profile.json` | completedStages: 5, confirmedFamilyTraits: 4, evidenceRefs: 4, explicitExclusions: 5, nextStages: 1, variantTraits: 3 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/scheme_designations.json` | electrical: 29, evidenceRefs: 3 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/schemes_variant.json` | records: 6 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/source_registry.json` | researchGaps: 4, sources: 4 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3e/source_registry_stage2.json` | sources: 5 |
| chme3-family | `docs/locomotives/diesel/chme3-family/chme3t/interactive_schemes.json` | profileViews: 1, sharedViewRefs: 9 |
| chme3-family | `docs/locomotives/diesel/chme3-family/common/acceptance_stage4_manifest.json` | profiles: 3 |
| chme3-family | `docs/locomotives/diesel/chme3-family/common/diagnostics_manifest.json` | $: 1 |
| chme3-family | `docs/locomotives/diesel/chme3-family/common/interactive_scheme_contract.json` | $: 1 |
| chme3-family | `docs/locomotives/diesel/chme3-family/common/interactive_shared_views.json` | views: 9 |
| chme3-family | `docs/locomotives/diesel/chme3-family/family_manifest.json` | profiles: 3 |
| tem2-family | `docs/locomotives/diesel/tem2-family/common/profile_contract.json` | familyRules: 5, profileDimensions: 6 |
| tem2-family | `docs/locomotives/diesel/tem2-family/common/source_registry.json` | researchGaps: 5, sources: 9 |
| tem2-family | `docs/locomotives/diesel/tem2-family/common/stage2_model.json` | equipment: 36, flows: 11, profiles: 2, schemes: 9, systems: 9 |
| tem2-family | `docs/locomotives/diesel/tem2-family/common/stage3_model.json` | foundationEvidenceRefs: 6, researchEvidence: 3, scenarios: 24 |
| tem2-family | `docs/locomotives/diesel/tem2-family/common/stage4_acceptance.json` | coreChecks: 14, profileChecks: 2, profiles: 2, routes: 2 |
| tem2-family | `docs/locomotives/diesel/tem2-family/family_manifest.json` | profiles: 2 |
| tem2-family | `docs/locomotives/diesel/tem2-family/tem2/profile.json` | completedStages: 1, confirmedFamilyTraits: 5, evidenceRefs: 6, executionDependentTraits: 5, explicitExclusions: 5, nextStages: 3 |
| tem2-family | `docs/locomotives/diesel/tem2-family/tem2u/profile.json` | completedStages: 1, confirmedFamilyTraits: 5, evidenceRefs: 4, explicitExclusions: 5, nextStages: 3, variantTraits: 7 |
| mixed (requires per-object review) | `docs/locomotives/manifests/locomotive_families.json` | families: 2 |

## Embedded and functional sources

- `app/src/main/java/ru/railbrake/calculator/ui/FirstAidScreen.kt`: 17 explicit `FirstAidTopic` IDs. `hypothermia` and `frostbite` are distinct; ordered `whenToUse`, `actions`, `dont`, `note`, `source` and search vocabulary require preservation. Publication/current medical status has not been confirmed.
- `app/src/main/java/ru/railbrake/calculator/core/KnowledgeRepository.kt` contains general knowledge, safety and VL80S articles together, plus generated article constructions. Ownership must be decided per article, not per Kotlin file. `SafetyScreen.kt` is a view over that repository.
- Source-derived diagnostic repositories (`DiagnosticRepository`, `ErmakDiagnosticRepository`, `Chme3DiagnosticRepository`, `Tem2DiagnosticRepository`) and their deepening/unknown routing files can contain runtime material beyond catalog JSON. Their effective graphs need separate extraction; VL80S already has a pinned canonical runtime.
- `patch/app/src/main/java/ru/railbrake/calculator/core/BrakeCalculator.kt` is the compiled overlay source of calculation rules and tables. The root `app/` lacks that file. `RailBrakeCalculator.zip!/app/src/main/java/ru/railbrake/calculator/data/HistoryRepository.kt` is the available history source; no separate root/patch history file was found. Details belong in `CALCULATIONS_HISTORY_MIGRATION_CONTRACT.md`.
- `RailBrakeCalculator.zip` blob `6c3c7edc1713c1c901a566fd8a81a2494ee4ac58` includes original VL80S layout PNG and pneumatic JPEG; current Beta audit records exact recovered SHA-256 and geometry. Do not import them again.

## Resolution queue

1. Resolve objects and aliases against existing VL80S canonical packs before any repeat import; check source fingerprints and all nested fields.
2. Split Common general knowledge/first aid/safety from VL80S-specific articles, preserving source and publication gates. Audit the encoded exam asset decoder.
3. Check primary Ermak, CHME3-family and TEM2-family assets against source JSON/Kotlin generators; map variants per object and resolve conflicts explicitly.
4. Classify remaining scripts, source documents and ZIP members as unique source data or superseded/functional material with exact mapping. This discovery table is **not** a claim of full migration.
