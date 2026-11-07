#!/usr/bin/env python3
"""Read-only-source CHME3 authoring handoff gate; never publishes diagnostics."""
import argparse
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BASE = "content-packs/diesel/chme3-family"
INDEX = BASE + "/migration/diagnostic-source-index.json"
PROFILES = BASE + "/migration/profile-source-index.json"
PILOT = BASE + "/diagnostics/authoring/stage4-rheostatic.research.json"
PACKS = [BASE + f"/diagnostics/recommended/diagnostics-0{i}.pack.json" for i in range(1, 5)]
DOC_PINS = {
    "docs/locomotives/chme3/diagnostics_996r_detail_pass3.json": ("f29c287c2eae1fb60e0cac61cab098fa8cae3c0f", 6),
    "docs/locomotives/chme3/diagnostics_brake_aux_pass3.json": ("1094688cc2e633fab21b6f989cc902f7a34d19d2", 8),
    "docs/locomotives/chme3/diagnostics_electrical_control_pass3.json": ("41d241cb0b58e5657ef0d6210e7b272d44df52d0", 10),
    "docs/locomotives/chme3/diagnostics_extended_pass3.json": ("9fa23a5c9e3da49fb025fb55245227314f6020da", 20),
    "docs/locomotives/chme3/diagnostics_powerplant_pass3.json": ("63988703bb795e82f40335a756b8b9bd3cad8e0a", 12),
    "docs/locomotives/diesel/chme3-family/chme3e/diagnostics_stage3.json": ("e6ac2baebda3a9f545a5ff1612b0b24d3c58be6e", 12),
}
PROFILE_PINS = {
    "docs/locomotives/chme3/profiles.json": "d8dc20124563c54756d53955c853c52839a64de9",
    "docs/locomotives/diesel/chme3-family/family_manifest.json": "791c42a64df0d23ee0327746132c59f9c60fc080",
    "docs/locomotives/diesel/chme3-family/chme3e/profile.json": "39743600eb4ff4d043380df5f75cff5641b37eaa",
    "docs/locomotives/diesel/chme3-family/chme3e/inheritance.json": "c8f56386499b9f232645bf5ebd4f8f6c3a4e563b",
}
GZIP_PINS = {
    "app/src/main/assets/technical/chme3_chme3_diagnostics.json.gz": "6a6068ad1ea54cb964b65a10ecf5c2425b2276e8",
    "app/src/main/assets/technical/chme3_chme3t_diagnostics.json.gz": "41809c6464113f48ef032ed70d2cb4483f12c28e",
    "app/src/main/assets/technical/chme3_chme3e_diagnostics.json.gz": "1ab9ae40bc90479eacb006d0eb62dd45e9f387fe",
}
LABELS = {"ЧМЭ3": "chme3", "ЧМЭ3Т": "chme3t", "ЧМЭ3Э": "chme3e"}
BINDINGS = {"chme3-base": "chme3", "chme3t-rheostatic": "chme3t", "chme3e-electronic": "chme3e"}


def need(ok, label):
    if not ok:
        raise AssertionError(label)


def load(root):
    def read(path):
        return json.loads((root / path).read_text(encoding="utf-8"))
    return read(INDEX), read(PROFILES), {p: read(p) for p in PACKS}, read(PILOT)


