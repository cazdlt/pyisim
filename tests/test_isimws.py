from random import randint
from pyisim.exceptions import NotFoundError
import pytest
import time
import random
from pyisim import search
from pyisim.auth import Session
from pyisim.entities import Person, ProvisioningPolicy, StaticRole
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
def session():
    return Session(test_url, admin_login, admin_pw, cert)


def test_search_access(session):
    r = search.access(session, filter="*Consulta*", limit=2)
    assert len(r) > 0


def test_search_people(session):
    r = search.people(session, by="employeenumber", filter="1015463230", limit=1)
    assert len(r) > 0


def test_search_service(session):
    r = search.service(session, search.organizational_container(session,"organizations",test_org)[0], filter="SAP NW")
    assert len(r) > 0
    assert r[0].name == "SAP NW"


def test_search_roles(session):
    r = search.roles(session, filter="SAP*")

    assert len(r) > 0
    assert "SAP" in r[0].name.upper()
    assert "ou=roles" in r[0].dn


def test_new_rol(session):
    parent=search.organizational_container(session,"organizations",test_org)[0]

    owners=[p.dn for p in search.people(session,by="employeenumber",filter="1015463230")]
    owners_roles=[r.dn for r in search.roles(session,filter="ITIM Administrators")]

    # creación
    rolinfo = {
        "name": "rol_prueba",
        "description": "rol_prueba",
        "parent": parent,
        "classification": "role.classification.business",
        "access_option": 2,
        "access_category": "Role",
        "owners": owners + owners_roles,
    }
    r = StaticRole(session, role_attrs=rolinfo)
    print(r)


def test_lookup_rol(session):
    dn = f"erglobalid=00000000000000000001,ou=roles,erglobalid=00000000000000000000,ou={test_org},dc={test_org}"
    r = StaticRole(session, dn=dn)
    assert r.name == "ITIM Administrators"

    dn = "not found"
    try:
        r = StaticRole(session, dn=dn)
    except NotFoundError:
        assert True


def test_crear_modificar_eliminar_rol(session):

    parent=search.organizational_container(session,"organizations",test_org)[0]

    owners=[p.dn for p in search.people(session,by="employeenumber",filter="1015463230")]
    owners_roles=[r.dn for r in search.roles(session,filter="ITIM Administrators")]

    # creación
    rolinfo = {
        "name": "rol_prueba",
        "description": "rol_prueba",
        "parent": parent,
        "classification": "role.classification.business",
        "access_option": 2,
        "access_category": "Role",
        "owners": owners + owners_roles,
    }
    rol = StaticRole(session, role_attrs=rolinfo)
    rol.add(session)
    assert hasattr(rol, "dn")

    # mod
    changes={
        "name":"rol_prueba_mod"
    }
    rol.description = "prueba_desc"
    rol.modify(session,changes)
    assert (
        StaticRole(session, dn=rol.dn).name == rol.name
    )  # busca el rol en sim y lo compara con el nuevo

    # del
    rol.delete(session)
    try:
        r = StaticRole(session, dn=rol.dn)
    except NotFoundError:
        assert True
    else:
        assert False


def test_get_client():
    s = Session(test_url, admin_login, admin_pw, cert)
    s.soapclient.login(admin_login, admin_pw)
    s.soapclient.login(admin_login, admin_pw)


def test_inicializar_politicas(session):

    parent=search.organizational_container(session,"organizations",test_org)[0]
    service=search.service(session,parent,filter="Directorio Activo")[0]

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
        "memberships": [x.dn for x in search.roles(session,filter="Auditor")],
        "enabled":False,
        "entitlements": entitlements,
    }
    pp = ProvisioningPolicy(session, policy_attrs=policy)
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
    pp = ProvisioningPolicy(session, policy_attrs=policy)

    pp.entitlements["ADprofile"]["automatic"]=True
    print("")


    #buscar y modificar política
    pp = search.provisioning_policy(session, "Test TipoServicio", parent)[0]
    print(pp)

    pp.entitlements=entitlements
    pp.entitlements["*"]["automatic"]=True
    print("")



def test_search_provisioning_policy(session):

    r = search.provisioning_policy(session, "Test TipoServicio", search.organizational_container(session,"organizations",test_org)[0])
    print(r[0].entitlements)
    assert len(r) > 0


