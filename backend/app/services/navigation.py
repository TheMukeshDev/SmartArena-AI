"""Navigation services for the SmartArena AI system.

Provides BFS-based shortest-path computation between stadium zones,
with optional support for accessibility-aware routing.
"""

from collections import deque
from collections.abc import Callable

ZONE_ADJACENCY: dict[str, list[str]] = {
    "North Stand": ["West Stand", "East Stand", "Gate A", "Gate B", "Concourse North"],
    "South Stand": ["West Stand", "East Stand", "Gate C", "Gate D", "Concourse South"],
    "West Stand": ["North Stand", "South Stand", "Gate A", "Gate D", "VIP Lounge"],
    "East Stand": ["North Stand", "South Stand", "Gate B", "Gate C", "Food Court East"],
    "Gate A": ["North Stand", "West Stand", "Parking Lot A"],
    "Gate B": ["North Stand", "East Stand", "Parking Lot B"],
    "Gate C": ["South Stand", "East Stand", "Transit Hub"],
    "Gate D": ["South Stand", "West Stand", "Rideshare Drop-off"],
    "Concourse North": ["North Stand", "Food Court North"],
    "Concourse South": ["South Stand", "Food Court South"],
    "VIP Lounge": ["West Stand"],
    "Food Court East": ["East Stand"],
    "Food Court North": ["Concourse North"],
    "Food Court South": ["Concourse South"],
    "Parking Lot A": ["Gate A"],
    "Parking Lot B": ["Gate B"],
    "Transit Hub": ["Gate C"],
    "Rideshare Drop-off": ["Gate D"],
}

ACCESSIBLE_EDGES: set[tuple[str, str]] = {
    ("North Stand", "West Stand"),
    ("North Stand", "East Stand"),
    ("North Stand", "Gate A"),
    ("North Stand", "Gate B"),
    ("North Stand", "Concourse North"),
    ("South Stand", "West Stand"),
    ("South Stand", "East Stand"),
    ("South Stand", "Gate C"),
    ("South Stand", "Gate D"),
    ("South Stand", "Concourse South"),
    ("West Stand", "North Stand"),
    ("West Stand", "South Stand"),
    ("West Stand", "Gate A"),
    ("West Stand", "Gate D"),
    ("West Stand", "VIP Lounge"),
    ("East Stand", "North Stand"),
    ("East Stand", "South Stand"),
    ("East Stand", "Gate B"),
    ("East Stand", "Gate C"),
    ("East Stand", "Food Court East"),
    ("Gate A", "North Stand"),
    ("Gate A", "West Stand"),
    ("Gate A", "Parking Lot A"),
    ("Gate B", "North Stand"),
    ("Gate B", "East Stand"),
    ("Gate B", "Parking Lot B"),
    ("Gate C", "South Stand"),
    ("Gate C", "East Stand"),
    ("Gate C", "Transit Hub"),
    ("Gate D", "South Stand"),
    ("Gate D", "West Stand"),
    ("Gate D", "Rideshare Drop-off"),
    ("Concourse North", "North Stand"),
    ("Concourse North", "Food Court North"),
    ("Concourse South", "South Stand"),
    ("Concourse South", "Food Court South"),
    ("VIP Lounge", "West Stand"),
    ("Food Court East", "East Stand"),
    ("Food Court North", "Concourse North"),
    ("Food Court South", "Concourse South"),
    ("Parking Lot A", "Gate A"),
    ("Parking Lot B", "Gate B"),
    ("Transit Hub", "Gate C"),
    ("Rideshare Drop-off", "Gate D"),
}

SENSORY_FRIENDLY_ZONES: set[str] = {"VIP Lounge", "Food Court East"}


def _bfs(
    start: str, end: str, edge_filter: Callable[[str, str], bool] | None = None
) -> list[str]:
    """Run a breadth-first search from *start* to *end* in the zone graph.

    When *edge_filter* is supplied it is called as ``edge_filter(node, neighbor)``
    for each candidate edge; the edge is skipped when the callable returns
    ``False``.

    Returns the shortest path as a list of zone names, or an empty list when
    no path exists.
    """
    if start not in ZONE_ADJACENCY or end not in ZONE_ADJACENCY:
        return []
    if start == end:
        return [start]

    visited = {start}
    queue: deque[list[str]] = deque([[start]])

    while queue:
        path = queue.popleft()
        node = path[-1]

        for neighbor in ZONE_ADJACENCY.get(node, []):
            if edge_filter is not None and not edge_filter(node, neighbor):
                continue
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])

    return []


def find_path(start: str, end: str) -> list[str]:
    """Find the shortest path between *start* and *end* using all available edges.

    Returns the path as a list of zone names, or an empty list if either zone
    is unknown or no route exists.
    """
    return _bfs(start, end)


def find_accessible_path(start: str, end: str) -> list[str]:
    """Find the shortest accessible path between two zones.

    Only edges listed in ``ACCESSIBLE_EDGES`` are traversed.  Returns the path
    as a list of zone names, or an empty list when no accessible route exists.
    """
    return _bfs(start, end, lambda n, nb: (n, nb) in ACCESSIBLE_EDGES)


def get_navigation_context(current_zone: str | None = None) -> dict:
    """Return a dictionary of navigation-related data for the frontend.

    When *current_zone* is provided the result also includes that zone and its
    immediate neighbours.
    """
    context: dict = {
        "zones": list(ZONE_ADJACENCY.keys()),
        "adjacency": ZONE_ADJACENCY,
        "sensory_friendly_zones": list(SENSORY_FRIENDLY_ZONES),
    }
    if current_zone:
        context["current_zone"] = current_zone
        context["reachable_zones"] = ZONE_ADJACENCY.get(current_zone, [])
    return context
