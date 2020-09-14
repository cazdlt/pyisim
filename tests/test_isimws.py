from isimws.exceptions import NotFoundError
import pytest
import time
import random
from isimws import search
from isimws.auth import Session
from isimws.entities import Person, ProvisioningPolicy, StaticRole
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
    print(r)


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
    s = Session(test_url, admin_login, admin_pw, cert)
    s.soapclient.login(admin_login, admin_pw)
    s.soapclient.login(admin_login, admin_pw)

def test_inicializar_politicas(sesion):

    entitlements={
        "Directorio Activo":{
            "auto":False,
            "ergroup":{
                "enforcement":"Default",
                "values":"return 'test';"
            }
        },
        "*":{
            "auto":False
        }
    }
    policy={
        "description":"test",
        "name":"test",
        "ou_name":test_org,
        "priority":100,
        "memberships":["Auditor"],
        "entitlements":entitlements
    }
    pp=****(sesion,policy_attrs=policy)

    print(pp)

    policy={
        "description":"test",
        "name":"test",
        "ou_name":test_org,
        "priority":100,
        "memberships":"*",
        "entitlements":{
            "Directorio Activo":{
                "auto":False
            },
        }
    }
    pp=****(sesion,policy_attrs=policy)
    print(pp)
    
def test_search_provisioning_policy(sesion):

    r = search.provisioning_policy(sesion, "ITIM Global",test_org)
    print(r)
    assert len(r) > 0

def test_crear_modificar_eliminar_politica(sesion):

    #crear
    name=f"test{random.randint(0,999999)}"
    policy={
        "description":"test",
        "name":name,
        "ou_name":test_org,
        "priority":100,
        "memberships":"*",
        "entitlements":{
            "Directorio Activo":{
                "auto":False
            },
        }
    }
    pp=****(sesion,policy_attrs=policy)
    pp.crear(sesion)
    
    #buscar pol creada
    time.sleep(3)
    pp_creada=search.provisioning_policy(sesion,name,test_org)[0]
    assert pp_creada.name==name

    #modificar y validar modificacion
    nueva_desc="modificacion"
    pp_creada.description=nueva_desc
    pp_creada.modificar(sesion)
    time.sleep(3)
    pp_mod=search.provisioning_policy(sesion,name,test_org)[0]
    assert pp_mod.description==nueva_desc

    #eliminar y validar eliminación
    time.sleep(120) #tiene que terminar de evaluar la creación/mod
    pp_mod.eliminar(sesion)
    time.sleep(10)
    pp_elim=search.provisioning_policy(sesion,name,test_org)
    assert len(pp_elim)==0

def test_search_groups(sesion):
    #TODO Search by account/access
    #by service
    service_dn=search.service(sesion,test_org,filter="Directorio Activo")[0].dn
    r=search.groups(sesion,by="service",service_dn=service_dn,group_info="Administrators")
    print(r)