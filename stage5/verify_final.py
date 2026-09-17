#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import gzip,hashlib,json,os,sys,zipfile
apk=Path(sys.argv[1]); out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
sha=hashlib.sha256(apk.read_bytes()).hexdigest()
assets_expected={
'vl80s_acceptance':('items',66),'vl80s_diagnostics':('scenarios',93),'vl80s_electrical':('baseSchemes',8),
'vl80s_equipment':('records',89),'vl80s_pneumatic':('views',8),
'ermak_diagnostics':('scenarios',135),'ermak_equipment':('records',111),'ermak_knowledge':('articles',138),'ermak_schemes':('schemes',22)
}
manifest={'apk':apk.name,'sha256':sha,'github_sha':os.environ.get('GITHUB_SHA',''),'assets':{}}
with zipfile.ZipFile(apk) as z:
    names=set(z.namelist())
    technical=sorted(n for n in names if n.startswith('assets/technical/') and (n.endswith('.json') or n.endswith('.json.gz')))
    canonical_names=sorted({Path(n[:-3] if n.endswith('.gz') else n).name for n in technical})
    manifest['technical_asset_files']=technical
    manifest['canonical_asset_names']=canonical_names
    if len(canonical_names)!=14: raise SystemExit(f'expected 14 canonical technical assets, got {len(canonical_names)}: {canonical_names}')
    def load(base):
        for n in (f'assets/technical/{base}.json',f'assets/technical/{base}.json.gz'):
            if n in names:
                raw=z.read(n)
                if n.endswith('.gz'): raw=gzip.decompress(raw)
                return json.loads(raw.decode('utf-8')),hashlib.sha256(raw).hexdigest()
        raise SystemExit(f'missing {base}')
    for base,(collection,expected) in assets_expected.items():
        data,digest=load(base); actual=len(data.get(collection,[]))
        if actual!=expected: raise SystemExit(f'{base}.{collection}: expected {expected}, got {actual}')
        manifest['assets'][base]={'collection':collection,'count':actual,'json_sha256':digest}
    # Extra recovered contracts.
    p,_=load('vl80s_pneumatic'); manifest['assets']['vl80s_pneumatic']['referenceBenchmarks']=len(p.get('referenceBenchmarks',[]))
    if len(p.get('referenceBenchmarks',[]))!=5: raise SystemExit('expected 5 VL80 pneumatic referenceBenchmarks')
    s,_=load('ermak_system_map'); manifest['assets']['ermak_system_map']={'criticalLinks':len(s.get('criticalLinks',[]))}
    if len(s.get('criticalLinks',[]))!=16: raise SystemExit('expected 16 Ermak criticalLinks')
(out/'FINAL_MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(out/'SHA256SUMS.txt').write_text(f'{sha}  {apk.name}\n',encoding='utf-8')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
