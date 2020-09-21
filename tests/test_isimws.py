from random import randint
from isimws.exceptions import NotFoundError
import pytest
import time
import random
from isimws import search
from isimws.auth import Session
from isimws.entities import Person, ProvisioningPolicy, StaticRole
from secret import (
    admin_login,
    admin_pw,
    cert,
    env,
    test_url,
    test_org,
    test_description,
    test_manager,
    test_dep,
)


@pytest.fixture
def sesion():
    return Session(test_url, admin_login, admin_pw, cert)


def test_search_access(sesion):
    r = search.access(sesion, filter="*Consulta*", limit=2)
    assert len(r) > 0


def test_search_people(sesion):
    r = search.people(sesion, "employeenumber", "96451425873", limit=1)
    assert len(r) > 0


def test_search_service(sesion):
    r = search.service(sesion, search.organizational_container(sesion,"organizations",test_org)[0], filter="SAP NW")
    assert len(r) > 0
    assert r[0].name == "SAP NW"


def test_search_roles(sesion):
    r = search.roles(sesion, filter="SAP*")

    assert len(r) > 0
    assert "SAP" in r[0].name.upper()
    assert "ou=roles" in r[0].dn


def test_new_rol(sesion):
    rol = {
        "name": "rol_prueba",
        "description": "rol_prueba",
        "parent": search.organizational_container(sesion,"organizations",test_org)[0],
        "classification": "Empresarial",
        "access_option": 2,
        "access_category": "Role",
        "owner_roles": None,
        "owner_cedulas": ["1015463230"],
    }
    r = StaticRole(sesion, role_attrs=rol)
    print(r)


def test_lookup_rol(sesion):
    dn = f"erglobalid=00000000000000000001,ou=roles,erglobalid=00000000000000000000,ou={test_org},dc={test_org}"
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
        "parent": search.organizational_container(sesion,"organizations",test_org)[0],
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

    parent=search.organizational_container(sesion,"organizations",test_org)[0]
    service=search.service(sesion,parent,filter="Directorio Activo")[0]

    entitlements = {
        service.dn: {
            "automatic": False,
            "workflow":None,
            "parameters":{
                "ergroup": [
                    {
                        "enforcement": "Default",
                        "type":"script",
                        "values": "return 'test';",
                    },
                    {
                        "enforcement": "Excluded",
                        "type":"null",
                    },
                    {
                        "enforcement": "Allowed",
                        "type":"constant",
                        "values": ["test1","test2"],
                    },
                    {
                        "enforcement": "Default",
                        "type":"Constant",
                        "values": ["test3"],
                    },
                    {
                        "enforcement": "MANDATORY",
                        "type":"REGEX",
                        "values": r"^[\s\w]+$",
                    },
                ],
                "eradfax": [{
                    "enforcement": "Allowed", 
                    "type":"constant",
                    "values": ["1018117"],
                }],
            }
        },
        "*": {
            "automatic": False,
            "workflow":None,
            "parameters":{}
        },
    }
    policy = {
        "description": "test",
        "name": "test",
        "parent": parent,
        "priority": 10000,
        "memberships": [x.dn for x in search.roles(sesion,filter="Auditor")],
        "enabled":False,
        "entitlements": entitlements,
    }
    pp = ProvisioningPolicy(sesion, policy_attrs=policy)
    print(pp.entitlements)
    print(pp)

    #modificar política
    policy = {
        "description": "test",
        "name": "test",
        "parent": parent,
        "priority": 100,
        "memberships": "*",
        "entitlements": {
            "ADprofile": {"automatic": False, "workflow":None, "parameters":{}},
        },
    }
    pp = ProvisioningPolicy(sesion, policy_attrs=policy)

    pp.entitlements["ADprofile"]["automatic"]=True
    print("")


    #buscar y modificar política
    pp = search.provisioning_policy(sesion, "Test TipoServicio", parent)[0]
    print(pp)

    pp.entitlements=entitlements
    pp.entitlements["*"]["automatic"]=True
    print("")



def test_search_provisioning_policy(sesion):

    r = search.provisioning_policy(sesion, "Test TipoServicio", search.organizational_container(sesion,"organizations",test_org)[0])
    print(r[0].entitlements)
    assert len(r) > 0


