# type: ignore
import random
import time

import pytest
from pyisim import search
from pyisim.auth import Session
from pyisim.entities import DynamicRole, Person, ProvisioningPolicy, StaticRole, Account, Request
from pyisim.entities.role import RoleAttributes
from pyisim.exceptions import NotFoundError
from pyisim.utils import get_account_defaults
from secret import (
    admin_login,
    admin_pw,
    cert,
    env,
    test_dep,
    test_description,
    test_manager,
    test_org,
    test_url,
    test_title,
    test_service_name,
)


@pytest.fixture
def session() -> Session:
    return Session(test_url, admin_login, admin_pw, cert)


def test_search_access(session):
    r = search.access(session, search_filter="*Consulta*", limit=2)
    assert len(r) > 0


def test_search_people(session):
    r = search.people(session, by="employeenumber", search_filter="1015463230", limit=1)
    assert len(r) > 0


def test_search_service(session):
    r = search.service(
        session,
        search.organizational_container(session, "organizations", test_org)[0],
        search_filter="SAP NW",
    )
    assert len(r) > 0
    assert r[0].name == "SAP NW"


def test_search_roles(session):
    r = search.roles(session, search_filter="SAP*")

    assert len(r) > 0
    assert "SAP" in r[0].name.upper()
    assert "ou=roles" in r[0].dn


def test_new_rol(session):
    parent = search.organizational_container(session, "organizations", test_org)[0]

    owners = [
        p.dn
        for p in search.people(session, by="employeenumber", search_filter="1015463230")
    ]
    owners_roles = [
        r.dn for r in search.roles(session, search_filter="ITIM Administrators")
    ]

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

    parent = search.organizational_container(session, "organizations", test_org)[0]

    owners = [
        p.dn
        for p in search.people(session, by="employeenumber", search_filter="1015463230")
    ]
    owners_roles = [
        r.dn for r in search.roles(session, search_filter="ITIM Administrators")
    ]

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
    changes = {"name": "rol_prueba_mod"}
    rol.description = "prueba_desc"
    rol.modify(session, changes)
    assert (
        StaticRole(session, dn=rol.dn).name == rol.name
    )  # busca el rol en sim y lo compara con el nuevo

    # del
    rol.delete(session)
    try:
        StaticRole(session, dn=rol.dn)
    except NotFoundError:
        assert True
    else:
        assert False


def test_get_client():
    s = Session(test_url, admin_login, admin_pw, cert)
    s.soapclient.login(admin_login, admin_pw)
    s.soapclient.login(admin_login, admin_pw)


def test_inicializar_politicas(session):

    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter="Directorio Activo")[0]

    entitlements = {
        service.dn: {
            "automatic": False,
            "workflow": None,
            "parameters": {
                "ergroup": [
                    {
                        "enforcement": "Default",
                        "type": "script",
                        "values": "return 'test';",
                    },
                    {
                        "enforcement": "Excluded",
                        "type": "null",
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["test1", "test2"],
                    },
                    {
                        "enforcement": "Default",
                        "type": "Constant",
                        "values": ["test3"],
                    },
                    {
                        "enforcement": "MANDATORY",
                        "type": "REGEX",
                        "values": r"^[\s\w]+$",
                    },
                ],
                "eradfax": [
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["1018117"],
                    }
                ],
            },
        },
        "*": {"automatic": False, "workflow": None, "parameters": {}},
    }
    policy = {
        "description": "test",
        "name": "test",
        "parent": parent,
        "priority": 10000,
        "memberships": [x.dn for x in search.roles(session, search_filter="Auditor")],
        "enabled": False,
        "entitlements": entitlements,
    }
    pp = ProvisioningPolicy(session, policy_attrs=policy)
    print(pp.entitlements)
    print(pp)

    # modificar política
    policy = {
        "description": "test",
        "name": "test",
        "parent": parent,
        "priority": 100,
        "memberships": "*",
        "entitlements": {
            "ADprofile": {"automatic": False, "workflow": None, "parameters": {}},
        },
    }
    pp = ProvisioningPolicy(session, policy_attrs=policy)

    pp.entitlements["ADprofile"]["automatic"] = True
    print("")

    # buscar y modificar política
    pp = search.provisioning_policy(session, "Test TipoServicio", parent)[0]
    print(pp)

    pp.entitlements = entitlements
    pp.entitlements["*"]["automatic"] = True
    print("")


