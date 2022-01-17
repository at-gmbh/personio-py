from tests.connection import get_skipif, get_test_employee, personio

skip_if_no_auth = get_skipif()


@skip_if_no_auth
def test_get_attendances():
    employee = get_test_employee()
    attendances = personio.get_attendances(employee)
    assert attendances
