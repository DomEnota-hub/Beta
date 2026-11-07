#!/usr/bin/env python3
"""Export read-only research data into human-readable JSON for review."""
import argparse
import json
from pathlib import Path
from validate_stage5_research import PATTERNS, load

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output-dir",required=True)
    args=parser.parse_args()
    out=Path(args.output_dir)
    out.mkdir(parents=True,exist_ok=True)
    for path in PATTERNS:
        target=out/Path(path).name.removesuffix(".gz")
        target.write_text(json.dumps(load(path),ensure_ascii=False,indent=2)+"\n",
                          encoding="utf-8")
        print(target)

if __name__ == "__main__":
    main()
