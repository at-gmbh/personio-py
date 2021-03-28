from personio_py.search import SearchIndex
from tests.apitest_shared import personio, skip_if_no_auth


@skip_if_no_auth
def test_search_index():
    index = SearchIndex(personio)
    # search for the most frequent names in Germany
    result = index.search("Müller Schmidt Schneider")
    assert len(result) > 0
    assert index.valid
    assert index.index
    assert index.last_update > 0
