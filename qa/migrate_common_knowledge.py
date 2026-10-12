#!/usr/bin/env python3
"""Preserve donor Common articles without promoting their claimed source status."""
import argparse
import hashlib
import json
import re
from pathlib import Path

from migrate_common_first_aid import matched, strings

PINS={
    "KnowledgeRepository.kt":"b37ead2d66c0c976bcc850f9cde4fddc0e198fb3",
    "KnowledgeFirstWave.kt":"b12651f2e4dde65e0b5f50277c8928a97809afdd",
}
BASE="app/src/main/java/ru/railbrake/calculator/core/"

def pin(name,src):
    b=src.encode()
    actual=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if actual!=PINS[name]:raise ValueError(f"unpinned {name}: {actual}")

def split_args(body):
    pieces=[];start=0;depth=0;quoted=False;escaped=False
    for i,c in enumerate(body):
        if quoted:
            if escaped:escaped=False
            elif c=="\\":escaped=True
            elif c=='"':quoted=False
        elif c=='"':quoted=True
        elif c=='(':depth+=1
        elif c==')':depth-=1
        elif c==',' and depth==0:
            pieces.append(body[start:i].strip());start=i+1
    pieces.append(body[start:].strip())
    return [x for x in pieces if x]

def named(body):
    return {k.strip():v.strip() for k,v in (p.split("=",1) for p in split_args(body))}

def string(expr):
    values=strings(expr)
    if len(values)!=1 or not expr.strip().startswith('"'):
        raise ValueError(f"expected one static Kotlin string: {expr[:100]}")
    if '$' in values[0]:raise ValueError("dynamic source string")
    return values[0]

def source_value(expr,vars):
    if expr in vars:return vars[expr]
    if not expr.startswith("KnowledgeSource("):raise ValueError(f"unknown source {expr[:70]}")
    raw,_=matched(expr,expr.index('('))
    if raw.lstrip().startswith('"'):
        pieces=split_args(raw)
        return (string(pieces[0]),string(pieces[1]) if len(pieces)>1 else None,None)
    f=named(raw)
    return (string(f["title"]),string(f["note"]) if "note" in f else None,
            string(f["externalUrl"]) if "externalUrl" in f else None)

def source_vars(s):
    result={}
    for m in re.finditer(r'(?:private )?val (\w+) = KnowledgeSource\(',s):
        raw,_=matched(s,m.end()-1)
        result[m.group(1)]=source_value("KnowledgeSource("+raw+")",{})
    return result

def common_explicit(s):
    vars=source_vars(s)
    result=[]
    for m in re.finditer(r'\bKnowledgeArticle\s*\(',s):
        raw,_=matched(s,m.end()-1)
        try:f=named(raw)
        except ValueError:continue
        if "id" not in f:continue
        raw_ids=strings(f["id"])
        if not raw_ids or '$' in raw_ids[0]:continue
        id=string(f["id"])
        if id.startswith("vl80-") or id in {
            "bsa1","cab-equipment","alsn","phase-splitter","relay-panels","bsa2",
            "rectifier-left","transformer","rectifier-right","vvk1","vvk2","mv3","mv4","mk","burt"}:
            continue
        result.append(dict(id=id,title=string(f["title"]),category=string(f["category"]),
            status=string(f["status"]),summary=string(f["summary"]),body=strings(f["body"]),
            tags=strings(f["tags"]),source=source_value(f["source"],vars),
            related=strings(f.get("relatedArticleIds","")),
            path=BASE+"KnowledgeRepository.kt"))
    if len(result)!=21:raise ValueError(f"expected 21 explicit Common articles, got {len(result)}")
    return result

def common_first_wave(s):
    vars=source_vars(s);result=[]
    for m in re.finditer(r'\barticle\s*\(',s):
        raw,_=matched(s,m.end()-1)
        p=split_args(raw)
        if not p or not p[0].startswith('"'):continue
        if len(p)!=7:raise ValueError(f"article positional fields {len(p)}")
        result.append(dict(id=string(p[0]),title=string(p[1]),category=string(p[2]),
            status="Проверено 25.09.2026",summary=string(p[3]),body=strings(p[4]),
            tags=strings(p[5]),source=source_value(p[6],vars),related=[],
            path=BASE+"KnowledgeFirstWave.kt"))
    if len(result)!=27:raise ValueError(f"expected 27 first-wave Common articles, got {len(result)}")
    return result

