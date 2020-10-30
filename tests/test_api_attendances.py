from .apitest_shared import *


@skip_if_no_auth
def test_create_attendances():
    attendances = personio.get_attendances(2007207)
    assert len(attendances) > 0


@skip_if_no_auth
def test_get_attendances():
    attendances = personio.get_attendances(2007207)
    assert len(attendances) > 0
