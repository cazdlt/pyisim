from isimws.exceptions import *
from isimws.entities import (
    Activity,
    Access,
    OrganizationalContainer,
    Person,
    Service,
    StaticRole,
    ProvisioningPolicy,
    Group,
)


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
        ret = session.buscarGruposPorServicio(service_dn, group_profile_name, group_info)
    else:
        raise InvalidOptionError("Invalid option")

    return [Group(session, group=g) for g in ret]


def people(
    session,
    filter="*",
    by="cn",
    profile_name="Person",
    attributes="*",
    embedded="",
    limit=50,
):
    """ "Wrapper para buscar/lookup personas o bpperson desde REST API

    Args:
        session ([isimws.auth.Session]): Sesión de isimws
        profile (str): Person/BPPerson
        by (str, optional): Atributo por el que buscar. Defaults to "cn".
        filter (str, optional): Filtro por el que buscar. Defaults to "*".
        attributes (str, optional): Atributos a retornar. Defaults to "dn".
        embedded (str, optional): Atributos embebidos a retornar (ej. manager.cn). Defaults to "".
        limit (int, optional): Defaults to 50.

    Returns:
        [list(Person)]: listado de personas encontradas
    """

    ret = session.restclient.buscarPersonas(
        profile_name,
        atributos=attributes,
        embedded=embedded,
        buscar_por=by,
        filtro=filter,
        limit=limit,
    )
    personas = [Person(session, person=p) for p in ret]
    return personas


def provisioning_policy(session, name, parent: OrganizationalContainer):

    wsou = parent.wsou
    results = session.soapclient.buscarPoliticaSuministro(
        wsou, nombre_politica=name, find_unique=False
    )
    return [ProvisioningPolicy(session, provisioning_policy=p) for p in results]


def roles(session, by="errolename", filter="*", find_unique=False):
    soap = session.soapclient
    results = soap.buscarRol(f"({by}={filter})", find_unique)
    return [StaticRole(session, rol=r) for r in results]


def activities(session, by="activityName", filter="*"):
    """Busca actividades

    Args:
        session (isimws.auth.Session): Sesión de isimws
        by (str, optional): Filtros disponibles por ISIM REST API (activityId, nombres de actividad/servicio/participantes) o requestId. Defaults to "activityName".
        filter (str, optional): Filtro. Defaults to "*".
    """

    if by == "requestId":
        # session.soapclient.buscarActividadesDeSolicitud(filter)
        """ RESPUESTA IBM A getRecurseSubProcess()
        Your observation is correct. The backend code returns the activities belonging to the first level sub-process only. 
        I feel the main confusion is due to the lack of documentation around this API and the name of the parameter used. 
        The intent of introducing this additional boolean flag was to restrict the result to only the direct activities of the main process. 
        It should have been “getImmediateChildActivities” rather than “recurseSubProcesses”.
        The customer can accomplish this by using a combination of getActivities() and getChildProcesses().
        """
        results = session.restclient.buscarActividad(
            solicitudID=f"/itim/rest/requests/{filter}"
        )
    else:
        results = session.restclient.buscarActividad(
            search_attr=by, search_filter=filter
        )

    return [Activity(session, activity=a) for a in results]


def access(session, by="accessName", filter="*", attributes="", limit=20):

    ret = session.restclient.buscarAcceso(
        by=by, filtro=filter, atributos=attributes, limit=limit
    )
    accesos = [Access(access=a) for a in ret]

    return accesos


def service(session, parent: OrganizationalContainer, by="erservicename", filter="*"):

    # ret=session.restclient.buscarServicio(by,filter,limit,atributos=attributes)
    # servicios=[Service(session,service=s) for s in ret]
    ret = session.soapclient.buscarServicio(
        parent.wsou, f"({by}={filter})", find_unique=False
    )
    servicios = [Service(session, service=s) for s in ret]

    return servicios


def organizational_container(session, profile_name, filter, by="name"):
    """[summary]

    Args:
        session (isimws.Session)
        profile_name (str): ["bporganizations", "organizationunits", "organizations","locations","admindomains"]
        filter (str): name or attr value
        by (str, optional): attribute to search by. Defaults to "name".

    Returns:
        isimws.entities.OrganizationalContainer
    """

    buscar_por = None if by == "name" else by
    ret = session.restclient.buscarOUs(
        profile_name, buscar_por=buscar_por, filtro=filter, attributes="dn"
    )

    ous = [OrganizationalContainer(session, organizational_container=ou) for ou in ret]

    return ous
