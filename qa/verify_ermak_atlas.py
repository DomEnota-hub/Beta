#!/usr/bin/env python3
import gzip
import json
import sys
from pathlib import Path


EXPECTED = {
    "ER-SCH-LAYOUT-2ES5K-BASE": 103,
    "ER-SCH-LAYOUT-3ES5K-HEAD": 103,
    "ER-SCH-LAYOUT-3ES5K-BOOSTER": 81,
}


def main() -> int:
    assets = Path(sys.argv[1] if len(sys.argv) > 1 else "app/src/main/assets")
    source = assets / "technical" / "ermak_schemes.json.gz"
    with gzip.open(source, "rt", encoding="utf-8") as stream:
        schemes = {item["id"]: item for item in json.load(stream)["schemes"]}

    for scheme_id, expected_count in EXPECTED.items():
        if scheme_id not in schemes:
            raise SystemExit(f"Missing Ermak atlas variant: {scheme_id}")
        hotspots = schemes[scheme_id].get("layers", {}).get("hotspotLayer", [])
        if len(hotspots) != expected_count:
            raise SystemExit(
                f"{scheme_id}: expected {expected_count} hotspots, got {len(hotspots)}"
            )
        for index, hotspot in enumerate(hotspots):
            layout = hotspot.get("layoutHint", {})
            if not hotspot.get("equipmentId") or not hotspot.get("label"):
                raise SystemExit(f"{scheme_id}[{index}]: missing equipmentId or label")
            if any(not isinstance(layout.get(key), int) for key in ("x", "y", "width", "height")):
                raise SystemExit(f"{scheme_id}[{index}]: invalid layout coordinates")
            if layout["x"] < 0 or layout["y"] < 0 or layout["width"] <= 0 or layout["height"] <= 0:
                raise SystemExit(f"{scheme_id}[{index}]: out-of-range layout rectangle")

    print("Ermak interactive atlas: 3 variants, 287 valid hotspots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
