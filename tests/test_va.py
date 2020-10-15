from pyisim.va.configure import update_property
from pyisim.va.auth import VASession
import pytest
from secret import va_login, va_pw, va_url


@pytest.fixture
def session():
    s = VASession(va_login, va_pw, va_url, None)
    return s


def test_list_property_files(session):
    out = update_property.list_files(session)
    assert isinstance(out, list)
    assert len(out) > 0


def test_get_property_value(session):
    property_file = "scriptframework.properties"
    not_found = update_property.get_property_value(session, property_file, "XX")
    assert not_found["result"] == "property_not_found"

    one = update_property.get_property_value(
        session, property_file, "ITIM.java.access.util"
    )
    assert one["PropertyName"] == "ITIM.java.access.util"

    multi = update_property.get_property_value(session, property_file)
    assert isinstance(multi, list)
    assert len(multi) > 0


def test_add_property(session):
    property_file = "CustomLabels.properties"
    property_name = "test"
    property_value = "test"
    r = update_property.add_property(
        session, property_file, property_name, property_value
    )
    assert r["result"] == "property_already_exist"


def test_update_property(session):
    property_file = "CustomLabels.properties"
    property_name = "test"
    property_value = "test"

    old_val = update_property.get_property_value(session, property_file, property_name)[
        "PropertyValue"
    ]
    if property_value == old_val:
        property_value += "X"

    r = update_property.update_property(
        session, property_file, property_name, property_value
    )
    assert r == "OK"

    new_val = update_property.get_property_value(session, property_file, property_name)[
        "PropertyValue"
    ]
    assert new_val == property_value

    r = update_property.update_property(session, property_file, property_name, old_val)
    assert r == "OK"


def test_delete_property(session):
    property_file = "CustomLabels.properties"
    property_name = "test"
    r = update_property.delete_property(session, property_file, property_name)
    print(r)