def test_crear_modificar_eliminar_politica(sesion):

    # crear
    name = f"test{random.randint(0,999999)}"
    parent=search.organizational_container(sesion,"organizations",test_org)[0]
    service=search.service(sesion,parent,filter="Directorio Activo")[0]

    entitlements = {
        service.dn: {
            "automatic": False,
            "workflow":None,
            "parameters":{
                "ercompany": [
                    {
                        "enforcement": "Default",
                        "type":"script",
                        "values": "return 'test';",
                    },
                    {
                        "enforcement": "Excluded",
                        "type":"null",
                    },
                    {
                        "enforcement": "Allowed",
                        "type":"constant",
                        "values": ["test1","test2"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type":"Constant",
                        "values": ["test3"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type":"REGEX",
                        "values": r"^[\s\w]+$",
                    },
                ],
                "eradfax": [{
                    "enforcement": "Allowed", 
                    "type":"constant",
                    "values": ["1018117"],
                }],
            }
        },
        "*": {
            "automatic": False,
            "workflow":None,
            "parameters":{}
        },
    }
    policy = {
        "description": "test",
        "name": name,
        "parent": parent,
        "priority": 10000,
        "memberships": [x.dn for x in search.roles(sesion,filter="Auditor")],
        "enabled":False,
        "entitlements": entitlements,
    }
    pp = ProvisioningPolicy(sesion, policy_attrs=policy)
    pp.crear(sesion)

    # buscar pol creada
    time.sleep(3)
    pp_creada = search.provisioning_policy(sesion, name, parent)[0]
    assert pp_creada.name == name

    # modificar y validar modificacion
    nueva_desc = "modificacion"
    pp_creada.description = nueva_desc
    pp_creada.entitlements[service.dn]["automatic"]=True
    pp_creada.modificar(sesion)
    time.sleep(3)
    pp_mod = search.provisioning_policy(sesion, name, parent)[0]
    assert pp_mod.description == nueva_desc

    # eliminar y validar eliminación
    time.sleep(120)  # tiene que terminar de evaluar la creación/mod
    pp_mod.eliminar(sesion)
    time.sleep(10)
    pp_elim = search.provisioning_policy(sesion, name, parent)
    assert len(pp_elim) == 0


def test_search_groups(sesion):
    # TODO Search by account/access
    # by service
    parent=search.organizational_container(sesion,"organizations",test_org)[0]
    service_dn = search.service(sesion, parent, filter="Directorio Activo")[0].dn
    r = search.groups(
        sesion, by="service", service_dn=service_dn, group_info="Administrators"
    )
    print(r)


def test_crear_modificar_suspender_restaurar_eliminar_persona(sesion):

    # required attributes on the Person form (more can be included)
    info_persona = {
        "givenname": "te",
        "sn": "st",
        "cn": "test",
        "initials": "CC",
        "employeenumber": random.randint(1, 99999999),
        "departmentnumber": test_dep,
        "manager": test_manager,
        "title": "test",
        "description": test_description,
        "businesscategory": "test",
        "mobile": "test@test.com",
    }
    persona = Person(sesion, person_attrs=info_persona)

    # crear y validar
    parent=search.organizational_container(sesion,"organizations",test_org)[0]
    persona.crear(sesion, parent, "ok")
    time.sleep(2)
    persona_creada = search.people(
        sesion,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_creada.employeenumber == str(info_persona["employeenumber"])

    # modificar
    persona_creada.title = "nuevo cargo"
    persona_creada.modificar(sesion, "ok")
    time.sleep(3)
    persona_mod = search.people(
        sesion,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_mod.title == persona_creada.title

    # suspender
    persona_mod.suspender(sesion,"ok")
    time.sleep(3)
    persona_sus = search.people(
        sesion,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_sus.erpersonstatus=="INACTIVE"

    #restaurar
    persona_sus.restaurar(sesion,"ok")
    time.sleep(3)
    persona_res = search.people(
        sesion,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_res.erpersonstatus=="ACTIVE"

    #eliminar
    persona_res.eliminar(sesion,"ok")
    time.sleep(3)
    persona_elim = search.people(
        sesion,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        limit=1,
    )
    assert len(persona_elim)==0


def test_activites_by_request_id(sesion):
    request_id="7046801252248442711"
    res=search.activities(sesion,by="requestId",filter=request_id)

def test_search_ou(sesion):
    #TODO
    name="Colpensiones"
    search.organizational_container(sesion,"organizations",name)

    name="Cromasoft Ltda"
    search.organizational_container(sesion,"bporganizations",name)
    
    name="Despacho del Presidente"
    search.organizational_container(sesion,"organizationunits",name)
