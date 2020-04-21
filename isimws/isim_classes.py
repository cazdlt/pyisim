from zeep import Client,Settings
from zeep.xsd import Nil
import datetime
import exceptions
import pytz

class ProvisioningPolicy():
    """
        Para usar con el API SOAPWS de ISIM7
    """
    def __init__(self, sesion, name,description,entitlements,memberships,ou,priority=1,scope=2,enabled=True):

        url=sesion.addr+"WSProvisioningPolicyServiceService?wsdl"
        settings = Settings(strict=False)
        client=Client(url,settings=settings)
        self.pp_client=client

        self.description=description
        self.name=name
        self.entitlements=self.crearEntitlementList(sesion,entitlements)
        self.membership=****(sesion,memberships)
        self.ou=****(ou)
        self.priority=priority
        self.scope=scope
        self.enabled=enabled
        self.date=datetime.datetime.now(pytz.timezone('America/Bogota')).isoformat()

        

    def __str__(self):
        ret=f"Nombre: {self.name}\n"
        ret+=f"Descripción: {self.description}\n"
        ret+=f"OU: {self.ou.name}\n"
        ret+=f"Miembros: {list(map(lambda x: x.name,self.membership.item))}\n"
        ret+=f"Entitlements: {list(map(lambda x: x.serviceTarget.name,self.entitlements.item))}"
        
        return ret

    
    def crearEntitlementList(self,sesion,titularidades):
        """
            Recibe dict sacado de crear_politicas.leerCSV():
            {
                nombre_servicio1:{
                    "auto":[bool],
                    nombre_attr1:{
                        "enforcement":[default/allowed/mandatory/excluded]
                        "script":[bool]
                        "values[lista de valores/string con el script]
                    },
                    nombre_attr2:{
                        ...
                    }
                },
                nombre_servicio2:{
                    ...
                }
            }
        """ 
        
        client=self.pp_client
        
        itemFactory=client.type_factory('ns1')
        listFactory = client.type_factory('ns0')
        
        entitlement_list=[]
        
        for servicio,attrs in titularidades.items():
            
            if servicio=="*": #Todos los servicios
                servicio_dn="*"
                tipo_entitlement = 2

            elif "Profile" in servicio: #Todos los servicios de un perfil
                # servicio_dn=sesion.buscarPerfilServicio(servicio) no sirve búsqueda de perfiles
                servicio_dn=servicio
                tipo_entitlement = 0

            else: #Servicio específico
                servicio_dn=sesion.buscarServicio("Colpensiones",f"(erservicename={servicio})")["itimDN"]
                tipo_entitlement = 1

            serviceTarget=itemFactory.WSServiceTarget(name=servicio_dn,type=tipo_entitlement)
            
            type_= 1 if attrs["auto"] else 0
            process_dn=sesion.searchWorkflow(attrs["flujo"]) if attrs["flujo"] else None
            #print(process_dn)

            parameters=self.crearParameterList(client,attrs)

            wsentitlement=itemFactory.WSProvisioningPolicyEntitlement(ownershipType="Individual",type=type_,serviceTarget=serviceTarget,parameters=parameters,processDN=process_dn)
            entitlement_list.append(wsentitlement)

        
        ws_entitlement_list = listFactory.ArrayOf_tns1_WSProvisioningPolicyEntitlement(entitlement_list)

        return ws_entitlement_list

    def crearParameterList(self,client,atributos):
        itemFactory=client.type_factory('ns1')
        listFactory = client.type_factory('ns0')

        attrs=atributos.copy()
 
        attrs.pop("auto")
        attrs.pop("flujo")
        parameters=[]

        for name,params in attrs.items():

            is_script= "return " in params["values"][0] #params["script"]
            enforcement_map={
                "default":2,
                "allowed":1,
                "excluded":0,
                "mandatory":3,
                "optional":2,
            }

            if is_script:
                val = params["values"]
                enforce = [enforcement_map[params["enforcement"]]]
                types = [10]
            else:
                val = list(map(lambda s: f'"{s}"',params["values"])) #lo envuelve en ""
                enforce = [enforcement_map[params["enforcement"]]]*len(val)
                types = [0]*len(val)
                #print(val,enforce,types)

            assert enforce is not None,f"Enforcement no válido {name} - {enforce}"

            values=listFactory.ArrayOf_xsd_string(val)
            expressionTypes=listFactory.ArrayOf_xsd_int(types)
            enforcementTypes=listFactory.ArrayOf_xsd_int(enforce)

            param=itemFactory.WSServiceAttributeParameter(name=name,values=values,expressionTypes=expressionTypes,enforcementTypes=enforcementTypes)
            parameters.append(param)
        
        parameter_array=listFactory.ArrayOf_tns1_WSServiceAttributeParameter(parameters)
        wsparameters=itemFactory.WSProvisioningParameters(parameter_array)

        return wsparameters

    def crearMembershipList(self,sesion,memberships):
        """
        Si recibe *: Devuelve 2;*
        Si recibe lista con nombres de roles: Devuelve array[1;rol1, 2;rol2, ...]
        """
        client=self.pp_client

        membershipFactory=client.type_factory('ns1')
        listFactory = client.type_factory('ns0')

        if memberships[0]=="*":
            mem=membershipFactory.WSProvisioningPolicyMembership(name="*",type=2)
            membershipList = listFactory.ArrayOf_tns1_WSProvisioningPolicyMembership([mem])
        else:
            lista=[]
            for membership in memberships:
                role_dn=sesion.buscarRol(f"(errolename={membership})")["itimDN"]
                mem=membershipFactory.WSProvisioningPolicyMembership(name=role_dn,type=3)
                lista.append(mem)
            membershipList = listFactory.ArrayOf_tns1_WSProvisioningPolicyMembership(lista)

        return membershipList
    
    def crearEnSIM(self,sesion):

        client=self.pp_client

        itemFactory=client.type_factory('ns1')
        
        wspp=****(
            description=self.description,
            name=self.name,
            entitlements=self.entitlements,
            membership=****,
            priority=self.priority,
            scope=self.scope,
            enabled=self.enabled
        )

        del wspp["organizationalContainer"]
        del wspp["caption"]
        del wspp["itimDN"]
        del wspp["keywords"]

        r=sesion.crearPolitica(self.ou,wspp,self.date)

        return r

    def modificarEnSIM(self, sesion, old_pp):

        client=self.pp_client

        itemFactory=client.type_factory('ns1')
        
        wspp=****(
            description=self.description,
            name=self.name,
            entitlements=self.entitlements,
            membership=****,
            priority=self.priority,
            scope=self.scope,
            enabled=self.enabled,
            itimDN=old_pp["itimDN"],
            caption=old_pp["caption"],
            keywords=old_pp["keywords"]
        )

        del wspp["organizationalContainer"]

        r=sesion.modificarPolitica(self.ou,wspp,self.date)

        return r

