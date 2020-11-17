from pyisim.entities.role import Role
from pyisim.exceptions import InvalidOptionError
from pyisim.entities import (
    Activity,
    Access,
    OrganizationalContainer,
    Person,
    Service,
    StaticRole,
    DynamicRole,
    ProvisioningPolicy,
    Group,
    Account,
)

from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from pyisim.auth import Session


def groups(
    session: "Session",
    by: str,
    service_dn: str = None,
    group_profile_name="",
    group_info="",
) -> List[Group]:
    """
    Service group search.

    Args:
        session (Session): Active ISIM Session
        by (str): "account", "access" or "service"
        service_dn (str, optional): Parent service DN if searching by service. Defaults to None.
        group_profile_name (str, optional): Group profile name if searching by service. Defaults to None.
        group_info (str, optional): Group name or description if searching by service. Defaults to None.

    Raises:
        NotImplementedError: Search by account and access not implemented


    Returns:
        List[Group]: Search results
    """

    if by == "account":
        raise NotImplementedError
    elif by == "access":
        raise NotImplementedError
    elif by == "service":
        ret = session.soapclient.buscarGruposPorServicio(
            service_dn, group_profile_name, group_info
        )
    else:
        raise InvalidOptionError("Invalid option")

    return [Group(session, group=g) for g in ret]


def people(
    session: "Session",
    search_filter="*",
    by="cn",
    profile_name="Person",
    attributes="*",
    limit=50,
) -> List[Person]:
    """
    Person search

    Args:
        session (Session): Active ISIM Session
        search_filter (str, optional): Filter to search by. Defaults to "*".
        by (str, optional): LDAP Attribute to search by. Defaults to "cn".
        profile_name (str, optional): Person/BPPerson. Defaults to "Person".
        attributes (str, optional): Attributes to return in the Person instance. Defaults to "*".
        limit (int, optional): Defaults to 50.

    Returns:
        List[Person]: Search results
    """

    ret = session.restclient.buscarPersonas(
        profile_name,
        atributos=attributes,
        embedded="",
        buscar_por=by,
        filtro=search_filter,
        limit=limit,
    )
    personas = [Person(session, person=p) for p in ret]
    return personas


def provisioning_policy(
    session: "Session", name: str, parent: OrganizationalContainer
) -> List[ProvisioningPolicy]:
    """
    Provioning Policy search

    Args:
        session (Session): Active ISIM Session
        name (str): Provisioning Policy name
        parent (OrganizationalContainer): Provisioning Policy business unit

    Returns:
        List[ProvisioningPolicy]: Search results
    """

    wsou = parent.wsou
    results = session.soapclient.buscarPoliticaSuministro(
        wsou, nombre_politica=name, find_unique=False
    )
    return [ProvisioningPolicy(session, provisioning_policy=p) for p in results]


def roles(session: "Session", by="errolename", search_filter="*") -> List[Role]:
    """
    Role search

    Args:
        session (Session): Active ISIM Session
        by (str, optional): LDAP Attribute to search by. Defaults to "errolename".
        search_filter (str, optional): Filter to search by. Defaults to "*".

    Returns:
        List[Role]: Search results. Returns both Dynamic and Static Roles.
    """
    soap = session.soapclient
    results = soap.buscarRol(f"({by}={search_filter})", find_unique=False)

    is_dynamic = [
        any(filter(lambda i: i.name == "erjavascript", r.attributes.item))  # type: ignore
        for r in results
    ]
    return [
        DynamicRole(session, rol=r) if is_dynamic[i] else StaticRole(session, rol=r)
        for i, r in enumerate(results)
    ]


def activities(
    session: "Session", by="activityName", search_filter="*"
) -> List[Activity]:
    """
    Pending Activity search

    Args:
        session (Session): Active ISIM Session
        by (str, optional): "requestId" or filters available in ISIMs REST API docs (activityId, activityName, serviceName, participantName). Defaults to "activityName".
        search_filter (str, optional): Filter to search by. Defaults to "*".

    Returns:
        List[Activity]: Search results
    """

    if by == "requestId":
        results = session.soapclient.buscarActividadesDeSolicitud(search_filter)
        return [Activity(session, id=a.id) for a in results]

    else:
        results = session.restclient.buscarActividad(
            search_attr=by, search_filter=search_filter
        )

        return [Activity(session, activity=a) for a in results]


def access(
    session: "Session", by="accessName", search_filter="*", attributes="", limit=20
) -> List[Access]:
    """
    Access search

    Args:
        session (Session): Active ISIM Session
        by (str, optional): Defaults to "accessName".
        search_filter (str, optional): Filter to search by. Defaults to "*".
        limit (int, optional): Defaults to 20.

    Returns:
        List[Access]: Search results
    """

    ret = session.restclient.buscarAcceso(
        by=by, filtro=search_filter, atributos=attributes, limit=limit
    )
    accesos = [Access(access=a) for a in ret]

    return accesos


def service(
    session: "Session",
    parent: OrganizationalContainer,
    by="erservicename",
    search_filter="*",
) -> List[Service]:
    """
    Service search

    Args:
        session (Session): Active ISIM Session
        parent (OrganizationalContainer): Service business unit
        by (str, optional): LDAP attribute to search by. Defaults to "erservicename".
        search_filter (str, optional): Filter to search by. Defaults to "*".

    Returns:
        List[Service]: Search results
    """

    # ret=session.restclient.buscarServicio(by,search_filter,limit,atributos=attributes)
    # servicios=[Service(session,service=s) for s in ret]
    ret = session.soapclient.buscarServicio(
        parent.wsou, f"({by}={search_filter})", find_unique=False
    )
    servicios = [Service(session, service=s) for s in ret]

    return servicios


def organizational_container(
    session: "Session", profile_name: str, search_filter: str, by="name"
) -> List[OrganizationalContainer]:
    """
    Organizational container search.

    Profile names:

    * bporganizations
    * organizationunits
    * organizations
    * locations
    * admindomains

    Args:
        session (Session): Active ISIM Session
        profile_name (str): Organizational container profile name
        search_filter (str): Filter to search by.
        by (str, optional): Attribute to search by. Defaults to "name".

    Returns:
        List[OrganizationalContainer]: Search results.
    """

    buscar_por = None if by == "name" else by
    ret = session.restclient.buscarOUs(
        profile_name, buscar_por=buscar_por, filtro=search_filter, attributes="dn"
    )

    ous = [OrganizationalContainer(session, organizational_container=ou) for ou in ret]

    return ous


def account(
    session: "Session",
    ldap_search_filter: str,
    service: "Service" = None,
) -> List[Account]:

    args = {"filter": ldap_search_filter}

    if service:
        profile_name = session.soapclient.getAccountProfileForService(service.dn)
        args["profile"] = profile_name
        results = session.soapclient.searchAccounts(args)
        return [
            Account(session, account=r)
            for r in results
            if r["serviceName"] == service.name
        ]
    else:
        results = session.soapclient.searchAccounts(args)
        return [Account(session, account=r) for r in results]
