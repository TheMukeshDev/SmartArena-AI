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

ACCESSIBLE_EDGES: dict[tuple[str, str], bool] = {
    ("North Stand", "West Stand"): True,
    ("North Stand", "East Stand"): True,
    ("North Stand", "Gate A"): True,
    ("North Stand", "Gate B"): True,
    ("North Stand", "Concourse North"): True,
    ("South Stand", "West Stand"): True,
    ("South Stand", "East Stand"): True,
    ("South Stand", "Gate C"): True,
    ("South Stand", "Gate D"): True,
    ("South Stand", "Concourse South"): True,
    ("West Stand", "North Stand"): True,
    ("West Stand", "South Stand"): True,
    ("West Stand", "Gate A"): True,
    ("West Stand", "Gate D"): True,
    ("West Stand", "VIP Lounge"): True,
    ("East Stand", "North Stand"): True,
    ("East Stand", "South Stand"): True,
    ("East Stand", "Gate B"): True,
    ("East Stand", "Gate C"): True,
    ("East Stand", "Food Court East"): True,
    ("Gate A", "North Stand"): True,
    ("Gate A", "West Stand"): True,
    ("Gate A", "Parking Lot A"): True,
    ("Gate B", "North Stand"): True,
    ("Gate B", "East Stand"): True,
    ("Gate B", "Parking Lot B"): True,
    ("Gate C", "South Stand"): True,
    ("Gate C", "East Stand"): True,
    ("Gate C", "Transit Hub"): True,
    ("Gate D", "South Stand"): True,
    ("Gate D", "West Stand"): True,
    ("Gate D", "Rideshare Drop-off"): True,
    ("Concourse North", "North Stand"): True,
    ("Concourse North", "Food Court North"): True,
    ("Concourse South", "South Stand"): True,
    ("Concourse South", "Food Court South"): True,
    ("VIP Lounge", "West Stand"): True,
    ("Food Court East", "East Stand"): True,
    ("Food Court North", "Concourse North"): True,
    ("Food Court South", "Concourse South"): True,
    ("Parking Lot A", "Gate A"): True,
    ("Parking Lot B", "Gate B"): True,
    ("Transit Hub", "Gate C"): True,
    ("Rideshare Drop-off", "Gate D"): True,
}

SENSORY_FRIENDLY_ZONES: set[str] = {"VIP Lounge", "Food Court East"}


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
        "sensory_friendly_zones": list(SENSORY_FRIENDLY_ZONES),
    }
    if current_zone:
        context["current_zone"] = current_zone
        context["reachable_zones"] = ZONE_ADJACENCY.get(current_zone, [])
    return context


def find_accessible_path(start: str, end: str) -> list[str]:
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
            edge = (node, neighbor)
            if not ACCESSIBLE_EDGES.get(edge, False):
                continue
            if neighbor == end:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(path + [neighbor])
    return []
