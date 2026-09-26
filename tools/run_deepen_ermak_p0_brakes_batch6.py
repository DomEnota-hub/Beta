#!/usr/bin/env python3
"""Apply batch6 with explicit route-back links for symptoms outside the selected brake scenario."""
from deepen_ermak_p0_brakes_batch6 import ROUTES, main


def point_finding(route_id: str, node_id: str, next_id: str) -> None:
    for node in ROUTES[route_id]["nodes"]:
        if node.get("id") == node_id:
            node["nextNodeId"] = next_id
            return
    raise SystemExit(f"missing node {route_id}:{node_id}")


# These findings explicitly establish that the observed symptom belongs to a
# different route. Keeping this explicit also makes the route-back terminal
# reachable and prevents dead graph nodes.
point_finding("ER-DIAG-082", "common", "not-this-scenario")
point_finding("ER-DIAG-083", "mechanical", "not-this-scenario")
point_finding("ER-DIAG-084", "indication", "not-this-scenario")

if __name__ == "__main__":
    main()
