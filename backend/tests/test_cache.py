import time
import pytest
from app.services.cache import SQLiteCache


@pytest.fixture
def cache(tmp_path):
    db_path = str(tmp_path / "test_cache.db")
    return SQLiteCache(db_path=db_path, ttl_seconds=10)


class TestSQLiteCache:
    def test_set_and_get(self, cache):
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self, cache):
        assert cache.get("nonexistent") is None

    def test_set_with_dict_value(self, cache):
        data = {"foo": "bar", "num": 42}
        cache.set("dict_key", data)
        assert cache.get("dict_key") == data

    def test_set_with_list_value(self, cache):
        data = [1, 2, 3, {"nested": True}]
        cache.set("list_key", data)
        assert cache.get("list_key") == data

    def test_ttl_expiry(self, cache):
        cache.set("expire_key", "value", ttl=0)
        time.sleep(0.1)
        assert cache.get("expire_key") is None

    def test_delete(self, cache):
        cache.set("del_key", "value")
        cache.delete("del_key")
        assert cache.get("del_key") is None

    def test_clear(self, cache):
        cache.set("a", 1)
        cache.set("b", 2)
        cache.clear()
        assert cache.get("a") is None
        assert cache.get("b") is None

    def test_overwrite(self, cache):
        cache.set("key", "old")
        cache.set("key", "new")
        assert cache.get("key") == "new"
