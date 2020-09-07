from isimws.exceptions import NotFoundError
import pytest

from isimws import search
from isimws.auth import Session
from isimws.entities import Person, StaticRole
from secret import admin_login, admin_pw, cert, env, test_url, test_org


@pytest.fixture
def sesion():
    return Session(test_url, admin_login, admin_pw, cert)


def test_search_access(sesion):
    r = search.access(sesion, filter="*Consulta*", limit=2)
    assert len(r) > 0


def test_search_people(sesion):
    r = search.people(sesion, Person, "employeenumber", "96451425873", limit=1)
    assert len(r) > 0


def test_search_service(sesion):
    r = search.service(sesion, test_org, filter="SAP NW")
    assert len(r) > 0
    assert r[0].name == "SAP NW"


def test_search_roles(sesion):
    r = search.roles(sesion, filter="SAP*")

    assert len(r) > 0
    assert "SAP" in r[0].name.upper()
    assert "ou=****[0].dn


def test_new_rol(sesion):
    rol = {
        "name": "rol_prueba",
        "description": "rol_prueba",
        "ou": test_org,
        "classification": "Empresarial",
        "access_option": 2,
        "access_category": "Role",
        "owner_roles": None,
        "owner_cedulas": ["1015463230"],
    }
    r = StaticRole(sesion, role_attrs=rol)


def test_lookup_rol(sesion):
    dn = f"erglobalid=00000000000000000001,ou=****,erglobalid=00000000000000000000,ou={test_org},dc={test_org}"
    r = StaticRole(sesion, dn=dn)
    assert r.name == "ITIM Administrators"

    dn = "not found"
    try:
        r = StaticRole(sesion, dn=dn)
    except NotFoundError:
        assert True


def test_crear_modificar_eliminar_rol(sesion):

    # creación
    rolinfo = {
        "name": "rol_prueba",
        "description": "rol_prueba",
        "ou": test_org,
        "classification": "Empresarial",
        "access_option": 2,
        "access_category": "Role",
        "owner_roles": None,
        "owner_cedulas": ["1015463230"],
    }
    rol = StaticRole(sesion, role_attrs=rolinfo)
    rol.crear(sesion)
    assert hasattr(rol, "dn")

    # mod
    rol.name = "rol_prueba_mod"
    rol.modificar(sesion)
    assert (
        StaticRole(sesion, dn=rol.dn).name == rol.name
    )  # busca el rol en sim y lo compara con el nuevo

    # del
    rol.eliminar(sesion)
    try:
        r = StaticRole(sesion, dn=rol.dn)
    except NotFoundError:
        assert True
    else:
        assert False

def test_get_client():
    s=Session(test_url, admin_login, admin_pw, cert)
    s.soapclient.login(admin_login, admin_pw)
    s.soapclient.login(admin_login, admin_pw)
