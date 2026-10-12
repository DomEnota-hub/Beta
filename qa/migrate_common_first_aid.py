#!/usr/bin/env python3
"""Import pinned FirstAidTopic source without granting action/publication authority."""
import argparse
import hashlib
import json
import re
from pathlib import Path

PINNED_BLOB = "09587b2da7f23ac532755fd8aad4ced100d369fa"
SOURCE_PATH = "app/src/main/java/ru/railbrake/calculator/ui/FirstAidScreen.kt"
SOURCE_ID = "common.source.first-aid-donor"
KIT_SOURCE_ID = "common.source.worker-kit-262n-donor"

def matched(text, start, opening="(", closing=")"):
    assert text[start] == opening
    depth, quoted, escaped = 0, False, False
    for i in range(start, len(text)):
        c = text[i]
        if quoted:
            if escaped: escaped = False
            elif c == "\\": escaped = True
            elif c == '"': quoted = False
        elif c == '"': quoted = True
        elif c == opening: depth += 1
        elif c == closing:
            depth -= 1
            if depth == 0: return text[start+1:i], i+1
    raise ValueError("unbalanced source")

def fields(body):
    result={}
    pieces=[]
    current=0
    depth, quoted, escaped=0,False,False
    for i,c in enumerate(body):
        if quoted:
            if escaped: escaped=False
            elif c=="\\": escaped=True
            elif c=='"': quoted=False
        elif c=='"': quoted=True
        elif c=='(': depth+=1
        elif c==')': depth-=1
        elif c==',' and depth==0:
            pieces.append(body[current:i].strip());current=i+1
    pieces.append(body[current:].strip())
    for p in pieces:
        if not p: continue
        k,v=p.split("=",1);result[k.strip()]=v.strip()
    return result

def strings(expr):
    return [json.loads(s) for s in re.findall(r'"(?:\\.|[^"\\])*"',expr)]

def parse_source(source):
    data=source.encode()
    actual=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
    if actual!=PINNED_BLOB: raise ValueError(f"unpinned source blob: {actual}")
    a=source.index("internal val firstAidTopics = listOf(")
    b=source.index("internal val firstAidSearchKeywords",a)
    section=source[a:b]
    topics=[]
    for m in re.finditer(r'\bFirstAidTopic\s*\(',section):
        raw,_=matched(section,m.end()-1)
        f=fields(raw)
        expected={"id","title","whenToUse","actions","dont","note","source"}
        if set(f)-expected: raise ValueError(f"unknown source fields {set(f)-expected}")
        if not {"id","title","whenToUse","actions"}<=set(f): raise ValueError("missing topic fields")
        topics.append({k:strings(f[k]) for k in ("id","title","whenToUse","actions","dont","note","source") if k in f})
    if len(topics)!=17 or len({t["id"][0] for t in topics})!=17:
        raise ValueError("expected 17 distinct donor topics")
    if {"hypothermia","frostbite"}-{t["id"][0] for t in topics}:
        raise ValueError("cold injury topics were merged")
    search=source[source.index("internal val firstAidSearchKeywords"):source.index("internal val workerKitLines")]
    keywords={}
    for m in re.finditer(r'"([^"]+)"\s+to\s+listOf\(',search):
        raw,_=matched(search,m.end()-1)
        keywords[m.group(1)]=strings(raw)
    if set(keywords)!={t["id"][0] for t in topics}: raise ValueError("keyword coverage")
    m=re.search(r'private const val FIRST_AID_SOURCE\s*=\s*"([^"]+)"',source)
    if not m: raise ValueError("source citation missing")
    kit=source[source.index("internal val workerKitLines = listOf("):]
    kit_raw,_=matched(kit,kit.index("listOf(")+len("listOf"))
    kit_lines=strings(kit_raw)
    if len(kit_lines)!=10: raise ValueError("worker kit source changed")
    return topics,keywords,m.group(1),kit_lines,actual

