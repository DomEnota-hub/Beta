# Beta 46: read-only audit before implementation

Audit date: 23 September 2026. Source tree: `dev14-integration` at
`a7837970ea26dd91e7bbf503df0eb1511c1d5b95`.

## Scope and method

This report records the read-only pass requested before mass fixes. The review covered the
Compose navigation graph, user-facing strings, repository/data boundaries, empty and loading
states, all declared colour palettes, the first-aid cards, and the acceptance datasets for
VL80S and Ermak. The current environment has no Android SDK, emulator or `adb`; consequently
layout findings in this pass are static and must still be checked on a real device after the
debug/release build. The hidden section, its content, and its access mechanism were not opened
or changed.

Priority: P0 — unsafe/breaks work; P1 — functional/navigation defect; P2 — UX/visual defect;
P3 — cosmetic.

## UI and architecture findings

| Screen | Problem | Cause | Priority | Proposed fix |
|---|---|---|---|---|
| Home | The common section is called “Справочник” and its subtitle also promises technical articles | Old information architecture | P1 | Rename to “База знаний”; describe only norms, safety and common materials |
| Knowledge list | General and locomotive-specific articles are searchable in one list | Search and categories use `allArticles`, including every `vl80-*` item and diagram detail | P1 | Expose only general articles in the Knowledge Base; keep direct lookup for Atlas deep links |
| Atlas → Safety | Identical occupational-safety cards appear separately for VL80S and Ermak | `loadSafety(family)` clones one common dataset under family-specific IDs | P1 | Move the common cards to the Knowledge Base and remove Safety from both Atlas section lists |
| Atlas → Ermak equipment / acceptance | Values such as `pneumatic_block`, `reservoir_group`, and `compressor_discharge_line` appear as locations | Generic JSON summary renders `zone`, `sectionScope`, and metadata directly | P1 | Use one exhaustive Russian location mapper; never fall back to a raw internal value |
| Acceptance | A single “Полная приёмка” is presented as the entry point | No mandatory/full distinction in the route model or UI | P1 | Add separate “Обязательная приёмка” and “Полный осмотр” routes |
| Ermak acceptance | Every one of 111 equipment records becomes a daily-looking checklist item | Checklist is generated mechanically from the Atlas, not from the operating manual | P0 | Build the mandatory route from RE7/TO-1; retain equipment-derived checks only in clearly labelled full inspection |
| Acceptance state | No explicit contract proves that mandatory items retain their state in full inspection | Routes are independent lists, although state is stored by item ID | P1 | Place the exact mandatory IDs at the start of full routes and add a repository/unit contract |
| Full acceptance start | Start point choice is hard-coded for any acceptance route | Clicking any route with a sequence opens the same “full acceptance” chooser | P1 | Show the chooser only for the full route; mandatory route opens directly |
| Knowledge empty search | The no-results message has no recovery action | Filters remain active and must be cleared separately | P2 | Add a reset action for query, category and favourites |
| Technical cards | Long subtitles and source text can make neighbouring cards uneven | Content-driven height, no truncation policy | P3 | Keep adaptive height; constrain only compact grid cards and preserve full text in details |
| All themes/palettes | Semantic error/warning cards use theme colours correctly, but runtime contrast is unverified | Static Compose review cannot measure the rendered device result | P2 | Verify every palette in the signed build on-device; capture any palette-specific defect |
| Navigation | Atlas deep links rely on global article lookup; filtering the Base naively would break them | Listing and direct lookup currently share one collection | P1 | Split “list/searchable general content” from “all content addressable by ID” |
| Loading/missing data | Technical detail has loading and not-found states; Knowledge list lacks an error boundary | Different screens implement states independently | P2 | Preserve current technical states and add a Knowledge empty state; CI runtime contracts cover data availability |

## First-aid content audit

Primary sources:

- Order of the Ministry of Health of Russia No. 220n of 3 May 2024, official publication:
  <https://publication.pravo.gov.ru/document/0001202405310015>
- Order of the Ministry of Health of Russia No. 262n of 24 May 2024, official publication:
  <https://publication.pravo.gov.ru/document/0001202405310074>
- Ministry of Health, “Алгоритмы оказания первой помощи”, 2024:
  <https://minzdrav.gov.ru/documents/9801-algoritmy-okazaniya-pervoy-pomoschi>
