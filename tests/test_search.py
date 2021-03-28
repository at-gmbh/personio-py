from personio_py.search import SearchCache
from tests.apitest_shared import personio, skip_if_no_auth


@skip_if_no_auth
def test_search_cache():
    cache = SearchCache(personio)
    # search for the most frequent names in Germany
    result = cache.search("Müller Schmidt Schneider")
    assert len(result) > 0
    assert cache.valid
    assert cache.index
    assert cache.last_update > 0
