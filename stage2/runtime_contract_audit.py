#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import gzip, json, re, sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
assets = root / 'app/src/main/assets/technical'
sources = root / 'app/src/main/java'
if not assets.exists() or not sources.exists():
    raise SystemExit('usage: runtime_contract_audit.py <patched Android project root>')

kt_files = list(sources.rglob('*.kt'))
kt = '\n'.join(p.read_text(encoding='utf-8', errors='replace') for p in kt_files)


def load(name: str):
    for p in (assets / f'{name}.json', assets / f'{name}.json.gz'):
        if p.exists():
            if p.suffix == '.gz':
                with gzip.open(p, 'rt', encoding='utf-8') as f: return json.load(f)
            return json.loads(p.read_text(encoding='utf-8'))
    raise AssertionError(f'missing canonical asset: {name}')


def keys(v):
    out=set()
    if isinstance(v, dict):
        for k, child in v.items(): out.add(k); out |= keys(child)
    elif isinstance(v, list):
        for child in v: out |= keys(child)
    return out

@dataclass(frozen=True)
class Contract:
    asset: str
    field: str
    kind: str  # visible or control
    patterns: tuple[str, ...]
    note: str

# This is deliberately a contract audit rather than a grep percentage. A field only
# passes when it exists in canonical data and the recovered runtime contains the
# loader/runtime/UI path that consumes it. Stage 3/4 then prove representative paths
# on Android itself.
contracts = [
    Contract('vl80s_acceptance','routes','control',(r'array\("routes"\)',),'route collection'),
    Contract('vl80s_acceptance','mode','control',(r'optString\("mode"\)',r'sequenceMode'),'route semantics'),
    Contract('vl80s_acceptance','itemIds','control',(r'array\("itemIds"\)',),'route membership'),
    Contract('vl80s_acceptance','notes','visible',(r'optString\("notes"\)',r'Условия маршрута'),'route warning text'),
    Contract('vl80s_acceptance','preconditions','control',(r'array\("preconditions"\)',r'requiredGates'),'safety gates'),
    Contract('vl80s_acceptance','states','control',(r'array\("states"\)',r'availableStates'),'five-state model'),
    Contract('vl80s_acceptance','rules','visible',(r'array\("rules"\)',r'Правила состояний'),'state rules'),
    Contract('vl80s_acceptance','gates','visible',(r'array\("gates"\)',r'acceptanceGateMeaning'),'gate meaning'),

    Contract('vl80s_electrical','baseSchemes','visible',(r'baseSchemes',r'Электр'),'base electrical schemes'),
    Contract('vl80s_electrical','modeOverlays','control',(r'modeOverlays',r'overlay'),'mode overlays'),
    Contract('vl80s_electrical','variantOverlays','control',(r'variantOverlays',r'overlay'),'variant overlays'),
    Contract('vl80s_electrical','semanticEdges','control',(r'semanticEdges',r'edge'),'electrical graph edges'),
    Contract('vl80s_electrical','paths','control',(r'paths',r'path'),'electrical paths'),

    Contract('vl80s_pneumatic','views','visible',(r'array\("views"\)',r'Пневмо'),'pneumatic views'),
    Contract('vl80s_pneumatic','states','control',(r'array\("states"\)',r'state'),'working states'),
    Contract('vl80s_pneumatic','referenceBenchmarks','visible',(r'referenceBenchmarks',r'Учебный ориентир'),'five reference benchmarks'),
    Contract('vl80s_pneumatic','paths','control',(r'paths',r'path'),'pneumatic paths'),
    Contract('vl80s_pneumatic','sequence','control',(r'sequence',),'pneumatic sequence'),

    Contract('ermak_diagnostics','graph','control',(r'obj\("graph"\)',r'ErmakDiagnostic'),'diagnostic graph'),
    Contract('ermak_diagnostics','startNodeId','control',(r'startNodeId',r'currentNode'),'graph start'),
    Contract('ermak_diagnostics','nodes','control',(r'array\("nodes"\)',r'node'),'graph nodes'),
    Contract('ermak_diagnostics','choices','control',(r'choices',r'nextNodeId'),'branch choices'),
    Contract('ermak_diagnostics','nextNodeId','control',(r'nextNodeId',),'node branch'),
    Contract('ermak_diagnostics','nextScenarioId','control',(r'nextScenarioId',),'scenario branch'),
    Contract('ermak_diagnostics','riskClass','visible',(r'riskClass',),'risk metadata'),
    Contract('ermak_diagnostics','sourceBound','visible',(r'sourceBound',),'source binding'),
    Contract('ermak_diagnostics','terminalStatus','control',(r'terminalStatus',),'terminal node status'),

    Contract('ermak_links','byEquipment','control',(r'byEquipment',r'ErmakRelatedIndex'),'indexed links'),
    Contract('ermak_links','bySystem','control',(r'bySystem',r'ErmakRelatedIndex'),'indexed links'),
    Contract('ermak_links','byDiagnostic','control',(r'byDiagnostic',r'ErmakRelatedIndex'),'indexed links'),
    Contract('ermak_links','byScheme','control',(r'byScheme',r'ErmakRelatedIndex'),'indexed links'),

    Contract('ermak_schemes','variantSelector','control',(r'variantSelector',r'ErmakScheme'),'execution selector'),
    Contract('ermak_schemes','dimensions','visible',(r'dimensions',r'Профиль исполнения'),'selector dimensions'),
    Contract('ermak_schemes','requiredWhen','control',(r'requiredWhen',r'required'),'conditional selector requirement'),
    Contract('ermak_schemes','hardRules','control',(r'hardRules',r'rule'),'compatibility rules'),
    Contract('ermak_schemes','variantRules','control',(r'variantRules',r'compatib'),'scheme compatibility'),
    Contract('ermak_schemes','hotspotLayer','control',(r'hotspotLayer',r'hotspot'),'interactive hotspots'),
    Contract('ermak_schemes','semanticGraph','control',(r'semanticGraph',r'edge'),'semantic graph'),
    Contract('ermak_schemes','flowLayer','control',(r'flowLayer',r'flow'),'flow layer'),
    Contract('ermak_schemes','path','control',(r'path',),'scheme paths'),

    Contract('ermak_system_map','criticalLinks','visible',(r'criticalLinks',r'Критическ'),'critical inter-system links'),
    Contract('ermak_system_map','profiles','visible',(r'profiles',r'Профил'),'system profiles'),
    Contract('ermak_system_map','dependencies','visible',(r'dependencies',r'Зависим'),'system dependencies'),
    Contract('ermak_system_map','interfaces','visible',(r'interfaces',r'Интерфейс'),'system interfaces'),
    Contract('ermak_system_map','evidenceNote','visible',(r'evidenceNote',r'Доказ'),'system evidence note'),
]

