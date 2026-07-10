ZONE_ADJACENCY = {
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


def find_path(start: str, end: str) -> list[str]:
    if start not in ZONE_ADJACENCY or end not in ZONE_ADJACENCY:
        return []
    if start == end:
        return [start]

    visited = {start}
    queue = [[start]]
    while queue:
        path = queue.pop(0)
        node = path[-1]
        for neighbor in ZONE_ADJACENCY.get(node, []):
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []


def get_navigation_context(current_zone: str | None = None) -> dict:
    context = {
        "zones": list(ZONE_ADJACENCY.keys()),
        "adjacency": ZONE_ADJACENCY,
    }
    if current_zone:
        context["current_zone"] = current_zone
        context["reachable_zones"] = ZONE_ADJACENCY.get(current_zone, [])
    return context
