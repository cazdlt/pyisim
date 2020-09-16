from datetime import date
from zeep import Client, Settings
from zeep.xsd import Nil
from zeep.transports import Transport
from zeep.helpers import serialize_object
from zeep.cache import InMemoryCache

# from isim_classes import StaticRole
import requests
import pprint
from isimws.exceptions import *


requests.packages.urllib3.disable_warnings()


class ISIMClient:
    def __init__(self, url, user_, pass_, cert_path=None):

        self.addr = url + "/itim/services/"
        self.cert_path = cert_path
        self.s = self.login(user_, pass_)

    def login(self, user_, pass_):
        url = self.addr + "WSSessionService?wsdl"
        assert self.cert_path is not None, "No certificate passed"
        client = self.get_client("session_client", url)
        sesion = client.service.login(user_, pass_)
        # print(sesion)
        return sesion

    def get_client(self, client_name, url):

        # Si ya se inicializó el cliente especificado en client_name, lo devuelve. Si no, lo inicializa, setea y devuelve.
        client = getattr(self, client_name, None)

        if client is None:
            settings = Settings(strict=False)
            s = requests.Session()
            s.verify = self.cert_path
            client = Client(
                url,
                settings=settings,
                transport=Transport(session=s, cache=InMemoryCache()),
            )
            # necesario porque los WSDL de SIM queman el puerto y no funciona con balanceador
            client.service._binding_options["address"] = url[:-5]
            setattr(self, client_name, client)

        return client

    def lookupContainer(self, dn):

        url = self.addr + "WSOrganizationalContainerServiceService?wsdl"
        client = self.get_client("ou_client", url)

        cont = client.service.lookupContainer(self.s, dn)

        return cont

    def buscarOrganizacion(self, nombre):

        url = self.addr + "WSOrganizationalContainerServiceService?wsdl"
        client = self.get_client("ou_client", url)

        ous = client.service.searchContainerByName(self.s, Nil, "Organization", nombre)
        if len(ous) == 0:
            ous = client.service.searchContainerByName(
                self.s, Nil, "OrganizationalUnit", nombre
            )

        assert (
            len(ous) > 0
        ), f"No se ha encontrado la Unidad Organizativa de nombre: {nombre}. Verifique que sea un filtro LDAP válido."
        assert (
            len(ous) == 1
        ), f"Se ha encontrado más de una Unidad Organizativa de nombre: {nombre}"
        return ous[0]

    def buscarPoliticaSuministro(self, wsou, nombre_politica, find_unique=True):
        """
        Si find_unique es True (por defecto):
           lanza error si no encuentra ninguno o encuentra múltiples.
           Devuelve instancia encontrada

        Si find_unique es False:
           No lanza errores
           Devuelve lista de resultados
        """

        url = self.addr + "WSProvisioningPolicyServiceService?wsdl"
        client = self.get_client("pp_client", url)

        politicas = client.service.getPolicies(self.s, wsou, nombre_politica)

        if find_unique:
            assert (
                len(politicas) > 0
            ), f"No se ha encontrado la política {nombre_politica}."
            assert (
                len(politicas) == 1
            ), f"Se ha encontrado más de la política con: {nombre_politica}"
            return politicas[0]
        else:
            return politicas

    def crearPolitica(self, ou, wsprovisioningpolicy, date):

        url = self.addr + "WSProvisioningPolicyServiceService?wsdl"
        client = self.get_client("pp_client", url)

        s = client.service.createPolicy(self.s, ou, wsprovisioningpolicy, date)

        return s

    def modificarPolitica(self, ou, wsprovisioningpolicy, date):

        url = self.addr + "WSProvisioningPolicyServiceService?wsdl"
        client = self.get_client("pp_client", url)

        s = client.service.modifyPolicy(self.s, ou, wsprovisioningpolicy, date)

        return s

    def eliminarPolitica(self, ou, dn, date):
        url = self.addr + "WSProvisioningPolicyServiceService?wsdl"
        client = self.get_client("pp_client", url)

        s = client.service.deletePolicy(self.s, ou, dn, date)

        return s

    def buscarRol(self, filtro, find_unique=True):
        """
        Si find_unique es True (por defecto):
           lanza error si no encuentra ninguno o encuentra múltiples.
           Devuelve instancia encontrada

        Si find_unique es False:
           No lanza errores
           Devuelve lista de resultados
        """

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client("role_client", url)

        roles = client.service.searchRoles(self.s, filtro)

        if find_unique:
            assert (
                len(roles) > 0
            ), f"No se ha encontrado el rol con el filtro: {filtro}. Verifique que sea un filtro LDAP válido."
            assert len(roles) == 1, f"Se ha encontrado más de un rol con: {filtro}"
            return roles[0]
        else:
            return roles

    def lookupRole(self, dn):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client("role_client", url)

        try:
            r = client.service.lookupRole(self.s, dn)
            return r
        except:
            raise NotFoundError("Rol no encontrado")

    def crearRolEstatico(self, wsrole, wsou):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client("role_client", url)

        return client.service.createStaticRole(self.s, wsou, wsrole)

    def modificarRolEstatico(self, role_dn, wsattr_list):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client("role_client", url)

        return client.service.modifyStaticRole(self.s, role_dn, wsattr_list)

    def eliminarRolEstatico(self, role_dn, date=None):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client("role_client", url)

        if date:
            # TODO
            pass
        else:
            date = Nil
        return client.service.removeRole(self.s, role_dn, date)

    def buscarPersona(self, filtro):

        url = self.addr + "WSPersonServiceService?wsdl"
        client = self.get_client("person_client", url)

        personas = client.service.searchPersonsFromRoot(self.s, filtro, Nil)

        assert (
            len(personas) > 0
        ), f"No se ha encontrado la persona con el filtro: {filtro}. Verifique que sea un filtro LDAP válido."
        assert len(personas) == 1, f"Se ha encontrado más de una persona con: {filtro}"
        return personas[0]

    def buscarServicio(self, parent_ou_name, filtro, find_unique=True):

        url = self.addr + "WSServiceServiceService?wsdl"
        client = self.get_client("service_client", url)

        ou = self.buscarOrganizacion(parent_ou_name)
        servicios = client.service.searchServices(self.s, ou, filtro)

        if find_unique:
            if len(servicios) == 0:
                raise NotFoundError(
                    f"No se ha encontrado el servicio con el filtro: {parent_ou_name} - {filtro}. Verifique que sea un filtro LDAP válido."
                )
            assert (
                len(servicios) == 1
            ), f"Se ha encontrado más de un servicio con: {parent_ou_name} - {filtro}"
            return serialize_object(servicios[0], target_cls=dict)
        else:
            return [serialize_object(s, target_cls=dict) for s in servicios]

    def searchWorkflow(self, nombre, org_name):
        """
        Busca flujos de cuenta y acceso por el nombre.
        Retorna el DN.
        """

        url = self.addr + "WSSearchDataServiceService?wsdl"
        client = self.get_client("search_client", url)

        """
        Category puede ser (usar EstaCapitalizacion y quitar _):
        ACCESS_TYPE, ACCOUNT_TEMPLATE, ADOPTION_POLICY, AGENT_OPERATION, ATTRIBUTE_CONSTRAINT, 
        BPUNIT, CATEGORIES_FOR_LIFE_CYCLE_MGT, CONFIG, CONTAINER, CREDENTIAL, CREDENTIAL_COMPONENT, 
        CREDENTIAL_LEASE, CREDENTIAL_POOL, CREDENTIAL_SERVICE, CUSTOM_PROCESS, DYNAMIC_ROLE, FORM_TEMPLATE, 
        GLOBAL_ACCOUNT_TEMPLATE, GROUP, HOST_SELECTION_POLICY, IDENTITY_POLICY, JOIN_DIRECTIVE, JOINDIRECTIVE, 
        LIFECYCLE_PROFILE, LOCATION, OBJECT_PROFILE, ORG, ORGROLE, ORGUNIT, ORPHANED_ACCOUNT, OWNERSHIP_TYPE, 
        PASSWORD_POLICY, PRIVILEGE_RULE, PROVISIONING_POLICY, RECERTIFICATION_POLICY, ROLE, SECURITY_DOMAIN, 
        SEPARATION_OF_DUTY_POLICY, SEPARATION_OF_DUTY_RULE, SERVICE, SERVICE_MODEL, SERVICE_PROFILE, 
        SHARED_ACCESS_POLICY, SYSTEM_ROLE, SYSTEM_USER, TENANT, USERACCESS
        """
        flujos = client.service.findSearchControlObjects(
            self.s,
            {
                "objectclass": "erWorkflowDefinition",
                "contextDN": f"ou=workflow,erglobalid=00000000000000000000,ou={org_name},dc={org_name}",
                "returnedAttributeName": "dn",
                "filter": f"(erProcessName={nombre})",
                "base": "global",
                "category": "CustomProcess",
            },
        )

        assert (
            len(flujos) > 0
        ), f"No se ha encontrado el flujo: {nombre}. Verifique que sea un filtro LDAP válido."
        assert len(flujos) == 1, f"Se ha encontrado más de un servicio con: {nombre}"

        return flujos[0]["value"]

    def buscarGruposPorServicio(self, dn_servicio, profile_name, info):

        url = self.addr + "WSGroupServiceService?wsdl"
        client = self.get_client("group_client", url)

        grps = client.service.getGroupsByService(
            self.s, dn_servicio, profile_name, info
        )
        return grps
