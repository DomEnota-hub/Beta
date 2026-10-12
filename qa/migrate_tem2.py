#!/usr/bin/env python3
"""Pinned TEM2/TEM2U source-object importer; scheme geometry stays training-only."""
import base64
import collections
import hashlib
import json
from pathlib import Path

from migrate_chme3 import TYPE_BY_SECTION, LINK_TYPES, compact

DONOR="3176d6ee228f0ed4b78371f45209e10c1c724eff"
ROOT=Path("content-packs/diesel/tem2-family")
VARIANTS=("tem2","tem2u")
PINS={
    ("tem2","catalog"):"c7a94c1cd2687b84de4358b80773e3156c6b93d7",
    ("tem2","diagnostics"):"93b3e9b79ab5f3a7847a3090b316969ae0b88226",
    ("tem2u","catalog"):"766ac526fa4b86245704ed0252c2fdf3998a0e78",
    ("tem2u","diagnostics"):"360ced5392b4cd19b819ad8c11b148f0651959d2",
    ("shared","layouts"):"10b70f9644011a1fd5347e21d6f86fbd2a20ec95",
    ("shared","sequences"):"526e7301e0902a6f868454a8ebf39563dce45d33",
}


def filename(variant,kind):
    if variant=="shared":
        return "tem2_scheme_layout_metadata" if kind=="layouts" else "tem2_stepwise_scheme_flows"
    return f"tem2_{variant}_{kind}"


def read_assets(donor_dir):
    result={}
    for key,sha in PINS.items():
        name=filename(*key)
        raw=base64.b64decode((donor_dir/f"{name}.json.b64").read_text())
        assert hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==sha,key
        doc=json.loads(raw)
        records=doc[{"catalog":"entries","diagnostics":"scenarios",
                     "layouts":"layouts","sequences":"sequences"}[key[1]]]
        result[key]=records
    return result


