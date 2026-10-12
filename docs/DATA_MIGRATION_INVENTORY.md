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

## Common migration checkpoint (2026-10-12)

- `FirstAidScreen.kt` blob `09587b2da7f23ac532755fd8aad4ced100d369fa`: 17 distinct first-aid topics + one worker-kit entity + two distinct SOURCE entities → 20 Common entries. Importer and pinned structural/negative validator: `qa/migrate_common_first_aid.py`, `qa/validate_common_first_aid.py`.
- `KnowledgeRepository.kt` blob `b37ead2d66c0c976bcc850f9cde4fddc0e198fb3` and `KnowledgeFirstWave.kt` blob `b12651f2e4dde65e0b5f50277c8928a97809afdd`: 48 unique article IDs → 26 KNOWLEDGE + 22 SAFETY; 19 distinct SOURCE entities. Importer/validator: `qa/migrate_common_knowledge.py`, `qa/validate_common_knowledge.py`. Eleven typed internal links resolve in the three-pack Common registry.
- These **87** entries are a source-mapped subset, not all Common source objects. All are unreviewed CANDIDATE/information-only with UNKNOWN source status/provenance; duplicate source descriptors were merged within this subset. The encrypted 329-question exam remains outside these packs, with hidden-access handling and object disposition open. `COMMON_INTERNAL` restricts links to Common→Common. CI on `7caea4394214348781e5925fdfec4bebd6b32617`: [38262930314](https://github.com/DomEnota-maker/Beta/actions/runs/38262930314) success.

## Ermak core asset mapping checkpoint (2026-10-12)

| Pinned donor source group | Observed source objects | Canonical output | Structural disposition |
|---|---:|---|---|
| `ermak_equipment.json.gz.records` | 111 | 111 EQUIPMENT | MIGRATED, exact nested object snapshot |
| `ermak_knowledge.json.gz.articles` | 138 | 138 KNOWLEDGE | MIGRATED, exact nested object snapshot |
| `ermak_diagnostics.json.gz.scenarios` | 136 | 136 DIAGNOSTIC_SCENARIO | MIGRATED, exact graph snapshot; 2535 nodes/2248 choices |
| `ermak_schemes.json.gz.schemes` | 22 | 22 ATLAS_SCHEME | MIGRATED, exact layers/metadata snapshot |
| `ermak_equipment.json.gz.sourceRegistry` | 99 keyed records / 97 source IDs | 99 SOURCE | MIGRATED by registry key; two colliding source IDs deliberately kept separate |
| Root metadata of the four assets above | four dictionaries excluding extracted arrays | `content-packs/electric/ermak/migration/source-audit.json` | MIGRATED as provenance/coverage metadata |
| `ermak_links.json.gz`, `ermak_system_map.json.gz` | 6 canonicalInputs and 15 systems, with further nested objects | None yet | PENDING_MAPPING, not accepted as migrated |

- Canonical Ermak pack entries: **506** in 27 packs. Complete source objects and source blob hashes are embedded per entry. Local importer comparison reproduces exact object arrays; CI verifies pinned pack hashes. **4731** typed same-model links resolve. All entries are `CANDIDATE` with UNKNOWN source/provenance and information-only action disposition; a future profile-specific gate must preserve original exclusions before publication.
- [Source audit](../content-packs/electric/ermak/migration/source-audit.json) lists each of **152** referenced source IDs and occurrence counts: 95 unambiguous (924 raw references, 922 distinct typed links), two collisions (6 references), 55 absent in the equipment registry (542 references). These 547 raw references do **not** have typed source targets. The collision `ER-SRC-039` identifies both an equipment TO-2 document and a pantograph training document; `ER-SRC-041` has two separately keyed records. No automatic equivalence asserted.
- Effective SHA `c4d18e85619156f9e4466facdd166e31f22efb52`. Remaining donor docs/Kotlin/generator/media objects need individual dispositions, and this checkpoint cannot count as full Ermak acceptance.

## CHME3 family core mapping checkpoint (2026-10-12)

| Execution | Catalog source records | Diagnostic source records | Canonical applicability |
|---|---:|---:|---|
| CHME3 | 306 | 55 | `chme3` only or exact shared group |
| CHME3T | 319 | 56 | `chme3t` only or exact shared group |
| CHME3E | 428 | 67 | `chme3e` only or exact shared group |

- Total **1231** source records from six pinned assets → **738** canonical entries; **493** exact variant copies `MERGED_WITH_CANONICAL`, **738** representative objects `MIGRATED`. Object-level mapping with donor variant, source index and Git blob SHA: [CHME3 source audit](../content-packs/diesel/chme3-family/migration/source-audit.json). 28 conflicting catalog IDs remain separate by execution; no inferred inheritance across variants. Catalog DIAGNOSTICS cards and executable graph sources are separate object kinds. 5421 typed same-variant links resolve; 610 raw source references remain unresolved (no target object in these six assets). Importer and validator: `qa/migrate_chme3.py`, `qa/validate_chme3.py`. [CI 38266192611](https://github.com/DomEnota-maker/Beta/actions/runs/38266192611) success on `affdc9befbfd532d2af9345fe2eddbebbe194467`.
- This is a six-asset coverage checkpoint. Donor docs/Kotlin/other technical assets and normative review remain unclassified or open. Every canonical entry is CANDIDATE/UNKNOWN/information-only.

## TEM2 / TEM2U core mapping checkpoint (2026-10-12)

| Execution/source | Catalog | Diagnostics | Scheme sources | Canonical applicability |
|---|---:|---:|---:|---|
| TEM2 | 122 | 22 | 8 shared-file sequences + 8 layouts | `tem2` |
| TEM2U | 131 | 24 | 9 shared-file sequences + 9 layouts | `tem2u` |

- **333** source objects from six pinned technical assets → **320** canonical entries in 17 packs. Thirteen byte-equivalent diagnostic copies merged; differing catalog records with equal source IDs remain separate. [TEM2 source audit](../content-packs/diesel/tem2-family/migration/source-audit.json) lists every source index/variant/blob and canonical ID; within these six assets, 1073 typed variant-safe links resolve and no target ID is missing. This does not close references in the remaining `docs/locomotives/diesel/tem2-family/` documents. Scheme coordinates are training geometry, not a precise mounting plan. Importer/validator: `qa/migrate_tem2.py`, `qa/validate_tem2.py`.
- Current imported Common + three model-block subset: **85** packs, **1651** canonical entries and **11,302** typed links; cross-block gate `qa/validate_migrated_data_array.py` checks them together. VL80S remains under its existing separate migration checks, and the full donor object ledger still needs final dispositions. All new TEM2 items remain CANDIDATE/UNKNOWN/information-only.

The complete [discovery ledger](data-migration/source-discovery-ledger.json) preserves all 837 preliminary file/group rows. Its PENDING and mirror statuses have not been replaced by final object dispositions; exact per-object mappings for the four migrated subsets are held in their source audits and pinned importers. [CI 38292680525](https://github.com/DomEnota-maker/Beta/actions/runs/38292680525) passed on `bdf3fe12315ca014855f7fc4ba4e841fca4a71ae` after the TEM2 reference-type fix.
