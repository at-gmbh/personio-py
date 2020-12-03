import os
from functools import lru_cache

import pytest

from personio_py import Personio, PersonioError

# Personio client authentication
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
personio = Personio(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

# deactivate all tests that rely on a specific personio instance
try:
    personio.authenticate()
    can_authenticate = True
except PersonioError:
    can_authenticate = False
skip_if_no_auth = pytest.mark.skipif(not can_authenticate, reason="Personio authentication failed")


@lru_cache(maxsize=1)
def get_test_employee():
    return personio.get_employees()[0]
