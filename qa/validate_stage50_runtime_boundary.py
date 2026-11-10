#!/usr/bin/env python3
"""Stage 50: research/runtime/APK boundary. Never an operational approval."""
import argparse
import copy
import gzip
import io
import json
import re
import zipfile
from pathlib import Path
from validate_stage49_cross_family_research import run as stage49_run

ROOT = Path(__file__).resolve().parents[1]
PIN = "3176d6ee228f0ed4b78371f45209e10c1c724eff"
BASE = "content-packs/electric/vl80s/diagnostics/authoring/"
EARLY = {
    "pantograph-no-rise": "stage4-pantograph.research.json",
    "gv-no-close": "stage5-gv-no-close.research.json.gz",
    "ekg-stuck": "stage5-ekg-stuck.research.json.gz",
    "gv-no-open": "stage6-gv-no-open.research.json",
    "ekg-slow-transition": "stage6-ekg-slow-transition.research.json",
    "compressor-long-run": "stage7-compressor-long-run.research.json",
    "compressor-no-start": "stage7-compressor-no-start.research.json",
    "compressor-pressure": "stage7-compressor-pressure.research.json",
}
DEFERRED = "DEFERRED_TO_POST_RELEASE_DEVICE_QA"


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def load_candidate(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(path.read_text(encoding="utf-8"))


def check_early(c, ident):
    label = "VL80S/" + ident
    need(c.get("originalId") == ident and
         c.get("scenarioId") == "vl80s.diag." + ident,
         label + " donor scenario ID drift")
    need(c.get("canonicalDonorCommit", c.get("donorPinnedSha")) == PIN,
         label + " donor pin drift")
    need(c.get("authoringProfileId") == "vl80s-general",
         label + " research profile drift")
    need(c.get("publicationStatus") == "CANDIDATE" and
         c.get("runtimeImport") is False and
         c.get("executable") is False and
         c.get("actionAuthorityGranted") is False,
         label + " runtime promotion")
    for flag in ("sourceAuthorityVerified", "exactInstalledVariantConfirmed",
                 "technicalClaimsReviewed", "substantiveSafetyReviewed"):
        if flag in c:
            need(c[flag] is False, label + " false gate " + flag)
    if ident == "pantograph-no-rise":
        need(set(c["versionDrafts"]) == {"SHORT", "DETAILED"},
             label + " missing pilot drafts")
        w = c["extendedWarningContract"]
        need(w["offByDefault"] is True and w["readToEndRequired"] is True and
             w["acknowledgementRequired"] is True and
             w["acknowledgementGrantsActionAuthority"] is False,
             label + " pilot warning bypass")
        need(c["acceptance"]["androidUI"] == "NOT_TESTED",
             label + " fabricated Android QA")
    elif ident in ("gv-no-close", "ekg-stuck"):
        need("short" in c and "detailed" in c,
             label + " missing research versions")
        w = c["historicalVisibility"]
        need(w["default"] == "HIDDEN" and w["warningReadToEnd"] is True and
             w["warningAcknowledged"] is True and
             w["actionPermissionGrantedByWarning"] is False,
             label + " historical warning bypass")
        need(c["integrationAudit"]["actualRuntimeGraphCompared"] is False,
             label + " invented runtime graph parity")
    else:
        need(set(c["versions"]) == {"SHORT", "DETAILED"},
             label + " missing research versions")
        w = c["warningGate"]
        need(w["default"] == "HIDDEN" and w["warningReadToEnd"] is True and
             w["warningAcknowledged"] is True and
             w["warningGrantsActionAuthority"] is False,
             label + " warning bypass")
    device = c.get("deviceQA")
    need(device is None or device in (DEFERRED, "NOT_RUN_DEFERRED"),
         label + " fabricated device QA")


def check_gradle(text):
    need('assets.srcDir("../content-packs")' in text,
         "legacy runtime assets unexpectedly removed")
    match = re.search(r'ignoreAssetsPattern\s*=\s*"([^"]+)"', text)
    need(match is not None, "research assets not excluded")
    parts = set(match.group(1).split(":"))
    need({"authoring", "migration", "*.research.json",
          "*.research.json.gz", "*.candidate.json",
          "*.candidate.json.gz", "*.research.*", "*.candidate.*"} <= parts,
         "research/migration asset exclusions incomplete (candidate.pack.json leak)")


def check_apk(archive):
    names = archive.namelist()
    need(len(names) == len(set(names)), "duplicate APK ZIP entry")
    for name in names:
        if not name.startswith("assets/"):
            continue
        segments = name.split("/")
        need(not ({"authoring", "migration"} & set(segments)),
             "research directory packaged: " + name)
        filename = segments[-1].lower()
        need(not (".research." in filename or ".candidate." in filename or
                  filename.endswith((".research", ".candidate"))),
             "research/candidate file packaged: " + name)
    prefix = "assets/electric/vl80s/"
    need(names.count(prefix + "runtime-index.json") == 1,
         "published legacy runtime index missing")
    index = json.loads(archive.read(prefix + "runtime-index.json"))
    need(index["modelId"] == "vl80s", "wrong runtime model")
    for path in index["packs"]:
        need(names.count("assets/" + path) == 1,
             "indexed published pack missing: " + path)
    diag_index_path = index["featureIndexes"]["diagnostics"]
    need(names.count("assets/" + diag_index_path) == 1,
         "legacy diagnostic index missing")
    diag = json.loads(archive.read("assets/" + diag_index_path))
    flow_path = diag["executableFlow"]
    need(names.count("assets/" + flow_path) == 1,
         "legacy executable flow missing")
    flow = json.loads(archive.read("assets/" + flow_path))
    need(flow["modelId"] == "vl80s" and flow["scenarioCount"] == 103,
         "legacy runtime baseline changed without review")


def audit():
    groups, gaps = stage49_run()
    need(not any(g["type"] == "MISSING_PER_CANDIDATE_DEVICE_QA_MARKER"
                 for g in gaps), "missing individual deferred device QA markers")
    for ident in ("CHME3-DIAG-%03d" % n for n in range(1, 13)):
        candidate = groups["CHME3"][ident][0]
        need(candidate.get("deviceQA") == DEFERRED,
             "CHME3 deferred device QA marker missing: " + ident)
    source = json.loads((ROOT / "content-packs/electric/vl80s/diagnostics/"
                         "migration/diagnostics-source.candidate.json")
                        .read_text(encoding="utf-8"))
    need(source["donorCommit"] == PIN, "source snapshot donor drift")
    original_ids = {row["id"] for row in source["sourceObject"]["scenarios"]}
    need(len(original_ids) == 103, "source snapshot count drift")
    need(set(groups["VL80S_BATCH"]) | set(EARLY) == original_ids,
         "8 early IDs do not reconcile to 95 batch IDs")
    for ident, filename in EARLY.items():
        check_early(load_candidate(ROOT / BASE / filename), ident)
    # These two authoring packs sit outside the excluded migration/authoring
    # directories. Their CANDIDATE status must never be confused with runtime.
    for family in ("diesel/chme3-family", "electric/ermak"):
        candidate_path = ROOT / "content-packs" / family / "atlas/shared-scheme-pairs.candidate.pack.json"
        need(candidate_path.is_file(), "candidate scheme pack missing: " + family)
        candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        need(candidate["manifest"]["packId"].endswith(".candidate"),
             "candidate manifest status drift: " + family)
        need(candidate["entries"] and all(
            entry.get("publicationStatus") == "CANDIDATE"
            for entry in candidate["entries"]),
            "unreviewed scheme candidate promotion: " + family)
    check_gradle((ROOT / "app-shell/build.gradle.kts").read_text(encoding="utf-8"))
    return {"candidateSchemePacksExcluded": 2, "batchCandidates": sum(map(len, groups.values())),
            "earlySourceIdentities": len(EARLY),
            "chme3DeviceQAMarkersRepaired": 12,
            "runtimeApproval": False,
            "deviceQA": "NOT_RUN_DEFERRED",
            "earlyGraphParity": "NOT_VERIFIED"}


def negative():
    c = load_candidate(ROOT / BASE / EARLY["gv-no-open"])
    mutations = [
        lambda x: x.update(runtimeImport=True),
        lambda x: x.update(publicationStatus="PUBLISHED"),
        lambda x: x.update(actionAuthorityGranted=True),
        lambda x: x.update(originalId="gv-no-close"),
        lambda x: x.update(donorPinnedSha="untrusted"),
        lambda x: x["warningGate"].update(warningReadToEnd=False),
        lambda x: x.update(deviceQA="PASS"),
    ]
    rejected = 0
    for mutate in mutations:
        changed = copy.deepcopy(c)
        mutate(changed)
        try:
            check_early(changed, "gv-no-open")
        except (AssertionError, KeyError):
            rejected += 1
        else:
            raise AssertionError("unsafe early-candidate mutation escaped")
    build = (ROOT / "app-shell/build.gradle.kts").read_text(encoding="utf-8")
    try:
        check_gradle(build.replace(":authoring", ":unprotected"))
    except AssertionError:
        rejected += 1
    else:
        raise AssertionError("missing authoring exclusion escaped")
    # Independent APK leak fixtures must fail before the VL80S runtime index
    # check, including candidates stored outside authoring/migration dirs.
    fixtures = (
        ("assets/electric/vl80s/diagnostics/authoring/stage4-pantograph.research.json", "research"),
        ("assets/diesel/chme3-family/atlas/shared-scheme-pairs.candidate.pack.json", "candidate"),
        ("assets/electric/ermak/atlas/shared-scheme-pairs.candidate.pack.json", "candidate"),
        ("assets/electric/ermak/atlas/future.research.pack.json.gz", "research"),
    )
    for filename, marker in fixtures:
        with io.BytesIO() as data:
            with zipfile.ZipFile(data, "w") as archive:
                archive.writestr(filename, "{}")
            data.seek(0)
            with zipfile.ZipFile(data) as archive:
                try:
                    check_apk(archive)
                except AssertionError as e:
                    need(marker in str(e), "wrong APK rejection reason: " + filename)
                    rejected += 1
                else:
                    raise AssertionError("APK candidate/research leak escaped: " + filename)
    for missing in ("*.candidate.*", "*.research.*"):
        build = (ROOT / "app-shell/build.gradle.kts").read_text(encoding="utf-8")
        try:
            check_gradle(build.replace(":" + missing, ""))
        except AssertionError:
            rejected += 1
        else:
            raise AssertionError("missing broad asset exclusion escaped: " + missing)
    return rejected


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--negative", action="store_true")
    parser.add_argument("--apk", type=Path)
    args = parser.parse_args()
    result = audit()
    if args.negative:
        result["rejectedMutations"] = negative()
    if args.apk:
        need(args.apk.is_file(), "APK not built: " + str(args.apk))
        with zipfile.ZipFile(args.apk) as archive:
            check_apk(archive)
        result["apkResearchAssetsExcluded"] = True
    print("STAGE50_RUNTIME_BOUNDARY " + json.dumps(result, ensure_ascii=False))
