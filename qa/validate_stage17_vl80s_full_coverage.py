#!/usr/bin/env python3
"""Independent Stage17 donor-ID research accounting; never grants operational authority."""
import argparse
import copy
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DONOR = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BLOB = "6ffdfdabf2f467dcdc4958768905f2b675ac0c26"
BASELINE_ONLY = {"aux-machines"}
EXPECTED_REPEATS = {"ekg-position-mismatch", "gv-air-loss"}

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def load(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(path.read_text(encoding="utf-8"))

def files():
    root = ROOT / "content-packs/electric/vl80s/diagnostics/authoring"
    result = list(root.glob("stage[4567]-*.research.json*"))
    docs = ROOT / "docs/diagnostics"
    result += list(docs.glob("STAGE7_AUXILIARY_CLOSEOUT_*.json"))
    for stage in range(8, 18):
        result += list(docs.glob(f"STAGE{stage}_*.json"))
    return sorted(set(result))

def versions(c):
    if "versions" in c:
        return c["versions"]
    if "versionDrafts" in c:
        return c["versionDrafts"]
    if "short" in c and "detailed" in c:
        return {"SHORT": c["short"], "DETAILED": c["detailed"]}
    return {}

def validate_candidate(c, donor, path):
    ident = c["originalId"]
    require(ident in donor, f"unknown original ID {ident}: {path}")
    require(c.get("publicationStatus") == "CANDIDATE", f"{ident}: published")
    for field in ("runtimeImport", "executable", "actionAuthorityGranted"):
        require(c.get(field) is False, f"{ident}: {field} is not false")
    for field in ("sourceAuthorityVerified", "exactInstalledVariantConfirmed"):
        if field in c:
            require(c[field] is False, f"{ident}: unverified authority promoted")
    if "donorPinnedSha" in c:
        require(c["donorPinnedSha"] == DONOR, f"{ident}: donor SHA mismatch")
    if "canonicalDonorCommit" in c:
        require(c["canonicalDonorCommit"] == DONOR, f"{ident}: pilot donor mismatch")
    if "authoringProfileId" in c:
        require(c["authoringProfileId"] == "vl80s-general", f"{ident}: profile drift")
    v = versions(c)
    require({"SHORT", "DETAILED"} <= set(v), f"{ident}: version missing")
    counts = []
    for mode in ("SHORT", "DETAILED"):
        route = v[mode]
        nodes = route.get("nodes", [])
        by_id = {n["id"]: n for n in nodes}
        require(nodes and len(nodes) == len(by_id), f"{ident}/{mode}: node IDs")
        start = route.get("startNodeId")
        require(start in by_id, f"{ident}/{mode}: start missing")
        seen, pending = set(), [start]
        while pending:
            key = pending.pop()
            require(key in by_id, f"{ident}/{mode}: broken edge")
            if key in seen:
                continue
            seen.add(key)
            n = by_id[key]
            require(n.get("operationRequested") is False, f"{ident}/{mode}: operation")
            if n["type"] == "QUESTION":
                edges = n.get("responses", {})
                require(set(edges) == {"YES", "NO", "UNKNOWN"},
                        f"{ident}/{mode}: non-tristate")
                require(by_id.get(edges["UNKNOWN"], {}).get("type") == "STOP",
                        f"{ident}/{mode}: UNKNOWN not STOP")
                pending.extend(edges.values())
            else:
                require(n["type"] in ("STOP", "OBSERVATION_REPORT"),
                        f"{ident}/{mode}: leaf type")
                require(n.get("responses") == {}, f"{ident}/{mode}: leaf edge")
        require(seen == set(by_id), f"{ident}/{mode}: unreachable nodes")
        counts.append(len(nodes))
    extensions = c.get("informationExtensions")
    if extensions is None:
        extensions = [r for mode in ("SHORT", "DETAILED")
                      for r in v[mode].get("extendedRoutes", [])]
    require(len(extensions) >= 4, f"{ident}: missing source alternatives")
    return counts + [len(extensions)]

def audit(donor, records, baseline):
    by_id = defaultdict(list)
    totals = [0, 0, 0]
    for path, c in records:
        counts = validate_candidate(c, donor, path)
        by_id[c["originalId"]].append(path)
        totals = [a + b for a, b in zip(totals, counts)]
    repeated = {ident for ident, paths in by_id.items() if len(paths) > 1}
    require(repeated == EXPECTED_REPEATS, f"unexpected repeated IDs: {repeated}")
    require(all(len(by_id[x]) == 2 for x in repeated), "duplicate count changed")
    missing = set(donor) - set(by_id)
    require(missing == BASELINE_ONLY, f"research gaps changed: {missing}")
    require(set(baseline) == BASELINE_ONLY, "baseline identity changed")
    for ident in missing:
        require(baseline[ident]["publicationStatus"] == "CANDIDATE",
                "legacy baseline unexpectedly published")
        require(baseline[ident]["sourceRefs"] == [],
                "legacy baseline source status changed")
    require(len(donor) == 103 and len(by_id) == 102,
            "donor/research coverage changed")
    return by_id, totals

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    args = parser.parse_args()
    inv = load(ROOT / "content-packs/electric/vl80s/migration/diagnostics-inventory.json")
    require(inv["sourceSnapshot"]["commit"] == DONOR
            and inv["sourceSnapshot"]["blobSha"] == BLOB, "pinned source drift")
    donor = {x["id"]: x for x in inv["scenarios"]}
    require(len(donor) == inv["scenarioCount"] == 103, "donor inventory drift")
    paths = files()
    records = []
    for path in paths:
        doc = load(path)
        candidates = doc.get("candidates")
        if candidates is None and "originalId" in doc:
            candidates = [doc]
        records.extend((str(path.relative_to(ROOT)), c) for c in (candidates or []))
    pack = load(ROOT / "content-packs/electric/vl80s/diagnostics/recommended/auxiliary.pack.json")
    baseline = {entry["aliases"][0]: entry for entry in pack["entries"]
                if entry["id"] == "vl80s.diag.aux-machines"}
    by_id, totals = audit(donor, records, baseline)
    cats = Counter(donor[ident]["category"] for ident in by_id)
    require(cats["Вспомогательные машины"] == 13
            and sum(cats.values()) == 102, "category research count drift")
    if args.negative:
        path, first = records[0]
        for field, value in (("runtimeImport", True), ("originalId", "invented-id")):
            mutated = copy.deepcopy(first)
            mutated[field] = value
            try:
                validate_candidate(mutated, donor, path)
            except AssertionError:
                continue
            raise AssertionError(f"negative mutation accepted: {field}")
        print("STAGE17_103_AUDIT_NEGATIVE_PASS 2")
    print(f"STAGE17_103_AUDIT_PASS donor=103 research=102 "
          f"baseline_only=aux-machines files={len(paths)} "
          f"records={len(records)} totals={totals} "
          f"intentional_duplicates={sorted(EXPECTED_REPEATS)}")
    print("NOT_CLOSED: aux-machines needs source-first SHORT/DETAILED and extensions; "
          "runtime remains blocked; device QA deferred")

if __name__ == "__main__":
    main()
