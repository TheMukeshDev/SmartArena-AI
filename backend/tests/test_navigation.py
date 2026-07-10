"""Tests for app.services.navigation — find_path and get_navigation_context."""

from app.services.navigation import find_path, get_navigation_context, ZONE_ADJACENCY


class TestFindPath:
    def test_direct_adjacency(self):
        path = find_path("North Stand", "West Stand")
        assert path == ["North Stand", "West Stand"]

    def test_multi_hop(self):
        path = find_path("Gate C", "West Stand")
        assert path[0] == "Gate C"
        assert path[-1] == "West Stand"
        assert len(path) > 2

    def test_same_start_end(self):
        path = find_path("North Stand", "North Stand")
        assert path == ["North Stand"]

    def test_unreachable_zone(self):
        path = find_path("North Stand", "Nonexistent Zone")
        assert path == []

    def test_invalid_start_zone(self):
        path = find_path("Invalid Zone", "North Stand")
        assert path == []

    def test_invalid_end_zone(self):
        path = find_path("North Stand", "Invalid Zone")
        assert path == []

    def test_bidirectional(self):
        path_ab = find_path("North Stand", "South Stand")
        path_ba = find_path("South Stand", "North Stand")
        assert path_ab[0] == "North Stand"
        assert path_ab[-1] == "South Stand"
        assert path_ba[0] == "South Stand"
        assert path_ba[-1] == "North Stand"


class TestGetNavigationContext:
    def test_no_current_zone(self):
        ctx = get_navigation_context()
        assert "zones" in ctx
        assert "adjacency" in ctx
        assert "current_zone" not in ctx
        assert len(ctx["zones"]) == len(ZONE_ADJACENCY)

    def test_with_current_zone(self):
        ctx = get_navigation_context("North Stand")
        assert ctx["current_zone"] == "North Stand"
        assert ctx["reachable_zones"] == ZONE_ADJACENCY["North Stand"]