def test_crear_modificar_eliminar_politica(session):

    # crear
    name = f"test{random.randint(0,999999)}"
    parent=search.organizational_container(session,"organizations",test_org)[0]
    service=search.service(session,parent,filter="Directorio Activo")[0]

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
        "memberships": [x.dn for x in search.roles(session,filter="Auditor")],
        "enabled":False,
        "entitlements": entitlements,
    }
    pp = ProvisioningPolicy(session, policy_attrs=policy)
    pp.add(session)

    # buscar pol creada
    time.sleep(3)
    pp_creada = search.provisioning_policy(session, name, parent)[0]
    assert pp_creada.name == name

    # modificar y validar modificacion
    nueva_desc = "modificacion"
    nuevos_ents=pp_creada.entitlements
    nuevos_ents[service.dn]["automatic"]=True
    changes={
        "description":nueva_desc,
        # "entitlements":nuevos_ents,
    }
    # pp_creada.description = nueva_desc
    pp_creada.entitlements[service.dn]["automatic"]=True
    pp_creada.modify(session,changes)
    time.sleep(3)
    pp_mod = search.provisioning_policy(session, name, parent)[0]
    assert pp_mod.description == nueva_desc

    # eliminar y validar eliminación
    time.sleep(120)  # tiene que terminar de evaluar la creación/mod
    pp_mod.delete(session)
    time.sleep(10)
    pp_elim = search.provisioning_policy(session, name, parent)
    assert len(pp_elim) == 0


def test_search_groups(session):
    # TODO Search by account/access
    # by service
    parent=search.organizational_container(session,"organizations",test_org)[0]
    service_dn = search.service(session, parent, filter="Directorio Activo")[0].dn
    r = search.groups(
        session, by="service", service_dn=service_dn, group_info="Administrators"
    )
    print(r)


def test_crear_modificar_suspender_restaurar_eliminar_persona(session):

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
    persona = Person(session, person_attrs=info_persona)

    # crear y validar
    parent=search.organizational_container(session,"organizations",test_org)[0]
    persona.add(session, parent, "ok")
    time.sleep(2)
    persona_creada = search.people(
        session,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_creada.employeenumber == str(info_persona["employeenumber"])

    # modificar
    persona_creada.title = "este no va" #se sobreescribe con changes
    persona_creada.mobile="estesi@test.org"

    nuevo_cargo_real="nuevo cargo si va"
    changes={
        "title":nuevo_cargo_real,
        "mail":"estetambien@test.org"
    }
    persona_creada.modify(session,"ok",changes)
    time.sleep(3)
    persona_mod = search.people(
        session,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_mod.title == nuevo_cargo_real

    # suspender
    persona_mod.suspend(session,"ok")
    time.sleep(3)
    persona_sus = search.people(
        session,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_sus.erpersonstatus=="INACTIVE"

    #restaurar
    persona_sus.restore(session,"ok")
    time.sleep(3)
    persona_res = search.people(
        session,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_res.erpersonstatus=="ACTIVE"

    #eliminar
    persona_res.delete(session,"ok")
    time.sleep(3)
    persona_elim = search.people(
        session,
        by="employeenumber",
        filter=info_persona["employeenumber"],
        limit=1,
    )
    assert len(persona_elim)==0


def test_activites_by_request_id(session):

    #group access
    request_id="5101169363690384727"
    res=search.activities(session,by="requestId",filter=request_id)
    print(res)

    #role access
    request_id="4395986706018163961"
    res=search.activities(session,by="requestId",filter=request_id)
    print(res)

    #recert
    request_id="4873926809151916308"
    res=search.activities(session,by="requestId",filter=request_id)
    print(res)

    #new user rfi
    request_id="4773504143421693102"
    res=search.activities(session,by="requestId",filter=request_id)
    print(res)
    

def test_search_ou(session):
    #TODO
    name="Colpensiones"
    search.organizational_container(session,"organizations",name)

    name="Cromasoft Ltda"
    search.organizational_container(session,"bporganizations",name)
    
    name="Despacho del Presidente"
    search.organizational_container(session,"organizationunits",name)
