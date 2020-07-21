from isimws.exceptions import *
from isimws.entities import Activity

def groups(sesion,by,dn,groupProfileName=None,groupInfo=None):
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
    sesion=sesion.soapclient
    if by=="account":
        raise NotImplementedError("No implementado aún")
    elif by=="access":
        raise NotImplementedError("No implementado aún")
    elif by=="service":
        assert groupProfileName is not None,"Debe ingresar el parámetro groupProfileName"
        assert groupInfo is not None,"Debe ingresar el parámetro groupInfo"
        ret=sesion.buscarGruposPorServicio(dn,groupProfileName,groupInfo)
    else:
        raise InvalidOptionError("Opción inválida")

    return ret

def people(sesion,profile,by="cn",filter="*",attributes="cn",embedded="",limit=50,href=None):
    """"Wrapper para buscar/lookup personas o bpperson desde REST API

    Args:
        sesion ([isimws.auth.Session]): Sesión de isimws
        profile (str): Person/BPPerson
        by (str, optional): Atributo por el que buscar. Defaults to "cn".
        filter (str, optional): Filtro por el que buscar. Defaults to "*".
        attributes (str, optional): Atributos a retornar. Defaults to "cn".
        embedded (str, optional): Atributos embebidos a retornar (ej. manager.cn). Defaults to "".
        limit (int, optional): Defaults to 50.
        href ([type], optional): Si se provee el href de la persona, se realiza un lookup de este. Defaults to None.

    Returns:
        [dict/list(dict)]: Si es búsqueda, listado de personas encontradas. Si es lookup, retorna el resultado.
    """

    sesion=sesion.restclient

    if href is not None:
        ret=sesion.lookupPersona(href)
    else:
        ret=sesion.buscarPersonas(profile.lower(), atributos=attributes, embedded=embedded, buscar_por=by, filtro=filter,limit=limit)

    return ret

def roles(sesion,by="errolename",filter="*",find_unique=False):
    soap=****
    results=soap.buscarRol(f"({by}={filter})",find_unique)
    return results

def activities(sesion,by="activityName",filter="*"):
    """Busca actividades

    Args:
        sesion (isimws.auth.Session): Sesión de isimws
        by (str, optional): Filtros disponibles por ISIM REST API (activityId, nombres de actividad/servicio/participantes) o requestId. Defaults to "activityName".
        filter (str, optional): Filtro. Defaults to "*".
    """

    if by=="requestId":
        results=sesion.restclient.buscarActividad(solicitudID=f"/itim/rest/requests/{filter}")
    else:
        results=sesion.restclient.buscarActividad(search_attr=by,search_filter=filter)

    return [Activity(sesion,activity=a) for a in results]