def validate(index, profiles, packs, pilot):
    need(index["donorCommit"] == profiles["donorCommit"] == PIN, "pinned donor commit")
    for name, obj in (("diagnostics", index), ("profiles", profiles)):
        need(obj["publicationStatus"] == "CANDIDATE", name + " candidate")
        need(obj["actionDisposition"] == "INFORMATION_ONLY", name + " information only")
        need(obj["runtimeImport"] is False, name + " no runtime")
    need(index["relationPolicy"] == "ID_AND_TITLE_MATCH_DOES_NOT_CONFER_AUTHORITY_OR_FIELD_EQUIVALENCE", "source/canonical distinction")
    need(profiles["profileBindings"] == BINDINGS, "three disjoint profile bindings")
    need(len(profiles["documents"]) == len(PROFILE_PINS), "four profile documents")
    need({d["sourcePath"]: d["sourceBlobSha"] for d in profiles["documents"]} == PROFILE_PINS, "profile donor blob pins")
    profile_docs = {d["sourcePath"]: d["sourceObject"] for d in profiles["documents"]}
    need([p["id"] for p in profile_docs["docs/locomotives/chme3/profiles.json"]["profiles"]] == list(BINDINGS), "profile IDs")
    inherit = profile_docs["docs/locomotives/diesel/chme3-family/chme3e/inheritance.json"]
    need(inherit["profileId"] == "chme3e-electronic", "CHME3E inheritance owner")
    need("NO_AUTOMATIC_INHERITANCE" in json.dumps(profile_docs["docs/locomotives/chme3/profiles.json"], ensure_ascii=False) or
         "NO_AUTOMATIC_INHERITANCE" in json.dumps(inherit, ensure_ascii=False), "no automatic CHME3T inheritance")
    need("CHME3T-EQ-BRAKE-RESISTORS" in inherit["hardExclusions"], "CHME3E rheostatic hard exclusion")

    need(len(index["documents"]) == len(DOC_PINS), "six documentary snapshots")
    need({d["sourcePath"]: (d["sourceBlobSha"], len(d["sourceObject"]["scenarios"])) for d in index["documents"]} == DOC_PINS, "six pinned documentary counts")
    sources = {}
    for doc in index["documents"]:
        for offset, source in enumerate(doc["sourceObject"]["scenarios"]):
            ident = source["id"]
            need(ident not in sources, "duplicate donor document ID " + ident)
            sources[ident] = (doc["sourcePath"], "/scenarios/" + str(offset), source)
    need(len(sources) == 68, "68 unique documentary source IDs")
    need(sum(i.startswith("CHME3E-DIAG-") for i in sources) == 12, "12 CHME3E-specific IDs")
    need(sum(i.startswith("CHME3-DIAG-") for i in sources) == 56, "56 shared CHME3 IDs")

    canonical = {}
    for path in PACKS:
        pack = packs[path]
        need(pack["manifest"]["entries"] == [e["id"] for e in pack["entries"]], "pack manifest " + path)
        for entry in pack["entries"]:
            need(entry["id"] not in canonical, "duplicate canonical ID")
            canonical[entry["id"]] = (path, entry)
    need(len(canonical) == 68, "68 unique canonical candidates")
    need(len(index["matches"]) == 68, "68 documentary relations")
    seen = set()
    for match in index["matches"]:
        ident, dest = match["sourceId"], match["canonicalId"]
        need(ident in sources and ident not in seen, "document relation unique " + ident)
        seen.add(ident)
        source_path, pointer, source = sources[ident]
        need(match["sourcePath"] == source_path and match["sourcePointer"] == pointer, "source pointer " + ident)
        need(match["relation"] == "ID_AND_TITLE_MATCH_ONLY", "no automatic authority " + ident)
        need(dest in canonical, "canonical match " + ident)
        pack_path, entry = canonical[dest]
        need(match["canonicalPack"] == pack_path, "canonical pack " + ident)
        need(entry["sourceObject"]["object"]["id"] == ident, "gzip projection ID " + ident)
        need(entry["title"] == source["title"] == entry["sourceObject"]["object"]["title"], "title parity " + ident)
        need(entry["applicability"]["variantIds"] == [LABELS[p] for p in source["profiles"]], "variant parity " + ident)
        need(entry["publicationStatus"] == "CANDIDATE" and entry["actionDisposition"] == "INFORMATION_ONLY", "candidate not authority " + ident)
        need(entry["sourceStatus"] == "UNKNOWN" and entry["provenance"] == "UNKNOWN", "unverified authority " + ident)
        need(entry["blocks"] == [], "no published instruction blocks " + ident)
        src_obj = entry["sourceObject"]
        need(GZIP_PINS.get(src_obj["sourcePath"]) == src_obj["sourceBlobSha"], "gzip provenance pin " + ident)
        if ident == "CHME3-DIAG-110":
            need(entry["applicability"]["variantIds"] == ["chme3t"], "CHME3T rheostatic isolation")
        if ident.startswith("CHME3E-DIAG-"):
            need(entry["applicability"]["variantIds"] == ["chme3e"], "CHME3E electronic isolation")
    need(seen == set(sources), "all 68 documentary records matched")
    need(pilot["originalId"] == "CHME3-DIAG-110" and pilot["authoringProfileId"] == "chme3t-rheostatic", "rheostatic pilot identity")
    need(pilot["canonicalDonorCommit"] == PIN and pilot["canonicalDonorBlob"] == GZIP_PINS["app/src/main/assets/technical/chme3_chme3t_diagnostics.json.gz"], "pilot donor pin")
    for key in ("runtimeImport", "executable", "actionAuthorityGranted", "exactInstalledProfileConfirmed", "sourceAuthorityVerified"):
        need(pilot[key] is False, "pilot blocked " + key)
    need(pilot["publicationStatus"] == "CANDIDATE", "pilot publication blocked")
    return {"documentary": len(sources), "canonical": len(canonical), "profile_documents": len(profiles["documents"])}


