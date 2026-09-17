#!/usr/bin/env python3
from pathlib import Path
import re,sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.')
p=root/'app/build.gradle.kts'
s=p.read_text(encoding='utf-8')
s,n=re.subn(r'versionName\s*=\s*"[^"]+"','versionName = "1.2.2-beta-restored"',s,count=1)
if n!=1: raise SystemExit('versionName not found exactly once')
p.write_text(s,encoding='utf-8')
print('Final Beta versionName: 1.2.2-beta-restored')
