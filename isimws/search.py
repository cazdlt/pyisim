from isimws.exceptions import *
from isimws.entities import Activity, Access, Person, Service,StaticRole


def groups(sesion, by, dn, groupProfileName="", groupInfo=""):
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
    sesion = sesion.soapclient
    if by == "account":
        raise NotImplementedError("No implementado aún")
    elif by == "access":
        raise NotImplementedError("No implementado aún")
    elif by == "service":
        assert (
            groupProfileName is not None
        ), "Debe ingresar el parámetro groupProfileName"
        assert groupInfo is not None, "Debe ingresar el parámetro groupInfo"
        ret = sesion.buscarGruposPorServicio(dn, groupProfileName, groupInfo)
    else:
        raise InvalidOptionError("Opción inválida")

    return ret


def people(
    sesion, profile=Person, by="cn", filter="*", attributes="cn", embedded="", limit=50
):
    """ "Wrapper para buscar/lookup personas o bpperson desde REST API

    Args:
        sesion ([isimws.auth.Session]): Sesión de isimws
        profile (str): Person/BPPerson
        by (str, optional): Atributo por el que buscar. Defaults to "cn".
        filter (str, optional): Filtro por el que buscar. Defaults to "*".
        attributes (str, optional): Atributos a retornar. Defaults to "cn".
        embedded (str, optional): Atributos embebidos a retornar (ej. manager.cn). Defaults to "".
        limit (int, optional): Defaults to 50.

    Returns:
        [list(dict)]: listado de personas encontradas
    """

    ret = sesion.restclient.buscarPersonas(
        profile.profile_name,
        atributos=attributes,
        embedded=embedded,
        buscar_por=by,
        filtro=filter,
        limit=limit,
    )
    personas = [profile(sesion, rest_person=p) for p in ret]
    return personas


def roles(sesion, by="errolename", filter="*", find_unique=False):
    soap = sesion.soapclient
    results = soap.buscarRol(f"({by}={filter})", find_unique)
    return [StaticRole(sesion,rol=r) for r in results]


def activities(sesion, by="activityName", filter="*"):
    """Busca actividades

    Args:
        sesion (isimws.auth.Session): Sesión de isimws
        by (str, optional): Filtros disponibles por ISIM REST API (activityId, nombres de actividad/servicio/participantes) o requestId. Defaults to "activityName".
        filter (str, optional): Filtro. Defaults to "*".
    """

    if by == "requestId":
        results = sesion.restclient.buscarActividad(
            solicitudID=f"/itim/rest/requests/{filter}"
        )
    else:
        results = sesion.restclient.buscarActividad(
            search_attr=by, search_filter=filter
        )

    return [Activity(sesion, activity=a) for a in results]


def access(sesion, by="accessName", filter="*", attributes="", limit=20):

    ret = sesion.restclient.buscarAcceso(
        by=by, filtro=filter, atributos=attributes, limit=limit
    )
    accesos = [Access(access=a) for a in ret]

    return accesos


def service(sesion, parent_name, by="erservicename", filter="*"):

    # ret=sesion.restclient.buscarServicio(by,filter,limit,atributos=attributes)
    # servicios=[Service(sesion,service=s) for s in ret]
    ret = sesion.soapclient.buscarServicio(
        parent_name, f"({by}={filter})", find_unique=False
    )
    servicios = [Service(sesion, service=s) for s in ret]

    return servicios