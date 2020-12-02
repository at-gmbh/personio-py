import os
import pytest

from functools import lru_cache

from personio_py import Personio, PersonioError

# Personio client authentication
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
personio = Personio(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)


#@lru_cache
def get_test_employee():
    return personio.get_employees()[0]


# deactivate all tests that rely on a specific personio instance
try:
    personio.authenticate()
    can_authenticate = True
    # This is used to ensure the test check for existing objects
except PersonioError:
    can_authenticate = False
skip_if_no_auth = pytest.mark.skipif(not can_authenticate, reason="Personio authentication failed")


