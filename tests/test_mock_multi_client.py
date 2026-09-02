"""
Regression tests for multi-client usage.

The previous implementation used a global client singleton (``g.client``) and reassigned the
module-level ``Employee`` class (plus a ``sys.modules`` patch) whenever a client was created.
That made it impossible to use two clients with different custom attributes at the same time:
the last client to be created would win. These tests make sure the de-globalized implementation
keeps clients fully independent.
"""

import pytest

from personio_py import CustomAttribute, Personio, PersonioError
from personio_py.models import Absence, BaseEmployee


def _client_with_attributes(client_id, attributes):
    """Create a Personio client whose custom attributes are stubbed (no API call required)."""
    client = Personio(client_id=client_id, client_secret="secret")
    client.authenticated = True
    client.get_custom_attributes = lambda: attributes
    return client


def test_multiple_clients_have_independent_employee_classes():
    client_a = _client_with_attributes(
        "multi_company_a",
        [
            CustomAttribute(key="dynamic_1", label="Phone (office)", type="standard"),
            CustomAttribute(key="dynamic_2", label="Skills", type="tags"),
        ],
    )
    client_b = _client_with_attributes(
        "multi_company_b",
        [CustomAttribute(key="dynamic_9", label="Cost Center Code", type="integer")],
    )

    employee_cls_a = client_a.employee_class
    employee_cls_b = client_b.employee_class

    # the two accounts produce independent Employee classes
    assert employee_cls_a is not employee_cls_b
    assert issubclass(employee_cls_a, BaseEmployee)
    assert issubclass(employee_cls_b, BaseEmployee)

    # each class only knows its own custom attributes
    assert employee_cls_a._custom_attribute_keys == ["dynamic_1", "dynamic_2"]
    assert employee_cls_b._custom_attribute_keys == ["dynamic_9"]

    # the shared base class stays unpolluted (the old global-singleton design could not do this)
    assert BaseEmployee._custom_attribute_keys == []

    # instances carry their own custom attributes (via auto-generated aliases) ...
    ada = employee_cls_a(id=1, first_name="Ada")
    ada.phone_office = "12345"
    assert ada.dynamic_1 == "12345"

    alan = employee_cls_b(id=2, first_name="Alan")
    alan.cost_center_code = 42
    assert alan.dynamic_9 == 42

    # ... and the accounts' attributes do not leak into each other
    assert not hasattr(alan, "phone_office")
    assert not hasattr(ada, "cost_center_code")


def test_same_account_clients_share_one_employee_class():
    attrs = [CustomAttribute(key="dynamic_1", label="Phone (office)", type="standard")]
    client_1 = _client_with_attributes("multi_shared_account", attrs)
    client_2 = _client_with_attributes("multi_shared_account", attrs)
    # two clients for the SAME account (client_id) share a single Employee class, so that their
    # employees compare equal
    assert client_1.employee_class is client_2.employee_class
    employee_1 = client_1.employee_class(id=1, first_name="Ada")
    employee_2 = client_2.employee_class(id=1, first_name="Ada")
    assert employee_1 == employee_2


def test_convenience_method_on_unbound_object_raises():
    # an object that was not returned by a client is not bound and cannot make API calls
    absence = Absence(id=123)
    with pytest.raises(PersonioError, match="not bound to a Personio client"):
        absence.delete()