def make(sources):
    for name,s in sources.items():pin(name,s)
    articles=common_explicit(sources["KnowledgeRepository.kt"])+common_first_wave(sources["KnowledgeFirstWave.kt"])
    if len({a["id"] for a in articles})!=48:raise ValueError("duplicate source article ID")
    by_id={a["id"]:a for a in articles}
    source_ids={}
    sources_out={}
    for a in articles:
        tup=a["source"]
        sid=source_ids.setdefault(tup,"common.source.knowledge-"+hashlib.sha256(
            json.dumps(tup,ensure_ascii=False).encode()).hexdigest()[:16])
        if sid in sources_out and sources_out[sid]!=tup:raise ValueError("source hash collision")
        sources_out[sid]=tup
    entries={"knowledge":[],"safety":[]}
    for a in articles:
        kind="safety" if a["id"].startswith("safety-") else "knowledge"
        cid=f"common.{kind}.{a['id']}"
        related=[]
        for raw in a["related"]:
            target=by_id.get(raw)
            if target is None:raise ValueError(f"unresolved Common relation {a['id']} -> {raw}")
            target_kind="safety" if raw.startswith("safety-") else "knowledge"
            related.append({"type":target_kind.upper(),"targetId":f"common.{target_kind}.{raw}",
                "scope":"COMMON_INTERNAL"})
        source_id=source_ids[a["source"]]
        entries[kind].append({
            "id":cid,"type":kind.upper(),"owner":{"kind":"COMMON"},
            "layer":"STANDARD","publicationStatus":"CANDIDATE",
            "provenance":"UNKNOWN","sourceStatus":"UNKNOWN","actionDisposition":"INFORMATION_ONLY",
            "title":a["title"],"summary":a["summary"],"details":a["body"],
            "blocks":[{"title":"Категория исходного материала","lines":[a["category"]]},
                      {"title":"Статус в доноре — не проверка текущей редакции","lines":[a["status"]]},
                      {"title":"Исходный ID и файл","lines":[a["id"],a["path"],PINS[Path(a["path"]).name]]}],
            "searchTerms":a["tags"],"sourceRefs":[source_id],
            "links":[{"type":"SOURCE","targetId":source_id,"scope":"COMMON_INTERNAL"}]+related
        })
    for sid,(title,note,url) in sorted(sources_out.items()):
        entries["knowledge"].append({
            "id":sid,"type":"SOURCE","owner":{"kind":"COMMON"},
            "publicationStatus":"CANDIDATE","provenance":"UNKNOWN","sourceStatus":"UNKNOWN",
            "actionDisposition":"INFORMATION_ONLY","title":title,
            "summary":note or "Источник указан в доноре; актуальность не подтверждена.",
            "details":([note] if note else [])+([url] if url else [])+
                ["Donor: DomEnota-maker/Test- @ 3176d6ee228f0ed4b78371f45209e10c1c724eff"],
            "sourceRefs":[],"links":[]
        })
    packs={}
    for kind,items in entries.items():
        packs[kind]={"manifest":{"schemaVersion":1,"packId":f"common.{kind}.articles-001",
            "packVersion":"0.1.0","family":None,"modelIds":[],"variantIds":[],
            "locale":"ru-RU","entries":[e["id"] for e in items],"requiresRuntime":"1.1.0",
            "sourceCatalogVersion":"test-3176d6ee-knowledge",
            "checksums":{"KnowledgeRepository.gitBlob":PINS["KnowledgeRepository.kt"],
                         "KnowledgeFirstWave.gitBlob":PINS["KnowledgeFirstWave.kt"]}},
            "entries":items}
    return packs

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("source_dir",type=Path)
    parser.add_argument("output_dir",type=Path)
    args=parser.parse_args()
    src={name:(args.source_dir/name).read_text() for name in PINS}
    packs=make(src)
    for kind,pack in packs.items():
        path=args.output_dir/f"{kind}.pack.json"
        path.parent.mkdir(parents=True,exist_ok=True)
        content=json.dumps(pack,ensure_ascii=False,indent=2)+"\n"
        path.write_text(content)
        print(kind,len(pack["entries"]),hashlib.sha256(content.encode()).hexdigest())

if __name__=="__main__":main()