def negative(index, profiles, packs, pilot):
    mutations = []
    def check_mutation(label, fn):
        a, b, c, d = copy.deepcopy((index, profiles, packs, pilot))
        fn(a, b, c, d)
        try:
            validate(a, b, c, d)
        except (AssertionError, KeyError, ValueError):
            mutations.append(label)
            return
        raise AssertionError("negative test unexpectedly passed: " + label)
    check_mutation("runtime promotion", lambda a,b,c,d: a.__setitem__("runtimeImport", True))
    check_mutation("donor commit drift", lambda a,b,c,d: a.__setitem__("donorCommit", "unverified"))
    check_mutation("missing relation", lambda a,b,c,d: a["matches"].pop())
    check_mutation("duplicate source", lambda a,b,c,d: a["matches"].append(copy.deepcopy(a["matches"][0])))
    check_mutation("source blob drift", lambda a,b,c,d: a["documents"][0].__setitem__("sourceBlobSha", "unverified"))
    check_mutation("profile alias drift", lambda a,b,c,d: b["profileBindings"].__setitem__("chme3e-electronic", "chme3t"))
    check_mutation("CHME3E inheritance leak", lambda a,b,c,d: b["documents"][3]["sourceObject"]["hardExclusions"].remove("CHME3T-EQ-BRAKE-RESISTORS"))
    check_mutation("CHME3T EDB leak", lambda a,b,c,d: next(e for p in c.values() for e in p["entries"] if e["sourceObject"]["object"]["id"] == "CHME3-DIAG-110")["applicability"].__setitem__("variantIds", ["chme3", "chme3t", "chme3e"]))
    check_mutation("CHME3E variant leak", lambda a,b,c,d: next(e for p in c.values() for e in p["entries"] if e["sourceObject"]["object"]["id"] == "CHME3E-DIAG-005")["applicability"].__setitem__("variantIds", ["chme3t", "chme3e"]))
    check_mutation("pilot activation", lambda a,b,c,d: d.__setitem__("executable", True))
    check_mutation("canonical action promotion", lambda a,b,c,d: c[PACKS[0]]["entries"][0].__setitem__("actionDisposition", "AUTHORIZED"))
    check_mutation("canonical title drift", lambda a,b,c,d: c[PACKS[0]]["entries"][0].__setitem__("title", "DRIFT"))
    return len(mutations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    source, profile, packs, pilot = load(ROOT)
    counts = validate(source, profile, packs, pilot)
    print("CHME3_AUTHORING_HANDOFF_PASS", json.dumps(counts, sort_keys=True))
    if args.negative:
        print("CHME3_AUTHORING_HANDOFF_NEGATIVE_PASS", negative(source, profile, packs, pilot))
