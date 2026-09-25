#!/usr/bin/env python3
import base64
import re
import subprocess
import zlib

BASE = "ce621e8fdc5a26af8670a056558b2e7d3bfc386a"
PATH = ".github/scripts/apply_diagnostic_foundation.py"
subprocess.run(["git", "fetch", "origin", BASE, "--depth=1"], check=True, stdout=subprocess.DEVNULL)
old_runner = subprocess.check_output(["git", "show", f"{BASE}:{PATH}"], text=True)
match = re.search(r"b64decode\('([^']+)'\)", old_runner)
if not match:
    raise RuntimeError("Original diagnostic foundation payload not found")
source = zlib.decompress(base64.b64decode(match.group(1))).decode("utf-8")
source = source.replace(
    'TechnicalAssetReader.readJsonObject(appContext, "technical/ermak_diagnostics.json")',
    'TechnicalAssetReader.readTechnicalJson(appContext, "ermak_diagnostics.json")',
)
source = source.replace(
    'Text(policyDecision.message.ifBlank {',
    'Text(policyDecision?.message.orEmpty().ifBlank {',
)
if 'readJsonObject(appContext, "technical/ermak_diagnostics.json")' in source:
    raise RuntimeError("Loader API replacement failed")
exec(compile(source, __file__, "exec"))