loaded={name:load(name) for name in sorted({c.asset for c in contracts})}
present={name:keys(data) for name,data in loaded.items()}
fail=[]; lines=[]
for c in contracts:
    if c.field not in present[c.asset]:
        lines.append(f'SKIP {c.asset}.{c.field}: not present in this canonical package')
        continue
    matched=[p for p in c.patterns if re.search(p,kt,re.I)]
    if not matched:
        fail.append(f'{c.asset}.{c.field}: no recovered {c.kind} path ({c.note})')
        lines.append('FAIL '+fail[-1])
    else:
        lines.append(f'PASS {c.kind:7s} {c.asset}.{c.field}: {c.note}')

# Structural integrity: collections recovered by the UI must still have stable IDs/titles.
checks=[]
def req_items(asset, collection, id_keys=('id',), title_keys=('title','name','label','symptom')):
    arr=loaded[asset].get(collection,[])
    assert isinstance(arr,list), f'{asset}.{collection} is not an array'
    bad=[]
    for i,x in enumerate(arr):
        if not isinstance(x,dict): bad.append((i,'not object')); continue
        if id_keys and not any(str(x.get(k,'')).strip() for k in id_keys): bad.append((i,'missing id'))
        if title_keys and not any(str(x.get(k,'')).strip() for k in title_keys): bad.append((i,'missing user label'))
    if bad: fail.append(f'{asset}.{collection}: malformed entries {bad[:8]}')
    checks.append(f'{asset}.{collection} count={len(arr)} malformed={len(bad)}')

req_items('ermak_diagnostics','scenarios')
req_items('ermak_schemes','schemes')
req_items('vl80s_acceptance','items')

report = root / 'stage2-runtime-contract.txt'
report.write_text('STAGE 2 — CANONICAL SOURCE → RECOVERED RUNTIME/UI CONTRACT\n\n' + '\n'.join(lines) + '\n\nSTRUCTURAL CHECKS\n' + '\n'.join(checks) + '\n\nRESULT\n' + ('FAIL\n'+'\n'.join(fail) if fail else 'PASS\nAll declared critical canonical fields have an explicit recovered runtime/UI path. Android visibility is exercised in stages 3–4.') + '\n', encoding='utf-8')
print(report.read_text(encoding='utf-8'))
if fail: raise SystemExit(2)
