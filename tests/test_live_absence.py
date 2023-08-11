from datetime import date
from functools import lru_cache
from typing import List

import pytest

from personio_py import Personio, PersonioError
from personio_py.models import Absence, AbsenceType, Employee, ShortEmployee
from tests import connection
from tests.connection import get_skipif, personio
from tests.test_live_employee import get_tim

skip_if_no_auth = get_skipif()


@skip_if_no_auth
def test_get_absence_types():
    absence_types = personio.get_absence_types()
    assert absence_types
    for at in absence_types:
        assert at.id
        assert at.name


@skip_if_no_auth
def test_get_absences():
    # get all absences
    employee = connection.get_test_employee()
    absences = personio.get_absences(employee.id)
    assert absences
    # get a single absence by ID
    absence_id = absences[0].id
    absence = personio.get_absence(absence_id)
    assert absence == absences[0]


@skip_if_no_auth
@pytest.mark.parametrize("half_day_start", [True, False])
@pytest.mark.parametrize("half_day_end", [True, False])
def test_create_absences(half_day_start: bool, half_day_end: bool):
    """
    Test the creation of absence records on the server.
    """
    # Prepare data
    test_user = get_test_employee()
    start_date = date(year=2022, month=1, day=1)
    end_date = date(year=2022, month=1, day=10)

    # Ensure there are no left absences
    delete_all_absences_of_employee(test_user)

    # Start test
    absence = create_absence_for_user(
        test_user, start_date=start_date, end_date=end_date,
        half_day_start=half_day_start, half_day_end=half_day_end)
    assert absence.id is None
    absence = absence.create()
    assert absence.id
    remote_absence = personio.get_absence(absence=absence)
    assert remote_absence.half_day_start is half_day_start
    assert remote_absence.half_day_end is half_day_end
    assert remote_absence == absence


@skip_if_no_auth
def test_get_absences_from_id():
    user = prepare_test_get_absences()
    absence_id = create_absence_for_user(user, create=True).id
    absence = personio.get_absence(absence_id)
    assert absence.id == absence_id


@skip_if_no_auth
def test_get_absences_from_absence_object():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    absence = personio.get_absence(remote_absence)
    assert absence.id == remote_absence.id


@skip_if_no_auth
def test_get_absences_from_absence_object_without_id():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    absence_id = remote_absence.id
    remote_absence.id = None
    absence = personio.get_absence(remote_absence)
    assert absence.id == absence_id


@skip_if_no_auth
def test_delete_absences_from_model():
    test_user = get_test_employee()
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence.delete()


@skip_if_no_auth
def test_delete_absence_from_absence_id():
    test_user = get_test_employee()
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    personio.delete_absence(absence.id)


@skip_if_no_auth
def test_delete_absences_from_client_object_with_id():
    test_user = get_test_employee()
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    personio.delete_absence(absence)


@skip_if_no_auth
def test_delete_absences_from_client_object_without_id():
    test_user = get_test_employee()
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence.id = None
    with pytest.raises(PersonioError):
        personio.delete_absence(absence)


def delete_absences(client: Personio, absences: List[int] or List[Absence]):
    for absence in absences:
        client.delete_absence(absence)


def create_absences(client: Personio, absences: List[Absence]):
    for absence in absences:
        client.create_absence(absence)


def delete_all_absences_of_employee(employee: Employee):
    absences = personio.get_absences(employee)
    delete_absences(personio, absences)


def create_absence_for_user(
        employee: Employee, time_off_type: AbsenceType = None, start_date: date = None,
        end_date: date = None, half_day_start: bool = False, half_day_end: bool = False,
        comment: str = None, create: bool = False) -> Absence:
    if not time_off_type:
        time_off_type = get_default_absence_type()
    if not start_date:
        start_date = date(year=2022, month=1, day=1)
    if not end_date:
        end_date = date(year=2022, month=1, day=10)
    absence = Absence(
        start_date=start_date,
        end_date=end_date,
        time_off_type=time_off_type,
        employee=employee,
        half_day_start=half_day_start,
        half_day_end=half_day_end,
        comment=comment
    )
    if create:
        absence.create()
    return absence


def prepare_test_get_absences() -> Employee:
    test_user = get_test_employee()
    # make sure there are no leftover absences
    delete_all_absences_of_employee(test_user)
    return test_user


@lru_cache(maxsize=1)
def get_test_employee():
    return get_tim()


@lru_cache(maxsize=1)
def get_default_absence_type():
    return personio.get_absence_types()[0]
