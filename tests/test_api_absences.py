from .apitest_shared import *
from datetime import timedelta, date

from personio_py import Employee, ShortEmployee, Personio, PersonioError, Absence, AbsenceType


@skip_if_no_auth
@pytest.mark.parametrize("half_day_start", [True, False])
@pytest.mark.parametrize("half_day_end", [True, False])
def test_create_absences(half_day_start: bool, half_day_end: bool):
    """
    Test the creation of absence records on the server.
    """
    # Prepare data
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    start_date = date(2021, 1, 1)
    end_date = date(2021, 1, 10)

    # Ensure there are no left absences
    delete_all_absences_of_employee(test_user)

    # Start test
    absence_to_create = create_absence_for_user(test_user,
                                                start_date=start_date,
                                                end_date=end_date,
                                                half_day_start=half_day_start,
                                                half_day_end=half_day_end)
    assert absence_to_create.id_ is None
    absence_to_create.create(personio)
    assert absence_to_create.id_
    remote_absence = personio.get_absence(absence=absence_to_create)
    assert remote_absence.half_day_start is half_day_start
    assert remote_absence.half_day_end is half_day_end
    assert remote_absence.start_date - start_date < timedelta(seconds=1)
    assert remote_absence.end_date - end_date < timedelta(seconds=1)


@skip_if_no_auth
def test_get_absences_from_id():
    user = prepare_test_get_absences()
    absence_id = create_absence_for_user(user, create=True).id_
    absence = personio.get_absence(absence_id)
    assert absence.id_ == absence_id


@skip_if_no_auth
def test_get_absences_from_absence_object():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    absence = personio.get_absence(remote_absence)
    assert absence.id_ == remote_absence.id_


@skip_if_no_auth
def test_get_absences_from_absence_object_without_id_remote_query():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    absence_id = remote_absence.id_
    remote_absence.id_ = None
    absence = personio.get_absence(remote_absence, remote_query_id=True)
    assert absence.id_ == absence_id


@skip_if_no_auth
def test_get_absences_from_absence_object_without_id_no_remote_query():
    user = prepare_test_get_absences()
    remote_absence = create_absence_for_user(user, create=True)
    remote_absence.id_ = None
    with pytest.raises(ValueError):
        personio.get_absence(remote_absence, remote_query_id=False)


@skip_if_no_auth
def test_delete_absences_from_model_no_client():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    with pytest.raises(PersonioError):
        absence.delete()


@skip_if_no_auth
def test_delete_absences_from_model_passed_client():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    assert absence.delete(client=personio) is True


@skip_if_no_auth
def test_delete_absences_from_model_with_client():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence._client = personio
    assert absence.delete() is True


@skip_if_no_auth
def test_delete_absence_from_absence_id():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    assert personio.delete_absence(absence.id_) is True


@skip_if_no_auth
def test_delete_absences_from_client_object_with_id():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    assert personio.delete_absence(absence) is True


@skip_if_no_auth
def test_delete_absences_from_client_object_with_no_id_query():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence.id_ = None
    assert personio.delete_absence(absence, remote_query_id=True) is True


@skip_if_no_auth
def test_delete_absences_from_client_object_with_no_id_no_query():
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])
    delete_all_absences_of_employee(test_user)
    absence = create_absence_for_user(test_user, create=True)
    absence.id_ = None
    with pytest.raises(ValueError):
        personio.delete_absence(absence, remote_query_id=False)


def delete_absences(client: Personio, absences: [int] or [Absence]):
    for absence in absences:
        client.delete_absence(absence)


def create_absences(client: Personio, absences: [Absence]):
    for absence in absences:
        client.create_absence(absence)


def delete_all_absences_of_employee(employee: Employee):
    absences = personio.get_absences(employee)
    delete_absences(personio, absences)


def create_absence_for_user(employee: Employee,
                            time_off_type: AbsenceType = None,
                            start_date: date = None,
                            end_date: date = None,
                            half_day_start: bool = False,
                            half_day_end: bool = False,
                            comment: str = None,
                            create: bool = False) -> Absence:
    if not time_off_type:
        absence_types = personio.get_absence_types()
        time_off_type = [absence_type for absence_type in absence_types if absence_type.name == "Unpaid vacation"][0]
    if not start_date:
        start_date = date(2021, 1, 1)
    if not end_date:
        end_date = date(2021, 1, 10)

    absence_to_create = Absence(
        start_date=start_date,
        end_date=end_date,
        time_off_type=time_off_type,
        employee=employee,
        half_day_start=half_day_start,
        half_day_end=half_day_end,
        comment=comment
    )
    if create:
        absence_to_create.create(personio)
    return absence_to_create


def prepare_test_get_absences() -> Employee:
    test_data = shared_test_data['test_employee']
    test_user = personio.get_employee(test_data['id'])

    # Be sure there are no leftover absences
    delete_all_absences_of_employee(test_user)
    return test_user

