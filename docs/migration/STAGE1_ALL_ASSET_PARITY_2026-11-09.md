# Stage 1/15: pinned donor source accounting and remaining semantic gaps (2026-11-09)

**Status: IN_PROGRESS.** This is a reproducible source-preservation audit, **not** a functional migration sign-off. The read-only donor is `DomEnota-hub/Test-` at `3176d6ee228f0ed4b78371f45209e10c1c724eff`. All changes are on the Beta audit branch.

## Asset-by-asset evidence

The `docs/migration/donor-asset-crosswalk.json` ledger covers **36/36** pinned donor assets by Git blob SHA and byte length. Every row now has a precise evidence disposition, with a green workflow for the reported scope. **35/36** have non-runtime candidate/source-index parity evidence; the final encrypted exam asset is decoded and audited but **has no target question pack**.

| Source group | Assets | CI-backed evidence | Explicit limitation |
|---|---:|---|---|
| VL80S | 9 | [VL80S pinned parity #42676198913](https://github.com/DomEnota-hub/Beta/actions/runs/42676198913): 8 full preserved source JSONs; equipment root context + 89 stable IDs; 66 acceptance IDs; 103 diagnostic IDs; 9 physical buckets; 1,181 diagnostic edges | Equipment field-by-field projection, runtime action authority and actual execution profile still need separate checks |
| TEM2/TEM2U | 6 | [TEM2 source parity #42666239232](https://github.com/DomEnota-hub/Beta/actions/runs/42666239232): 333 source occurrences → 320 canonical candidate objects; zero object mismatches; 1,073 internal links | All candidate/information-only; source authority and device behavior unverified |
| CHME3/T/E | 6 | [CHME3 source parity #42667717204](https://github.com/DomEnota-hub/Beta/actions/runs/42667717204): 1,231 source occurrences → 738 canonical candidates | **610 unresolved references** remain quarantined |
| Ermak | 6 | [Ermak source parity #42667848154](https://github.com/DomEnota-hub/Beta/actions/runs/42667848154): 506 canonical objects from four source arrays; [shared/index audit #42676625079](https://github.com/DomEnota-hub/Beta/actions/runs/42676625079): two pinned supplemental index blobs and 523 reciprocal diagnostic/scheme pairs | **542 SOURCE_GAP occurrences, 6 ambiguous source-ID occurrences**, 1 missing diagnostic index ID (`ER-DIAG-136`), 5 missing source IDs, 2 reused raw source IDs; none auto-resolved |
| Shared | 8 JSON | [Shared pinned source parity #42676538231](https://github.com/DomEnota-hub/Beta/actions/runs/42676538231): 4 complete source JSON candidate snapshots and 4 split-object candidate projections; scheme palette and viewport contract preserved as non-runtime UI contracts | Source presentation identity, emergency authorization, scheme applicability and current normative authority remain unverified |
| Exam | 1 encoded | [Exam audit #42676935679](https://github.com/DomEnota-hub/Beta/actions/runs/42676935679): pinned Kotlin decoder and encrypted asset, 329 unique questions, **0 missing diagnostic/equipment reference IDs** against pinned VL80S candidate mappings; 3/3 negative/positive tests | No decrypted question text committed; **no Beta question pack or UI integration**. CI artifact contains only aggregate metadata |

The source crosswalk statuses deliberately distinguish:
- `SOURCE_ARRAY_EQUIVALENT_CANDIDATE`: original array objects match preserved candidate objects, without publication authority.
- `SOURCE_OBJECT_EQUIVALENT_CANDIDATE`: complete original source JSON preserved and checked against pinned donor.
- `SOURCE_CONTEXT_AND_ID_EQUIVALENT_CANDIDATE`: VL80S equipment non-record root plus 89 stable IDs, **not** full field-by-field equality.
- `SOURCE_SPLIT_OBJECT_EQUIVALENT_CANDIDATE`: source records and metadata split across non-runtime candidate inventories.
- `SOURCE_INDEX_RECONCILED_CANDIDATE`: exact Ermak source index blobs and mapped candidate IDs with unresolved links retained.
- `SOURCE_DECODED_AUDITED_NO_TARGET`: encrypted exam questions decoded only in CI memory, without any target migration.

## New validation implementation

- `qa/validate_vl80s_source_parity.py`, `qa/test_vl80s_source_parity.py`, `.github/workflows/vl80s-source-parity.yml`.
- `qa/validate_shared_pinned_source_parity.py`, `.github/workflows/shared-source-parity.yml`.
- `content-packs/locomotive-migration/interactive-scheme-ui-contracts.candidate.json`: exact donor palette/viewport contract data, **not imported by runtime**.
- `qa/audit_exam_source.py`, `qa/test_exam_source.py`, `.github/workflows/exam-source-audit.yml`: encrypted exam audit without exporting plaintext or decoder key.
- `qa/validate_donor_asset_crosswalk.py` enforces separate evidence-backed status values and retains `runtimePublication=NOT_PROVEN` for all 36 assets.

## Unresolved gates before stage 1 can close

1. Reconcile **610 CHME3** unresolved links against confirmed sources, or explicitly record each as quarantined with a verified non-executable fallback.
2. Resolve or quarantine **Ermak** source-ID gaps and collisions and missing `ER-DIAG-136` index mapping. Do not infer from matching titles.
3. Determine authorized source and applicability of 329 exam questions; migrate them to a non-runtime Beta candidate pack with stable IDs and provenance before wiring any user-facing feature.
4. Audit Kotlin-only feature and local-state parity, not merely JSON assets; map each donor feature to a Beta module, test and implementation state.
5. Separate candidate content preservation from confirmed operational applicability and current safety/normative approval. Unknown variants must remain fail-closed.
6. Complete CI on the final branch HEAD; do not mark this stage complete based on green runs from earlier commits.

**Next concrete operation:** build a Kotlin feature-to-module crosswalk and identify missing runtime wiring, then address the CHME3/Ermak unresolved source-link ledgers in bounded verified batches. Only after source and Kotlin reconciliation should stage 2 start.

## Дополнение 10.11.2026: metadata-only индекс экзаменационного источника

`qa/audit_exam_source.py` дополнен генерацией **только идентификаторов и ссылок** 329 экзаменационных вопросов, без текста вопросов, ответов, ключа дешифрования, вариантов или подсказок. Новый CI-артефакт `exam-candidate-index-metadata-only` создаётся в `$RUNNER_TEMP`, не публикуется в Android APK и автоматически удаляется по retention (14 дней). Включены идентификаторы, ссылки на диагностические сценарии/оборудование и булево поле изображения. Содержимое проверяется по pinned donor asset SHA, исходному decoder SHA, хешу набора ID и проверке ссылок на сохранённые VL80S-кандидаты.

Индекс имеет `status=METADATA_ONLY_CANDIDATE_NOT_QUESTION_PACK`, `runtimeImport=false`, `sourceRightsVerified=false`, `crewActionAuthorized=false`. Это **не перенос текста экзаменационных вопросов**, не лицензирование, не публикация и не функциональный экран. Добавлено 6 регрессионных тестов (в том числе попытки утечки текста через ID/ссылку, дубликаты, неверные типы и неизвестные связи). До подтверждения прав исходные тексты не переносить.

**CI-статус нового изменения: PENDING до терминальной проверки финального HEAD.**
