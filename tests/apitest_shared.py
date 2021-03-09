import os
from functools import lru_cache
from datetime import date

import pytest

from personio_py import Personio, PersonioError

# Test time. if used on a personio instance, only touch entries during this time range
NOT_BEFORE = date(year=2022, month=1, day=1)
NOT_AFTER = date(year=2022, month=12, day=31)

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
