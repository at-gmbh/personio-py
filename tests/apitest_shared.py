import os
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

# This is used to ensure the test check for existing objects
test_employee = personio.get_employees()[0]
shared_test_data = {
    'test_employee': {
        'id': test_employee.id_,
        'first_name': test_employee.first_name,
        'last_name': test_employee.last_name,
        'email': test_employee.email,
        'hire_date': test_employee.hire_date
    }
}
