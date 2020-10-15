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
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyisim.auth import Session


def groups(session, by, service_dn=None, group_profile_name="", group_info=""):
    """Buscar grupos.

    Args:
        by (string): "account", "access" or "service"
        dn (string): account or access dn
        groupProfileName (string, optional): Group profile name if searching by service. Defaults to None.
        groupInfo (string, optional): Group name or description if searching by service. Defaults to None.

    Raises:
        NotImplementedError: Search by account or access not implemented yet.
        InvalidOptionError

    Returns:
        list: Search results
    """
    session = session.soapclient
    if by == "account":
        raise NotImplementedError
    elif by == "access":
        raise NotImplementedError
    elif by == "service":
        ret = session.buscarGruposPorServicio(
            service_dn, group_profile_name, group_info
        )
    else:
        raise InvalidOptionError("Invalid option")

    return [Group(session, group=g) for g in ret]


def people(
    session,
    search_filter="*",
    by="cn",
    profile_name="Person",
    attributes="*",
    limit=50,
):
    """ "Wrapper para buscar/lookup personas o bpperson desde REST API

    Args:
        session ([pyisim.auth.Session]): Sesión de pyisim
        profile (str): Person/BPPerson
        by (str, optional): LDAP Attribute to search by. Defaults to "cn".
        search_filter (str, optional): Filter to search by. Defaults to "*".
        attributes (str, optional): Attributes to return in the Person instance. Defaults to "dn".
        limit (int, optional): Defaults to 50.

    Returns:
        [list(Person)]: listado de personas encontradas
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


def provisioning_policy(session, name: str, parent: OrganizationalContainer):

    wsou = parent.wsou
    results = session.soapclient.buscarPoliticaSuministro(
        wsou, nombre_politica=name, find_unique=False
    )
    return [ProvisioningPolicy(session, provisioning_policy=p) for p in results]


def roles(session, by="errolename", search_filter="*", find_unique=False):
    soap = session.soapclient
    results = soap.buscarRol(f"({by}={search_filter})", find_unique)

    is_dynamic = [
        any(filter(lambda i: i.name == "erjavascript", r.attributes.item))
        for r in results
    ]
    return [
        DynamicRole(session, rol=r) if is_dynamic[i] else StaticRole(session, rol=r)
        for i, r in enumerate(results)
    ]


def activities(session, by="activityName", search_filter="*"):
    """
    Returns PENDING activities

    Args:
        session (pyisim.auth.Session): PyISIM Session
        by (str, optional): "requestId" oor filters available in ISIMs REST API docs (activityId, activityName, serviceName, participantName). Defaults to "activityName".
        search_filter (str, optional): Search filter. Defaults to "*".
    """

    if by == "requestId":
        results = session.soapclient.buscarActividadesDeSolicitud(search_filter)
        return [Activity(session, id=a.id) for a in results]

    else:
        results = session.restclient.buscarActividad(
            search_attr=by, search_filter=search_filter
        )

        return [Activity(session, activity=a) for a in results]


def access(session, by="accessName", search_filter="*", attributes="", limit=20):

    ret = session.restclient.buscarAcceso(
        by=by, filtro=search_filter, atributos=attributes, limit=limit
    )
    accesos = [Access(access=a) for a in ret]

    return accesos


def service(session, parent: OrganizationalContainer, by="erservicename", search_filter="*"):

    # ret=session.restclient.buscarServicio(by,search_filter,limit,atributos=attributes)
    # servicios=[Service(session,service=s) for s in ret]
    ret = session.soapclient.buscarServicio(
        parent.wsou, f"({by}={search_filter})", find_unique=False
    )
    servicios = [Service(session, service=s) for s in ret]

    return servicios


def organizational_container(session, profile_name, search_filter, by="name"):
    """[summary]

    Args:
        session (pyisim.Session)
        profile_name (str): ["bporganizations", "organizationunits", "organizations","locations","admindomains"]
        search_filter (str): name or attr value
        by (str, optional): attribute to search by. Defaults to "name".

    Returns:
        pyisim.entities.OrganizationalContainer
    """

    buscar_por = None if by == "name" else by
    ret = session.restclient.buscarOUs(
        profile_name, buscar_por=buscar_por, filtro=search_filter, attributes="dn"
    )

    ous = [OrganizationalContainer(session, organizational_container=ou) for ou in ret]

    return ous