- Ministry of Health, “Первая помощь”, instructor manual, 2025:
  <https://static-0.minzdrav.gov.ru/system/attachments/attaches/000/080/129/original/Учебное_пособие_для_преподавателей.pdf>

| Existing card | Classification | Finding and correction |
|---|---|---|
| No consciousness | Current but incomplete | Add airway opening and breathing assessment for no more than 10 seconds |
| No breathing / CPR | Current but incomplete | Explicitly clear only obvious external obstructions, open the airway, assess breathing, prohibit blind finger sweeps, and avoid delaying CPR; retain 30:2, 5–6 cm and 100–120/min |
| Bleeding | Current | Preserve direct pressure → pressure dressing → tourniquet when required and time recording |
| Choking | Current but incomplete | Add checks after each back blow, pregnancy/marked obesity chest thrusts, unconscious transition to CPR, and removal only of a visible object |
| Trauma and fractures | Current | Preserve safe positioning, bleeding control and no forced reduction |
| Burns | Current but incomplete | Change cooling from “about” to at least 20 minutes and separate chemical exposure |
| Electric injury | Current | Preserve the railway electrical-safety boundary and CPR after safe isolation |
| Poisoning / chemistry | Requires clarification | Split poisoning from chemical skin/eye exposure so the algorithms are not conflated |
| Hypothermia | Current | Keep as a separate systemic condition and preserve gradual torso warming |
| Frostbite | Outdated in one step | Remove optional water rewarming from this worker card; use insulation, immobilisation, internal warming and medical help; prohibit rubbing and direct heat |
| Bites/stings | Current | Preserve urgent escalation for systemic signs |
| Acute stress reaction | Current | Preserve safety, calm communication and escalation for danger/disorientation |
| Seizure | Current | Preserve head protection, no restraint/no objects in mouth, recovery position after seizure when breathing |

Every card will show its source basis. Content that is not a substitute for training or emergency
dispatcher instructions remains explicitly labelled as such.

## Acceptance document audit

### VL80S

The operating manual’s depot acceptance section requires inspection and checks in the TO-1
scope and refers brake equipment to the applicable brake-maintenance instruction. TO-1 covers
the mechanical part, roof equipment viewed from the ground and pantograph, traction and
auxiliary machines, ventilation, electrical and pneumatic control, lighting/signalling, sand
equipment, transformer oil, condensate draining, instruments, water, tools/PPE/schemes,
wipers, pneumatic leakage, and brake equipment.

Source: “Электровоз ВЛ80С. Руководство по эксплуатации”, acceptance/TO-1:
<https://poezdvl.com/vl80c/vl80c_159.html>.

Decision: a short mandatory route will follow those documented TO-1 groups. The existing
66 detailed cards remain the full inspection; they are not all labelled mandatory for every
handover.

### 2ES5K / 3ES5K Ermak

RE7 requires TO-1 at acceptance. It lists tools/PPE/fire extinguishers/schemes, mechanical
equipment, lubricators, leakage, machines, ventilation, transformer oil, water, sand equipment,
wipers, pneumatic connections, condensate, roof/pantographs, lighting/signalling, MSUD and
traction/braking circuit checks, instruments/indicators, recording cassettes, and brake equipment.
RE8 describes TO-2 as specialist maintenance and does not justify treating the whole Atlas as a
daily mandatory route.

Source: `ИДМБ.661142.009РЭ7`, “Использование по назначению”, acceptance/TO-1:
<https://rcit.su/techinfoV57.html>.

Decision: the mandatory Ermak route will be authored from RE7/TO-1. The 111 Atlas-derived
equipment checks will remain available only as the full inspection, with an explicit statement
that this is an application reference route and not a confirmed normative daily sequence.

No “По условиям” route is added in this pass: the reviewed sources identify conditional work,
but a reliable actionable sequence requires the corresponding repair, storage, winter-operation,
or local document rather than inference from TO-1.

## Migration rule

- Knowledge Base: occupational safety, first aid, general brake/normative references, signals,
  PTE/IDP and other series-independent material.
- Atlas: equipment, systems, technical articles, electrical/pneumatic/interactive schemes and
  equipment-specific diagnostics for a selected locomotive family.
- Direct article lookup remains available for Atlas navigation, but locomotive articles are not
  listed or searched from the Knowledge Base.