def test_search_provisioning_policy(session):

    r = search.provisioning_policy(
        session,
        "Test TipoServicio",
        search.organizational_container(session, "organizations", test_org)[0],
    )
    print(r[0].entitlements)
    assert len(r) > 0


def test_crear_modificar_eliminar_politica(session):

    # crear
    name = f"test{random.randint(0,999999)}"
    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter="Directorio Activo")[0]

    entitlements = {
        service.dn: {
            "automatic": False,
            "workflow": None,
            "parameters": {
                "ercompany": [
                    {
                        "enforcement": "Default",
                        "type": "script",
                        "values": "return 'test';",
                    },
                    {
                        "enforcement": "Excluded",
                        "type": "null",
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["test1", "test2"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "Constant",
                        "values": ["test3"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "REGEX",
                        "values": r"^[\s\w]+$",
                    },
                ],
                "eradfax": [
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["1018117"],
                    }
                ],
            },
        },
        "*": {"automatic": False, "workflow": None, "parameters": {}},
    }
    policy = {
        "description": "test",
        "name": name,
        "parent": parent,
        "priority": 10000,
        "memberships": [x.dn for x in search.roles(session, search_filter="Auditor")],
        "enabled": False,
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
    nuevos_ents = pp_creada.entitlements
    nuevos_ents[service.dn]["automatic"] = True
    changes = {
        "description": nueva_desc,
        # "entitlements":nuevos_ents,
    }
    # pp_creada.description = nueva_desc
    pp_creada.entitlements[service.dn]["automatic"] = True
    pp_creada.modify(session, changes)
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
    parent = search.organizational_container(session, "organizations", test_org)[0]
    service_dn = search.service(session, parent, search_filter="Directorio Activo")[
        0
    ].dn
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
    parent = search.organizational_container(session, "organizations", test_org)[0]
    persona.add(session, parent, "ok")
    time.sleep(5)
    persona_creada = search.people(
        session,
        by="employeenumber",
        search_filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_creada.employeenumber == str(info_persona["employeenumber"])

    # modificar
    persona_creada.title = "este no va"  # se sobreescribe con changes
    persona_creada.mobile = "estesi@test.org"

    nuevo_cargo_real = "nuevo cargo si va"
    changes = {"title": nuevo_cargo_real, "mail": "estetambien@test.org"}
    persona_creada.modify(session, "ok", changes)
    time.sleep(3)
    persona_mod = search.people(
        session,
        by="employeenumber",
        search_filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_mod.title == nuevo_cargo_real

    # suspender
    persona_mod.suspend(session, "ok")
    time.sleep(3)
    persona_sus = search.people(
        session,
        by="employeenumber",
        search_filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_sus.erpersonstatus == "INACTIVE"

    # restaurar
    persona_sus.restore(session, "ok")
    time.sleep(3)
    persona_res = search.people(
        session,
        by="employeenumber",
        search_filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_res.erpersonstatus == "ACTIVE"

    # eliminar
    persona_res.delete(session, "ok")
    time.sleep(3)
    persona_elim = search.people(
        session,
        by="employeenumber",
        search_filter=info_persona["employeenumber"],
        limit=1,
    )
    assert len(persona_elim) == 0


def test_activites_by_request_id(session):

    # group access
    request_id = "5101169363690384727"
    res = search.activities(session, by="requestId", search_filter=request_id)
    print(res)

    # role access
    request_id = "4395986706018163961"
    res = search.activities(session, by="requestId", search_filter=request_id)
    print(res)

    # recert
    request_id = "4873926809151916308"
    res = search.activities(session, by="requestId", search_filter=request_id)
    print(res)

    # new user rfi
    request_id = "4773504143421693102"
    res = search.activities(session, by="requestId", search_filter=request_id)
    print(res)


def test_search_ou(session):
    name = test_org
    search.organizational_container(session, "organizations", name)

    name = "Cromasoft Ltda"
    search.organizational_container(session, "bporganizations", name)

    name = "Despacho del Presidente"
    search.organizational_container(session, "organizationunits", name)


def test_search_dynrole(session):

    # solo dinámico
    r = search.roles(session, search_filter="Logonhours GDD")
    print(r)

    # ambos
    r = search.roles(session, search_filter="*Logonhours*")
    print(r)


def test_crear_modificar_eliminar_dynrol(session):
    parent = search.organizational_container(session, "organizations", test_org)[0]

    owners = [
        p.dn
        for p in search.people(session, by="employeenumber", search_filter="1015463230")
    ]
    owners_roles = [
        r.dn for r in search.roles(session, search_filter="ITIM Administrators")
    ]

    # creación
    name = "dynrol_prueba"
    rolinfo = {
        "name": name,
        "description": "dynrol_prueba",
        "parent": parent,
        "classification": "role.classification.business",
        "access_option": 2,
        "access_category": "Role",
        "owners": owners + owners_roles,
        "rule": "(title=ROLETEST)",
    }
    rol = DynamicRole(session, role_attrs=rolinfo)
    rol.add(session)
    time.sleep(3)
    rol_creado = search.roles(session, search_filter=name)
    assert rol_creado[0].name == name
    rol_creado = rol_creado[0]

    # mod
    changes = {"name": "dynrol_prueba_mod", "rule": "(departmentnumber=ROLETEST)"}
    rol_creado.description = "prueba_desc"
    rol_creado.modify(session, changes)
    time.sleep(3)

    # esto hace lookup en SIM y compara con los atributos de acá
    assert DynamicRole(session, dn=rol_creado.dn).description == rol_creado.description

    # del
    rol_creado.delete(session)
    time.sleep(3)
    try:
        DynamicRole(session, dn=rol_creado.dn)
    except NotFoundError:
        assert True
    else:
        assert False


def test_crear_modificar_eliminar_rol_dataclasss(session):

    parent = search.organizational_container(session, "organizations", test_org)[0]

    owners = [
        p.dn
        for p in search.people(session, by="employeenumber", search_filter="1015463230")
    ]
    owners_roles = [
        r.dn for r in search.roles(session, search_filter="ITIM Administrators")
    ]

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
    role_atrrs = RoleAttributes(**rolinfo)
    rol = StaticRole(session, role_attrs=role_atrrs)
    rol.add(session)
    assert hasattr(rol, "dn")

    # mod
    changes = {"name": "rol_prueba_mod"}
    rol.description = "prueba_desc"
    rol.modify(session, changes)
    assert (
        StaticRole(session, dn=rol.dn).name == rol.name
    )  # busca el rol en sim y lo compara con el nuevo

    # del
    rol.delete(session)
    try:
        StaticRole(session, dn=rol.dn)
    except NotFoundError:
        assert True
    else:
        assert False


def test_crear_modificar_eliminar_politica_dataclass(session):

    # crear
    name = f"test{random.randint(0,999999)}"
    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter="Directorio Activo")[0]

    entitlements = {
        service.dn: {
            "automatic": False,
            "workflow": None,
            "parameters": {
                "ercompany": [
                    {
                        "enforcement": "Default",
                        "type": "script",
                        "values": "return 'test';",
                    },
                    {
                        "enforcement": "Excluded",
                        "type": "null",
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["test1", "test2"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "Constant",
                        "values": ["test3"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "REGEX",
                        "values": r"^[\s\w]+$",
                    },
                ],
                "eradfax": [
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["1018117"],
                    }
                ],
            },
        },
        "*": {"automatic": False, "workflow": None, "parameters": {}},
    }
    policy = {
        "description": "test",
        "name": name,
        "parent": parent,
        "priority": 10000,
        "memberships": [x.dn for x in search.roles(session, search_filter="Auditor")],
        "enabled": False,
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
    nuevos_ents = pp_creada.entitlements
    nuevos_ents[service.dn]["automatic"] = True
    changes = {
        "description": nueva_desc,
        # "entitlements":nuevos_ents,
    }
    # pp_creada.description = nueva_desc
    pp_creada.entitlements[service.dn]["automatic"] = True
    pp_creada.modify(session, changes)
    time.sleep(3)
    pp_mod = search.provisioning_policy(session, name, parent)[0]
    assert pp_mod.description == nueva_desc

    # eliminar y validar eliminación
    time.sleep(120)  # tiene que terminar de evaluar la creación/mod
    pp_mod.delete(session)
    time.sleep(10)
    pp_elim = search.provisioning_policy(session, name, parent)
    assert len(pp_elim) == 0


def test_get_account_defaults(session):
    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter="Directorio Activo")[0]
    person = search.people(session, by="employeenumber", search_filter="1015463230")[0]

    try:
        r = get_account_defaults(session, service)
        print(r)
    except Exception as e:
        print(e)

    r = get_account_defaults(session, service, person)
    print(r)


def test_search_account(session):

    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter="Directorio Activo")[0]
    sfilter = "(eruid=cazamorad)"

    # sin servicio
    r = search.account(session, sfilter)
    print(r)

    # con servicio
    r = search.account(session, sfilter, service)
    print(r)


def test_crear_cuenta(session):

    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter="Directorio Activo")[0]
    owner = search.people(session, by="employeenumber", search_filter="55608311080")[0]
    justification = "ok"

    attrs = get_account_defaults(session, service, owner)
    cuenta = Account(session, account_attrs=attrs)
    cuenta.add(session, owner, service, justification)


def test_get_person_accounts(session):
    me = session.current_person()
    accounts = me.get_accounts(session)
    print(accounts)


def test_suspender_restaurar_eliminar_cuenta(session):

    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter=test_service_name)[0]

    n = random.randint(0, 10000)
    test_person_attrs = {
        "cn": ".",
        "givenname": "prueba",
        "sn": n,
        "employeenumber": n,
        "manager": test_manager,
        "description": test_description,
        "departmentnumber": test_dep,
        "title": test_title,
        "mail": "cazdlt@gmail.com",
        "mobile": "cazdlt@gmail.com",
    }

    p = Person(session, person_attrs=test_person_attrs)
    p.add(session, parent, "test")
    time.sleep(5)

    owner = search.people(session, by="employeenumber", search_filter=n)[0]
    justification = "ok"

    # crear
    attrs = get_account_defaults(session, service, owner)
    cuenta = Account(session, account_attrs=attrs)
    r = cuenta.add(session, owner, service, justification)
    time.sleep(3)

    # suspender y probar
    cuentas = owner.get_accounts(session)
    cuenta_test = [c for c in cuentas if c.service_name == test_service_name][0]
    cuenta_test.suspend(session, justification)
    time.sleep(3)
    cuentas = owner.get_accounts(session)
    cuenta_test = [c for c in cuentas if c.service_name == test_service_name][0]
    assert cuenta_test.eraccountstatus == "1"

    # restaurar y probar
    cuentas = owner.get_accounts(session)
    cuenta_test = [c for c in cuentas if c.service_name == test_service_name][0]
    cuenta_test.restore(session, "NewPassw0rd", justification)
    time.sleep(3)
    cuentas = owner.get_accounts(session)
    cuenta_test = [c for c in cuentas if c.service_name == test_service_name][0]
    assert cuenta_test.eraccountstatus == "0"

    # eliminar
    try:
        cuenta_test.delete(session, "ok")
        time.sleep(3)
        cuentas = owner.get_accounts(session)
        cuenta_test = [c for c in cuentas if c.service_name == test_service_name]
        assert len(cuenta_test) < 1
    except Exception as e:
        assert (
            "CTGIMI019E" in e.message
        )  # CTGIMI019E = can't delete because policy (but tried)


def test_modificar_dejar_huerfana_cuenta(session):

    parent = search.organizational_container(session, "organizations", test_org)[0]
    service = search.service(session, parent, search_filter=test_service_name)[0]

    n = random.randint(0, 10000)
    test_person_attrs = {
        "cn": ".",
        "givenname": "prueba",
        "sn": n,
        "employeenumber": n,
        "manager": test_manager,
        "description": test_description,
        "departmentnumber": test_dep,
        "title": test_title,
        "mail": "cazdlt@gmail.com",
        "mobile": "cazdlt@gmail.com",
    }

    # crea persona y la busca
    p = Person(session, person_attrs=test_person_attrs)
    p.add(session, parent, "test")
    time.sleep(5)
    owner = search.people(session, by="employeenumber", search_filter=n)[0]

    justification = "ok"

    # crear
    attrs = get_account_defaults(session, service, owner)
    cuenta = Account(session, account_attrs=attrs)
    r = cuenta.add(session, owner, service, justification)
    time.sleep(3)

    # modificar
    cuentas = owner.get_accounts(session)
    cuenta_test = [c for c in cuentas if c.service_name == test_service_name][0]
    cuenta_test.title = "new title"
    cuenta_test.sn = "nueva description"
    changes = {"title": "newer title", "employeenumber": 347231}  # this should stay
    cuenta_test.modify(session, justification, changes)

    try:
        cuenta_test.orphan(session)
        time.sleep(5)
        cuentas = owner.get_accounts(session)
        cuenta_test = [c for c in cuentas if c.service_name == test_service_name]
        assert len(cuenta_test) < 1
    except Exception as e:
        pass
        # assert (
        #     "CTGIMI019E" in e.message
        # )  # CTGIMI019E = can't orphan because policy (but tried)


def test_request_access_approve(session):

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
    parent = search.organizational_container(session, "organizations", test_org)[0]
    persona.add(session, parent, "ok")
    time.sleep(5)
    persona_creada = search.people(
        session,
        by="employeenumber",
        search_filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_creada.employeenumber == str(info_persona["employeenumber"])

    accesses=search.access(session,search_filter="*",limit=2) # get two accesses
    r=persona_creada.request_access(session,accesses,"ok")
    time.sleep(3)
    request_id=r.request.id
    print(r)
    actividades=search.activities(session,"requestId",request_id)

    #complete 
    r2=actividades[0].complete(session,"approve","ok")
    print(r2)

    #now try to complete it again
    r3=actividades[0].complete(session,"approve","ok")
    print(r3)

def test_lookup_request(session):

    id="4020615234983983545" #real id
    r=Request(session,id=id)
    assert str(r.id)==id

    try:
        id="6344020623458355" #non existant id
        r=Request(session,id=id)
    except NotFoundError:
        pass

def test_get_pending_activities_abort(session):

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
    parent = search.organizational_container(session, "organizations", test_org)[0]
    persona.add(session, parent, "ok")
    time.sleep(5)
    persona_creada = search.people(
        session,
        by="employeenumber",
        search_filter=info_persona["employeenumber"],
        attributes="*",
        limit=1,
    )[0]
    assert persona_creada.employeenumber == str(info_persona["employeenumber"])

    accesses=search.access(session,search_filter="*",limit=2) # get two accesses
    r=persona_creada.request_access(session,accesses,"ok")
    time.sleep(3)
    request_id=r.request.id

    request=Request(session,id=request_id)
    from_request=request.get_pending_activities(session)    
    
    from_search=search.activities(session,"requestId",request_id)

    assert len(from_request)==len(from_search)

    request.abort(session,"ok")
    time.sleep(3)
    aborted=Request(session,id=request_id)
    assert aborted.process_state=="A"
    