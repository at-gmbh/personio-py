import os
from functools import lru_cache

import pytest

from personio_py import Employee, Personio, PersonioError

# Personio client authentication
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
personio = Personio(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


@lru_cache(maxsize=1)
def get_skipif():
    return pytest.mark.skipif(not can_authenticate(), reason="Personio authentication failed")


def can_authenticate() -> bool:
    try:
        personio.authenticate()
        return True
    except PersonioError:
        return False


@lru_cache(maxsize=1)
def get_test_employee() -> Employee:
    alan = personio.search_first("Alan Turing")
    if alan:
        return alan
    else:
        return personio.get_employees()[0]
