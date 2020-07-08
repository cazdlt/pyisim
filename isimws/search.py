from isimws.exceptions import *

class Search:
    def __init__(self,sesion):
        self.sesion=sesion
        
    def groups(self,by,dn,groupProfileName=None,groupInfo=None):
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
        sesion=self.sesion.soapclient
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

    def people(self,profile,search_by="cn",filter="*",attributes="cn",embedded="",limit=50):
 
        sesion=self.sesion.restclient
        ret=sesion.buscarPersonas(profile.lower(), atributos=attributes, embedded=embedded, buscar_por=search_by, filtro=filter,limit=limit)

        return ret
