#!/usr/bin/env python3
"""Stage 13: inspect the *built APK*, not only source-tree publication flags.

All family pack files remain candidate/unknown at this checkpoint. A filename
ending in .pack.json does not imply publication. Fail if any family or research
material leaks into APK assets, even if UI currently hides the content.
"""
from pathlib import Path
from zipfile import ZipFile
import sys

apk_dir = Path("app-shell/build/outputs/apk/debug")
apks = sorted(apk_dir.glob("*.apk"))
if len(apks) != 1:
    raise SystemExit(f"Expected exactly one Debug APK in {apk_dir}, got {apks!r}")

quarantined_roots = (
    "assets/electric/ermak/",
    "assets/diesel/chme3-family/",
    "assets/diesel/tem2-family/",
    "assets/locomotive-migration/",
)
quarantined_components = {"migration", "authoring"}
quarantined_suffixes = (".candidate.", ".research.")

with ZipFile(apks[0]) as apk:
    paths = [name for name in apk.namelist() if name.startswith("assets/")]
    leaks = []
    for name in paths:
        lower = name.lower()
        components = set(lower.split("/"))
        if (
            lower.startswith(quarantined_roots)
            or components & quarantined_components
            or any(suffix in lower for suffix in quarantined_suffixes)
        ):
            leaks.append(name)

    # Regression guard: this must not accidentally strip the VL80S published runtime.
    required = "assets/electric/vl80s/runtime-index.json"
    if required not in paths:
        raise SystemExit(f"Published VL80S runtime missing from APK: {required}")
    if leaks:
        print("UNPUBLISHED_ASSET_LEAK:", *leaks[:100], sep="\n", file=sys.stderr)
        raise SystemExit(f"Stage 13 quarantine failed: {len(leaks)} forbidden APK assets")
    print(f"STAGE13_APK_QUARANTINE_PASS {apks[0].name} assets={len(paths)}")
