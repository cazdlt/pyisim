from zeep import Client,Settings
from zeep.xsd import Nil
from isim_classes import StaticRole
import requests
import pprint
import exceptions

requests.packages.urllib3.disable_warnings()

class sim():
    def __init__(self, user_, pass_,env="int"):

        # colpensiones
        ambientes = {
            "int": "https://iam.appintegracion.loc:9082/itim/services/",
            "qa": "https://",
            # "pr":"https://"
        }

        self.addr = ambientes[env]
        self.s = self.login(user_, pass_)
        
    def login(self,user_,pass_):
        url=self.addr+"WSSessionService?wsdl"
        client=Client(url)
        sesion=client.service.login(user_,pass_)
        #print(sesion)
        return sesion

    def buscarOrganizacion(self,nombre):

        try:
            client=self.ou_client
        except AttributeError: #si el cliente de OUs no se ha inicializado
            url=self.addr+"WSOrganizationalContainerServiceService?wsdl"
            settings = Settings(strict=False)
            self.ou_client=Client(url,settings=settings)
            client=self.ou_client
        
        ous=client.service.searchContainerByName(self.s,Nil,"Organization",nombre)
        if len(ous)==0:
            ous=client.service.searchContainerByName(self.s,Nil,"OrganizationalUnit",nombre)
        
        assert len(ous)>0,f"No se ha encontrado la Unidad Organizativa de nombre: {nombre}. Verifique que sea un filtro LDAP válido."
        assert len(ous)==1,f"Se ha encontrado más de una Unidad Organizativa de nombre: {nombre}"
        return ous[0]

    def buscarPoliticaSuministro(self,wsou, nombre_politica, find_unique=True):
        """
           Si find_unique es True (por defecto): 
              lanza error si no encuentra ninguno o encuentra múltiples. 
              Devuelve instancia encontrada

           Si find_unique es False:
              No lanza errores
              Devuelve lista de resultados
        """           

        try:
            client=self.pp_client
        except AttributeError:
            url=self.addr+"WSProvisioningPolicyServiceService?wsdl"
            settings = Settings(strict=False)
            self.pp_client=Client(url,settings=settings)
            client=self.pp_client

        politicas=client.service.getPolicies(self.s,wsou,nombre_politica)

        if find_unique:
            assert len(politicas)>0,f"No se ha encontrado la política {nombre_politica}."
            assert len(politicas)==1,f"Se ha encontrado más de la política con: {nombre_politica}"
            return politicas[0]
        else:
            return politicas
        

    def crearPolitica(self,ou,wsprovisioningpolicy,date):
        
        try:
            client=self.pp_client
        except AttributeError:
            url=self.addr+"WSProvisioningPolicyServiceService?wsdl"
            settings = Settings(strict=False)
            self.pp_client=Client(url,settings=settings)
            client=self.pp_client

        s=client.service.createPolicy(self.s,ou,wsprovisioningpolicy,date)
        
        return s

    def modificarPolitica(self,ou,wsprovisioningpolicy,date):
        
        try:
            client=self.pp_client
        except AttributeError:
            url=self.addr+"WSProvisioningPolicyServiceService?wsdl"
            settings = Settings(strict=False)
            self.pp_client=Client(url,settings=settings)
            client=self.pp_client

        s=client.service.modifyPolicy(self.s,ou,wsprovisioningpolicy,date)
        
        return s
    
    def buscarRol(self,filtro,find_unique=True):
        """
           Si find_unique es True (por defecto): 
              lanza error si no encuentra ninguno o encuentra múltiples. 
              Devuelve instancia encontrada

           Si find_unique es False:
              No lanza errores
              Devuelve lista de resultados
        """

        try:
            client=self.role_client
        except AttributeError:
            url=self.addr+"WSRoleServiceService?wsdl"
            settings = Settings(strict=False)
            self.role_client=Client(url,settings=settings)
            client=self.role_client

        roles=client.service.searchRoles(self.s,filtro)

        if find_unique:
            assert len(roles)>0,f"No se ha encontrado el rol con el filtro: {filtro}. Verifique que sea un filtro LDAP válido."
            assert len(roles)==1,f"Se ha encontrado más de un rol con: {filtro}"
            return roles[0]
        else:
            return roles


    def crearRolEstatico(self,wsrole,wsou):

        try:
            client=self.role_client
        except AttributeError:
            url=self.addr+"WSRoleServiceService?wsdl"
            settings = Settings(strict=False)
            self.role_client=Client(url,settings=settings)
            client=self.role_client

        return client.service.createStaticRole(self.s,wsou,wsrole)

    def modificarRolEstatico(self,role_dn,wsattr_list):

        try:
            client=self.role_client
        except AttributeError:
            url=self.addr+"WSRoleServiceService?wsdl"
            settings = Settings(strict=False)
            self.role_client=Client(url,settings=settings)
            client=self.role_client

        return client.service.modifyStaticRole(self.s,role_dn,wsattr_list)

    def buscarPersona(self,filtro):

        try:
            client=self.person_client
        except AttributeError:
            url=self.addr+"WSPersonServiceService?wsdl"
            settings = Settings(strict=False)
            self.person_client=Client(url,settings=settings)
            client=self.person_client

        personas=client.service.searchPersonsFromRoot(self.s,filtro,Nil)
        
        assert len(personas)>0,f"No se ha encontrado la persona con el filtro: {filtro}. Verifique que sea un filtro LDAP válido."
        assert len(personas)==1,f"Se ha encontrado más de una persona con: {filtro}"
        return personas[0]

    def buscarServicio(self,parent_ou_name,filtro,find_unique=True):

        try:
            client=self.service_client
        except AttributeError:
            url=self.addr+"WSServiceServiceService?wsdl"
            settings = Settings(strict=False)
            self.service_client=Client(url,settings=settings)
            client=self.service_client

        ou=****(parent_ou_name)
        servicios=client.service.searchServices(self.s,ou,filtro)

        if find_unique:
            if len(servicios)==0:
                raise exceptions.NotFoundError(f"No se ha encontrado el servicio con el filtro: {parent_ou_name} - {filtro}. Verifique que sea un filtro LDAP válido.")
            assert len(servicios)==1,f"Se ha encontrado más de un servicio con: {parent_ou_name} - {filtro}"
            return servicios[0]
        else:
            return servicios
    
    def buscarPerfilServicio(self,nombre, find_unique=True):
        """
            NO FUNCIONA IBM DOCUMENT YOUR SHIT
            Busca el el perfil de servicio indicado por [nombre]
            Retorna el DN. 
        """

        try:
            client=self.search_client
        except AttributeError:
            url=self.addr+"WSSearchDataServiceService?wsdl"
            settings = Settings(strict=False)
            self.search_client=Client(url,settings=settings)
            client=self.search_client

        perfiles=client.service.findSearchControlObjects(self.s,{
                 "objectclass": "erServiceProfile", 
                 "contextDN": "ou=****,ou=****,ou=****,dc=colpensiones", 
                 "returnedAttributeName": "dn", 
                 "filter": f"(erObjectProfileName={nombre})", 
                 "base": "global",
                 "category":"ProfileService"
        })

        if find_unique:
            if len(perfiles)==0:
                raise exceptions.NotFoundError(f"No se ha encontrado el perfil: {nombre}. Verifique que sea un filtro LDAP válido.")
            assert len(perfiles)==1,f"Se ha encontrado más de un perfil de servicio con: {nombre}"
            return perfiles[0]["value"]
        else:
            return [p["value"] for p in perfiles]

    def searchWorkflow(self,nombre):
        """
            Busca flujos de cuenta y acceso por el nombre.
            Retorna el DN. 
        """

        try:
            client=self.search_client
        except AttributeError:
            url=self.addr+"WSSearchDataServiceService?wsdl"
            settings = Settings(strict=False)
            self.search_client=Client(url,settings=settings)
            client=self.search_client

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
        flujos=client.service.findSearchControlObjects(self.s,{
                 "objectclass": "erWorkflowDefinition", 
                 "contextDN": "ou=****,erglobalid=00000000000000000000,ou=****,dc=colpensiones", 
                 "returnedAttributeName": "dn", 
                 "filter": f"(erProcessName={nombre})", 
                 "base": "global",
                 "category":"CustomProcess"
        })

        assert len(flujos)>0,f"No se ha encontrado el flujo: {nombre}. Verifique que sea un filtro LDAP válido."
        assert len(flujos)==1,f"Se ha encontrado más de un servicio con: {nombre}"

        return flujos[0]["value"]

    

        
if __name__ == "__main__":
    sesion=sim("","")
    
    print(sesion.buscarRol("(errolename=WS)",find_unique=False))

    # print(sesion.buscarServicio("Colpensiones","(erservicename=Directorio Activo)"))
    
    # role=StaticRole(sesion,"Rol WS 4","Con dueño rol y humano","Aplicacion",2,"Aplicaciones_Colpensiones",owner_cedulas=["1015463230"],owner_roles=["Test Role"])
    # wsrole=role.crearWSRole(sesion)
    # print(wsrole)
    # ret=sesion.crearRolEstatico(wsrole,"Colpensiones")
    # print(ret)

    # print(sesion.buscarPersona("(employeenumber=1015463230)")["itimDN"])
    

   
    