def make_pack(source):
    topics,keywords,citation,kit_lines,blob=parse_source(source)
    entries=[]
    for t in topics:
        id=t["id"][0]
        blocks=[
            {"title":"Когда применять","lines":t["whenToUse"]},
            {"title":"Действия — исходный текст, требует проверки","lines":t["actions"]},
            {"title":"Не делать — исходный текст, требует проверки","lines":t.get("dont",[])},
        ]
        if t.get("note"): blocks.append({"title":"Примечание","lines":t["note"]})
        if t.get("source"): blocks.append({"title":"Источник темы","lines":t["source"]})
        entries.append({
            "id":f"common.first-aid.{id}","aliases":[],"type":"FIRST_AID",
            "owner":{"kind":"COMMON"},"publicationStatus":"CANDIDATE",
            "layer":"STANDARD","provenance":"UNKNOWN","sourceStatus":"UNKNOWN",
            "actionDisposition":"INFORMATION_ONLY","title":t["title"][0],
            "summary":t["whenToUse"][0],"details":[],"blocks":blocks,
            "searchTerms":keywords[id],"sourceRefs":[SOURCE_ID],
            "links":[{"type":"SOURCE","targetId":SOURCE_ID,"scope":"COMMON_INTERNAL"}]
        })
    entries.append({
        "id":"common.first-aid.worker-kit","type":"FIRST_AID","owner":{"kind":"COMMON"},
        "publicationStatus":"CANDIDATE","layer":"STANDARD","provenance":"UNKNOWN",
        "sourceStatus":"UNKNOWN","actionDisposition":"INFORMATION_ONLY",
        "title":"Аптечка работника — состав из донора","summary":"Исходный перечень; редакция источника требует проверки.",
        "details":[],"blocks":[{"title":"Комплектность — исходный текст, требует проверки","lines":kit_lines}],
        "searchTerms":["аптечка","бинт","жгут","перчатки","маска","салфетки","пластырь","ножницы","покрывало"],
        "sourceRefs":[KIT_SOURCE_ID],"links":[{"type":"SOURCE","targetId":KIT_SOURCE_ID,"scope":"COMMON_INTERNAL"}]
    })
    entries.append({
        "id":SOURCE_ID,"type":"SOURCE","owner":{"kind":"COMMON"},
        "publicationStatus":"CANDIDATE","provenance":"UNKNOWN","sourceStatus":"UNKNOWN",
        "actionDisposition":"INFORMATION_ONLY","title":"Первая помощь — источник из донора",
        "summary":citation,"details":[f"Donor: DomEnota-maker/Test- @ 3176d6ee228f0ed4b78371f45209e10c1c724eff",
            f"Path: {SOURCE_PATH}",f"Git blob: {blob}",
            "Указание источника в доноре не подтверждает его текущую редакцию и применимость."],
        "sourceRefs":[],"links":[]
    })
    entries.append({
        "id":KIT_SOURCE_ID,"type":"SOURCE","owner":{"kind":"COMMON"},
        "publicationStatus":"CANDIDATE","provenance":"UNKNOWN","sourceStatus":"UNKNOWN",
        "actionDisposition":"INFORMATION_ONLY","title":"Аптечка работника — источник из донора",
        "summary":"Донор ссылается на приказ Минздрава России №262н; редакция не проверена.",
        "details":[f"Donor: DomEnota-maker/Test- @ 3176d6ee228f0ed4b78371f45209e10c1c724eff",
            f"Path: {SOURCE_PATH}",f"Git blob: {blob}"],
        "sourceRefs":[],"links":[]
    })
    return {"manifest":{"schemaVersion":1,"packId":"common.first-aid.topics-001",
        "packVersion":"0.1.0","family":None,"modelIds":[],"variantIds":[],
        "locale":"ru-RU","entries":[e["id"] for e in entries],
        "requiresRuntime":"1.1.0","sourceCatalogVersion":"test-3176d6ee-first-aid",
        "checksums":{"sourceGitBlob":blob}},
        "entries":entries}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("source",type=Path)
    parser.add_argument("output",type=Path)
    args=parser.parse_args()
    content=json.dumps(make_pack(args.source.read_text()),ensure_ascii=False,indent=2)+"\n"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(content)
    print("17_FIRST_AID_TOPICS_AND_WORKER_KIT_IMPORTED",hashlib.sha256(content.encode()).hexdigest())

if __name__=="__main__":main()
