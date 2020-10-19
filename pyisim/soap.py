from zeep import Client, Settings
from zeep.xsd import Nil
from zeep.transports import Transport
from zeep.helpers import serialize_object
from zeep.cache import InMemoryCache

# from isim_classes import StaticRole
import requests
from pyisim.exceptions import NotFoundError

# from pyisim.entities import OrganizationalContainer


requests.packages.urllib3.disable_warnings()


class ISIMClient:
    def __init__(self, url, user_, pass_, cert_path=None):

        self.addr = url + "/itim/services/"
        self.cert_path = cert_path
        self.s = self.login(user_, pass_)

    def login(self, user_, pass_):
        url = self.addr + "WSSessionService?wsdl"
        assert self.cert_path is not None, "No certificate passed"
        client = self.get_client(url)
        session = client.service.login(user_, pass_)
        return session

    def get_client(self, url):

        # Si ya se inicializó el cliente especificado en client_name, lo devuelve. Si no, lo inicializa, setea y devuelve.
        # ej. -> https://<ITIMURL>/.../WSSessionService?wsdl -> wssessionservice
        client_name = url.split("/")[-1][:-5].lower()
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
        client = self.get_client(url)

        cont = client.service.lookupContainer(self.s, dn)

        return cont

    def buscarOrganizacion(self, perfil, nombre):

        url = self.addr + "WSOrganizationalContainerServiceService?wsdl"
        client = self.get_client(url)

        ous = client.service.searchContainerByName(self.s, Nil, perfil, nombre)

        return ous

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
        client = self.get_client(url)

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
        client = self.get_client(url)

        s = client.service.createPolicy(self.s, ou, wsprovisioningpolicy, date)

        return s

    def modificarPolitica(self, ou, wsprovisioningpolicy, date):

        url = self.addr + "WSProvisioningPolicyServiceService?wsdl"
        client = self.get_client(url)

        s = client.service.modifyPolicy(self.s, ou, wsprovisioningpolicy, date)

        return s

    def eliminarPolitica(self, ou, dn, date):
        url = self.addr + "WSProvisioningPolicyServiceService?wsdl"
        client = self.get_client(url)

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
        client = self.get_client(url)

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
        client = self.get_client(url)

        try:
            r = client.service.lookupRole(self.s, dn)
            return r
        except:
            raise NotFoundError("Rol no encontrado")

    def crearRolEstatico(self, wsrole, wsou):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client(url)

        return client.service.createStaticRole(self.s, wsou, wsrole)

    def modificarRolEstatico(self, role_dn, wsattr_list):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client(url)

        return client.service.modifyStaticRole(self.s, role_dn, wsattr_list)

    def eliminarRol(self, role_dn, date=None):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client(url)

        if date:
            raise NotImplementedError()
        else:
            date = Nil
        return client.service.removeRole(self.s, role_dn, date)

    def buscarPersona(self, filtro):

        url = self.addr + "WSPersonServiceService?wsdl"
        client = self.get_client(url)

        personas = client.service.searchPersonsFromRoot(self.s, filtro, Nil)

        assert (
            len(personas) > 0
        ), f"No se ha encontrado la persona con el filtro: {filtro}. Verifique que sea un filtro LDAP válido."
        assert len(personas) == 1, f"Se ha encontrado más de una persona con: {filtro}"
        return personas[0]

    def buscarServicio(self, ou, filtro, find_unique=True):

        url = self.addr + "WSServiceServiceService?wsdl"
        client = self.get_client(url)
        servicios = client.service.searchServices(self.s, ou, filtro)

        if find_unique:
            if len(servicios) == 0:
                raise NotFoundError(
                    f"No se ha encontrado el servicio con el filtro:  {filtro}. Verifique que sea un filtro LDAP válido."
                )
            assert (
                len(servicios) == 1
            ), f"Se ha encontrado más de un servicio con: {filtro}"
            return serialize_object(servicios[0], target_cls=dict)
        else:
            return [serialize_object(s, target_cls=dict) for s in servicios]

    def searchWorkflow(self, nombre, org_name):
        """
        Busca flujos de cuenta y acceso por el nombre.
        Retorna el DN.
        """

        url = self.addr + "WSSearchDataServiceService?wsdl"
        client = self.get_client(url)

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
        client = self.get_client(url)

        grps = client.service.getGroupsByService(
            self.s, dn_servicio, profile_name, info
        )
        return grps

    def buscarActividadesRecursivo(self, process_id, act_list):
        url = self.addr + "WSRequestServiceService?wsdl"
        client = self.get_client(url)

        acts = client.service.getActivities(self.s, int(process_id), False)
        act_list.extend(acts)

        subprocesses = client.service.getChildProcesses(self.s, int(process_id))
        for s in subprocesses:
            self.buscarActividadesRecursivo(s.requestId, act_list)
        return "ok"

    def buscarActividadesDeSolicitud(self, process_id):
        """
        The customer can accomplish this by using a combination of getActivities() and getChildProcesses().
        """
        # url = self.addr + "WSRequestServiceService?wsdl"
        # client = self.get_client(url)

        actividades = []
        self.buscarActividadesRecursivo(int(process_id), actividades)

        # Filtra solo las actividades manuales (M) y pendientes (R)
        manuales_pendientes = [
            a for a in actividades if a.activityType == "M" and a.state == "R"
        ]

        # acts = client.service.getActivities(self.s, int(process_id), True)
        # subprocesses
        return manuales_pendientes

    def suspenderPersona(self, dn, justification):
        # suspendPerson(session: ns1:WSSession, personDN: xsd:string, justification: xsd:string)
        url = self.addr + "WSPersonServiceService?wsdl"
        client = self.get_client(url)

        r = client.service.suspendPerson(self.s, dn, justification)
        return r

    def restaurarPersona(self, dn, justification):
        # restorePerson(password: xsd:string, date: xsd:dateTime, justification: xsd:string) -> restorePersonReturn: ns1:WSRequest
        url = self.addr + "WSPersonServiceService?wsdl"
        client = self.get_client(url)

        r = client.service.restorePerson(self.s, dn, True, Nil, Nil, justification)
        return r

    def eliminarPersona(self, dn, justification):
        # deletePerson(session: ns1:WSSession, personDN: xsd:string, date: xsd:dateTime, justification: xsd:string) -> deletePersonReturn: ns1:WSRequest
        url = self.addr + "WSPersonServiceService?wsdl"
        client = self.get_client(url)

        r = client.service.deletePerson(self.s, dn, Nil, justification)
        return r

    def crearRolDinamico(self, wsrole, wsou, date=None):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client(url)

        if date:
            raise NotImplementedError()
        else:
            date = Nil

        return client.service.createDynamicRole(self.s, wsou, wsrole, date)

    def modificarRolDinamico(self, role_dn, wsattr_list, date=None):

        url = self.addr + "WSRoleServiceService?wsdl"
        client = self.get_client(url)

        if date:
            raise NotImplementedError()
        else:
            date = Nil

        return client.service.modifyDynamicRole(self.s, role_dn, wsattr_list, date)

    def getDefaultAccountAttributesByPerson(self, service_dn, person_dn):
        url = self.addr + "WSAccountServiceService?wsdl"
        client = self.get_client(url)

        r = client.service.getDefaultAccountAttributesByPerson(
            self.s, service_dn, person_dn
        )
        return serialize_object(r, target_cls=dict)

    def getDefaultAccountAttributes(self, service_dn):
        url = self.addr + "WSAccountServiceService?wsdl"
        client = self.get_client(url)

        r = client.service.getDefaultAccountAttributes(self.s, service_dn)
        return serialize_object(r, target_cls=dict)

    def getAccountProfileForService(self, service_dn):
        url = self.addr + "WSAccountServiceService?wsdl"
        client = self.get_client(url)

        r = client.service.getAccountProfileForService(self.s, service_dn)
        return r

    def searchAccounts(self, search_arguments):
        url = self.addr + "WSAccountServiceService?wsdl"
        client = self.get_client(url)

        search_arguments = {k: v for k, v in search_arguments.items() if v is not None}

        r = client.service.searchAccounts(self.s, search_arguments)
        return serialize_object(r, target_cls=dict)

    # createAccount(session: ns1:WSSession, serviceDN: xsd:string, wsAttrs: ns1:WSAttribute[], date: xsd:dateTime, justification: xsd:string) -> createAccountReturn: ns1:WSRequest
    def createAccount(self, service_dn, wsattrs, date, justification):
        url = self.addr + "WSAccountServiceService?wsdl"
        client = self.get_client(url)

        if date:
            raise NotImplementedError()
        else:
            date=Nil

        r = client.service.createAccount(
            self.s, service_dn, wsattrs, date, justification
        )
        return serialize_object(r, target_cls=dict)