class StaticRole():
    """
        Para usar con el API SOAPWS de ISIM7
        Los atributos se llenan correctamente únicamente al crear un nueva instancia de StaticRole
        Para enviar al API: 
            Instanciar con atributos necesarios
            llamar el método crearWSRole()
            llamar simsoap.crearRolEstatico() con lo retornado del método

        access_option:
            1: No acceso
            2: Acceso
            3: Acceso común
        
        classification:
            Empresarial
            Aplicacion

        access_category: El nombre de la categoría del acceso del rol tal como se ve en la consola de administración

        owner roles: Lista de nombres de roles dueños del acceso
        owner_cedulas: Lista de cédulas de personas dueñas del acceso

    """
    def __init__(self,sesion,name,description,ou,classification,access_option,access_category=None,owner_roles=None,owner_cedulas=None):
        
        self.name=name
        self.description=description
        self.ou=****(ou)

        assert classification in ["Empresarial","Aplicacion"],f"El rol {name} debe ser empresarial o de aplicación."
        if classification=="Empresarial":
            self.classification="role.classification.business"
        else:
            self.classification="role.classification.application"

        assert access_option in [1,2,3]
        self.access_option=access_option
        if access_option==2:
            assert access_category is not None,"Si el rol es acceso, debe darle una categoría"
            self.access_category=access_category
        
        self.owners=[]
        if owner_cedulas:
            for dueno in owner_cedulas:
                #print(dueno)
                self.owners.append(sesion.buscarPersona(f"(employeenumber={dueno})")["itimDN"])

        if owner_roles:
            for rol in owner_roles:
                #print(rol)
                self.owners.append(sesion.buscarRol(f"(errolename={rol})")["itimDN"])

    def crearAtributoRol(self,client,name,values):
        itemFactory=client.type_factory('ns1')
        listFactory = client.type_factory('ns0')

        values=listFactory.ArrayOf_xsd_string(values)

        attr=itemFactory.WSAttribute(name=name,operation=0,values=values,isEncoded=False)

        return attr

    def crearWSRole(self,sesion):

        """
            A partir de la información de la instancia, devuelve un objeto WSRole para entregárselo al API de ISIM 
        """

        url=sesion.addr+"WSRoleServiceService?wsdl"
        settings = Settings(strict=False)
        client=Client(url,settings=settings)

        itemFactory=client.type_factory('ns1')
        listFactory = client.type_factory('ns0')

        eraccesoption=self.crearAtributoRol(client,"eraccessoption",self.access_option)
        erRoleClassification=self.crearAtributoRol(client,"erRoleClassification",self.classification)

        if self.access_option in [2,3]:
            erObjectProfileName=self.crearAtributoRol(client,"erObjectProfileName",self.access_category)
            lista_atributos=[eraccesoption,erRoleClassification,erObjectProfileName]
        else:
            lista_atributos=[eraccesoption,erRoleClassification]

        if self.owners is not None:
            owner=self.crearAtributoRol(client,"owner",self.owners)
            lista_atributos.append(owner)

        array_attributes=listFactory.ArrayOf_tns1_WSAttribute(lista_atributos)

        role=itemFactory.WSRole(attributes=array_attributes,select=False,name=self.name,description=self.description)

        del role["itimDN"]
        return role

    def crearEnSIM(self,sesion):

        url=sesion.addr+"WSRoleServiceService?wsdl"
        settings = Settings(strict=False)
        client=Client(url,settings=settings)
        
        wsrole=self.crearWSRole(sesion)

        r=sesion.crearRolEstatico(wsrole,self.ou)

        return r

    def modificarEnSIM(self,sesion,role_dn):

        url=sesion.addr+"WSRoleServiceService?wsdl"
        settings = Settings(strict=False)
        client=Client(url,settings=settings)
        
        wsrole=self.crearWSRole(sesion)
        wsattributes=wsrole["attributes"]["item"]
        
        erparent=self.crearAtributoRol(client,"erparent",self.ou["itimDN"])
        description=self.crearAtributoRol(client,"description",wsrole["description"])
        
        wsattributes.append(erparent)
        wsattributes.append(description)

        #print(wsattributes)

        r=sesion.modificarRolEstatico(role_dn,wsattributes)

        return r
        