def build(donor_dir):
    arrays=read_assets(donor_dir)
    seq_variants={r["id"]:r["family"].lower() for r in arrays["shared","sequences"]}
    assert len(seq_variants)==17
    groups=collections.defaultdict(list)
    for (source_variant,kind),records in arrays.items():
        for index,record in enumerate(records):
            variant=(seq_variants[record["sequenceId"]] if kind=="layouts" else
                     seq_variants[record["id"]] if kind=="sequences" else source_variant)
            source_id=record.get("id") or record.get("sequenceId")
            groups[(kind,source_id,compact(record))].append((variant,source_variant,index,record))
    conflicts=collections.Counter((k,sid) for k,sid,_ in groups)
    variant_map={}
    grouped=collections.defaultdict(list)
    mappings=[]
    for (kind,source_id,_),copies in sorted(groups.items()):
        variants=[v for v,_,_,_ in copies]
        suffix="" if conflicts[(kind,source_id)]==1 else "."+"-".join(variants)
        canonical=f"tem2.{kind}.{source_id.lower()}{suffix}"
        variant,source_variant,index,record=copies[0]
        name=filename(source_variant,kind)
        type_name=("DIAGNOSTIC_SCENARIO" if kind=="diagnostics" else
                   "ATLAS_SCHEME" if kind in ("layouts","sequences") else
                   TYPE_BY_SECTION[record["section"]])
        entry={
            "id":canonical,"type":type_name,
            "owner":{"kind":"MODEL","modelId":"tem2-family"},
            "applicability":{"modelIds":["tem2-family"],"variantIds":variants},
            "layer":"STANDARD","publicationStatus":"CANDIDATE",
            "provenance":"UNKNOWN","sourceStatus":"UNKNOWN",
            "actionDisposition":"INFORMATION_ONLY",
            "title":record.get("title") or source_id,
            "summary":record.get("subtitle") or record.get("symptom") or
                      record.get("functionalDisclaimer") or None,
            "searchTerms":record.get("searchAliases",[]) if kind=="catalog" else
                          record.get("searchTerms",[]) if kind=="diagnostics" else [],
            "sourceRefs":record.get("sourceRefs",[]) if kind=="diagnostics" else [],
            "blocks":record.get("blocks",[]) if kind=="catalog" else [],
            "links":[],
            "sourceObject":{"sourcePath":f"app/src/main/assets/technical/{name}.json",
                            "sourceBlobSha":PINS[(source_variant,kind)],"object":record},
        }
        grouped[kind].append(entry)
        for j,(v,sv,idx,_) in enumerate(copies):
            assert (v,kind,source_id) not in variant_map
            variant_map[v,kind,source_id]=entry
            mappings.append({"variant":v,"sourceKind":kind,"sourceId":source_id,
                             "sourceIndex":idx,"canonicalId":canonical,
                             "disposition":"MIGRATED" if j==0 else "MERGED_WITH_CANONICAL",
                             "gitBlob":PINS[(sv,kind)]})
    unresolved=[]
    for kind,entries in grouped.items():
        for e in entries:
            raw=e["sourceObject"]["object"]
            for variant in e["applicability"]["variantIds"]:
                if kind=="catalog": targets=[("catalog",x) for x in raw.get("relatedIds",[])]
                elif kind=="diagnostics": targets=[("catalog",x) for x in raw.get("equipmentRefs",[])]
                elif kind=="sequences": targets=[("catalog",raw["sourceSchemeRef"]),("layouts",raw["id"])]
                else: targets=[("sequences",raw["sequenceId"])]
                for target_kind,target_id in targets:
                    target=variant_map.get((variant,target_kind,target_id))
                    if target is None:
                        unresolved.append({"source":e["id"],"variant":variant,
                                           "targetKind":target_kind,"sourceTargetId":target_id})
                        continue
                    e["links"].append({"type":LINK_TYPES[target["type"]] if target["type"]
                                       in LINK_TYPES else "ATLAS_SCHEME",
                                       "targetId":target["id"],"role":kind,
                                       "applicability":{"variantIds":[variant]}})
    outputs={}
    subdirs={"catalog":"technical-data/catalog","diagnostics":"diagnostics/recommended",
             "layouts":"atlas/layouts","sequences":"atlas/sequences"}
    for kind,entries in grouped.items():
        for offset in range(0,len(entries),20):
            n=offset//20+1;chunk=entries[offset:offset+20]
            relevant=[(v,k) for v,k in PINS if k==kind]
            m={"schemaVersion":1,"packId":f"tem2-family.{kind}.{n:02d}",
               "packVersion":"0.1.0","family":"DIESEL","modelIds":["tem2-family"],
               "variantIds":sorted({v for e in chunk for v in e["applicability"]["variantIds"]}),
               "locale":"ru-RU","entries":[e["id"] for e in chunk],
               "requiresRuntime":"1.1.0","sourceCatalogVersion":f"test-{DONOR[:8]}-tem2",
               "checksums":{f"{v}.{k}.gitBlob":PINS[(v,k)] for v,k in relevant}}
            path=ROOT/subdirs[kind]/f"{kind}-{n:02d}.pack.json"
            outputs[path]=json.dumps({"manifest":m,"entries":chunk},ensure_ascii=False,
                                     separators=(",", ":"))+"\n"
    audit={"schemaVersion":1,"donorCommit":DONOR,
           "sourceCounts":{f"{v}.{k}":len(a) for (v,k),a in arrays.items()},
           "canonicalCounts":{k:len(a) for k,a in grouped.items()},
           "mappings":sorted(mappings,key=lambda x:(x["variant"],x["sourceKind"],x["sourceIndex"])),
           "unresolvedReferences":unresolved,
           "linkCount":sum(len(e["links"]) for a in grouped.values() for e in a),
           "layoutPolicy":"training geometry only; not a mounting diagram"}
    outputs[ROOT/"migration/source-audit.json"]=(json.dumps(audit,ensure_ascii=False,
                                                            separators=(",", ":"))+"\n")
    return outputs


if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser();p.add_argument("--donor-dir",type=Path,required=True)
    p.add_argument("--output-root",type=Path,default=Path("."));a=p.parse_args()
    outputs=build(a.donor_dir)
    for path,content in outputs.items():
        target=a.output_root/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(content)
    print("TEM2_VARIANT_PACKS",len(outputs)-1)
