import datetime
from collections import defaultdict

from isimws.exceptions import *


class ProvisioningPolicy:
    """
    Para usar con el API SOAPWS de ISIM7
    """

    def __init__(
        self,
        sesion,
        provisioning_policy=None,
        policy_attrs=None,
    ):
        """Initializes ProvisioningPolicy object

        Args:
            sesion (isimws.Session): Custom ISIM/ Default ISIM Session
            policy_attrs(dict):
                name (str): policy name
                description (str): policy description
                entitlements (dict): {
                    service_dn/service_profile_name/*:{
                        "automatic":True/False,
                        "workflow":account_request_workflow_name/None,
                        "parameters:{
                            attr_name:[
                                    {
                                        "enforcement":enforcement_type (allowed/mandatory/default/excluded),
                                        "type":parameter_type (constant/regex/null/script)
                                        "values": attribute_value (None, str for regex/script, list for constant values),
                                    },
                                    {... more values}
                                ],
                            {... more attributes}
                        }
                    },
                    {... more services}
                }
                memberships (list): list of role DNs or ["*"] if everyone. TYPE 4 NOT SUPPORTED (Everyone that's not entitled through other policies NOT SUPPORTED)
                parent (isimws.entities.OrganizationalContainer): parent container
                priority (int): policy priority.
                scope (int, optional): policy scope (1=ONE_LEVEL / 2=SUBTREE). Defaults to 2.
                enabled (bool, optional): Defaults to True.
                caption(str,optional): Defaults to "".
                keywords(str,optional): Defaults to "".
        """

        # sesion = sesion.soapclient
        url = sesion.soapclient.addr + "WSProvisioningPolicyServiceService?wsdl"
        self.__pp_client = sesion.soapclient.get_client(url)

        local_tz = datetime.datetime.now().astimezone().tzinfo
        self.date = datetime.datetime.now(local_tz).isoformat()

        if policy_attrs:
            self.description = policy_attrs["description"]
            self.name = policy_attrs["name"]
            self.ou = policy_attrs["parent"]  # .wsou
            self.entitlements = policy_attrs["entitlements"]
            self.membership = policy_attrs["memberships"]

            # probando
            # self.entitlements = self.__crearEntitlementList(
            #     sesion.soapclient, policy_attrs["entitlements"]
            # )
            # self.membership = self.__crearMembershipList(
            #     sesion.soapclient, policy_attrs["memberships"]
            # )
            self.priority = policy_attrs["priority"]
            self.scope = (
                policy_attrs["scope"] if "scope" in policy_attrs else 2
            )  # 1=ONE_LEVEL, 2=SUBTREE
            self.enabled = (
                policy_attrs["enabled"] if "enabled" in policy_attrs else True
            )
            self.caption = policy_attrs["caption"] if "caption" in policy_attrs else ""
            self.keywords = (
                policy_attrs["keywords"] if "keywords" in policy_attrs else ""
            )

        else:

            # if dn: no hay método de lookup en sim
            #     rol=sesion.lookupProvisioningPolicy(dn)
            self.description = provisioning_policy["description"]
            self.name = provisioning_policy["name"]
            self.dn = provisioning_policy["itimDN"]
            self.ou = OrganizationalContainer(
                sesion, dn=provisioning_policy["organizationalContainer"]["itimDN"]
            )
            self.priority = provisioning_policy["priority"]
            self.scope = provisioning_policy["scope"]

            # self.entitlements = provisioning_policy["entitlements"]
            # for titularidad in self.entitlements.item:
            #     if titularidad.parameters.parameters is None:
            #         titularidad.parameters.parameters = {"item": []}

            self.entitlements = self.__traducirWSEntitlements(
                sesion.soapclient, provisioning_policy["entitlements"]
            )
            self.membership = [
                m["name"] for m in provisioning_policy["membership"]["item"]
            ]

            self.caption = provisioning_policy["caption"]
            self.keywords = provisioning_policy["keywords"]
            self.enabled = provisioning_policy["enabled"]

    def __traducirWSEntitlements(self, sesion, wsentitlements):
        """
        Convierte WSEntitlements en diccionario estándar para poder modificar
        Retorna:
        entitlements (dict): {
            service_dn/service_profile_name/*:{
                "automatic":True/False,
                "workflow":account_request_workflow_name/None,
                "parameters:[
                    attr_name:[
                            {
                                "enforcement":enforcement_type (allowed/mandatory/default/excluded),
                                "type":parameter_type (constant/regex/null/script)
                                "values": attribute_value (None, str for regex/script, list for constant values),
                            },
                            {... more values}
                        ],
                    {... more attributes}
                ]
            },
            {... more services}
        }
        """

        enforcement_mapping = {
            2: "default",
            1: "allowed",
            0: "excluded",
            3: "mandatory",
        }

        type_mapping = {
            0: "constant",
            10: "script",
            20: "regex",
        }

        entitlements = {}
        for titularidad in wsentitlements["item"]:
            service = titularidad["serviceTarget"]["name"]
            workflow = titularidad["processDN"]
            automatic = titularidad["type"] == 1
            wsparams = titularidad["parameters"]["parameters"]
            if not wsparams:
                parameters = {}
            else:
                parameters = {}
                for param in wsparams["item"]:
                    attr_name = param.name
                    values = param.values.item
                    types = param.expressionTypes.item
                    enforcement = param.enforcementTypes.item
                    attr_values = list(zip(values, enforcement, types))
                    attr_values = [
                        {
                            "enforcement": enforcement_mapping[val[1]],
                            "type": "constant"
                            if val[0][0] == val[0][-1] == '"'
                            else "null"
                            if val[0] == "return null;"
                            else type_mapping[val[2]],
                            "values": [val[0][1:-1]]
                            if val[0][0] == val[0][-1] == '"'
                            else None
                            if val[0] == "return null;"
                            else val[0],
                        }
                        for val in attr_values
                    ]

                    parameters[attr_name] = attr_values

            entitlements[service] = {
                "workflow": workflow,
                "automatic": automatic,
                "parameters": parameters,
            }

        return entitlements

    def __crearEntitlementList(self, sesion, titularidades):
        """
        {
            service_dn/service_profile_name/*:{
                "automatic":True/False,
                "workflow":account_request_workflow_name/None,
                "parameters:[
                    attr_name:[
                            {
                                "enforcement":enforcement_type (allowed/mandatory/default/excluded),
                                "type":parameter_type (constant/regex/null/script)
                                "values": attribute_value (None, str: for regex/script, list: for constant value),
                            },
                            {... more values}
                        ],
                    {... more attributes}
                ]
            },
            {... more services}
        }
        """
        # sesion=sesion.soapclient
        client = self.__pp_client

        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        entitlement_list = []

        for servicio, attrs in titularidades.items():

            if servicio == "*":  # Todos los servicios
                servicio_dn = "*"
                tipo_entitlement = 2

            elif "profile" in servicio.lower():  # Todos los servicios de un perfil
                # servicio_dn=sesion.buscarPerfilServicio(servicio) no sirve búsqueda de perfiles
                servicio_dn = servicio
                tipo_entitlement = 0

            else:  # Servicio específico
                servicio_dn = servicio
                tipo_entitlement = 1

            serviceTarget = itemFactory.WSServiceTarget(
                name=servicio_dn, type=tipo_entitlement
            )

            type_ = 1 if attrs["automatic"] else 0
            process_dn = (
                sesion.searchWorkflow(attrs["workflow"], self.ou.name)
                if attrs["workflow"]
                else None
            )
            # print(process_dn)

            parameters = self.__crearParameterList(client, attrs["parameters"])

            wsentitlement = itemFactory.WSProvisioningPolicyEntitlement(
                ownershipType="Individual",
                type=type_,
                serviceTarget=serviceTarget,
                parameters=parameters,
                processDN=process_dn,
            )
            entitlement_list.append(wsentitlement)

        ws_entitlement_list = listFactory.ArrayOf_tns1_WSProvisioningPolicyEntitlement(
            entitlement_list
        )

        return ws_entitlement_list

    def __crearParameterList(self, client, atributos):
        """
        {
             attr_name:[
                     {
                         "enforcement":enforcement_type (allowed/mandatory/default/excluded),
                         "type":parameter_type (constant/regex/null/script)
                         "values": attribute_value (None, str: for regex/script, list: for constant value),
                     },
                     {... more values}
                 ],
             {... more attributes}
         }
        """
        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        attrs = atributos.copy()

        parameters = []

        enforcement_map = {
            "default": 2,
            "allowed": 1,
            "excluded": 0,
            "mandatory": 3,
            "optional": 2,
        }

        type_map = {
            "constant": 0,
            "script": 10,
            "regex": 20,
            "null": 10,
        }

        for name, values in attrs.items():
            attr_values = []
            for value in values:
                if "constant" in value["type"].lower():
                    val = [f'"{s}"' for s in value["values"]]
                    enforce = [enforcement_map[value["enforcement"].lower()]] * len(val)
                    tipo = [0] * len(val)
                elif "null" in value["type"].lower():
                    val = ["return null;"]
                    enforce = [enforcement_map[value["enforcement"].lower()]]
                    tipo = [10]
                else:
                    val = [value["values"]]
                    enforce = [enforcement_map[value["enforcement"].lower()]]
                    tipo = [type_map[value["type"].lower()]]

                attr_values.append((val, enforce, tipo))

            # organiza la info al formato requerido (listas planas separadas)
            values, enforcements, types = list(zip(*attr_values))

            values = [item for elem in values for item in elem]
            enforcements = [item for elem in enforcements for item in elem]
            types = [item for elem in types for item in elem]

            values = listFactory.ArrayOf_xsd_string(values)
            expressionTypes = listFactory.ArrayOf_xsd_int(types)
            enforcementTypes = listFactory.ArrayOf_xsd_int(enforcements)

            param = itemFactory.WSServiceAttributeParameter(
                name=name,
                values=values,
                expressionTypes=expressionTypes,
                enforcementTypes=enforcementTypes,
            )
            parameters.append(param)

        parameter_array = listFactory.ArrayOf_tns1_WSServiceAttributeParameter(
            parameters
        )
        wsparameters = itemFactory.WSProvisioningParameters(parameter_array)

        return wsparameters

    def __crearMembershipList(self, sesion, memberships):
        """
        Si recibe ["*"]: Devuelve 2;*
        Si recibe lista con nombres de roles: Devuelve array[1;rol1, 2;rol2, ...]
        """
        # sesion=sesion.soapclient
        client = self.__pp_client

        membershipFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        if not memberships:
            raise Exception("La política debe tener al menos un miembro.")
        elif memberships[0] == "*":
            mem = membershipFactory.WSProvisioningPolicyMembership(name="*", type=2)
            membershipList = listFactory.ArrayOf_tns1_WSProvisioningPolicyMembership(
                [mem]
            )
        else:
            lista = []
            for membership in memberships:
                role_dn = membership
                mem = membershipFactory.WSProvisioningPolicyMembership(
                    name=role_dn, type=3
                )
                lista.append(mem)
            membershipList = listFactory.ArrayOf_tns1_WSProvisioningPolicyMembership(
                lista
            )

        return membershipList

    def crear(self, sesion):
        sesion = sesion.soapclient
        client = self.__pp_client

        itemFactory = client.type_factory("ns1")

        ents = self.__crearEntitlementList(sesion, self.entitlements)
        membs = self.__crearMembershipList(sesion, self.membership)
        wspp = itemFactory.WSProvisioningPolicy(
            description=self.description,
            name=self.name,
            entitlements=ents,
            membership=membs,
            priority=self.priority,
            scope=self.scope,
            enabled=self.enabled,
        )

        del wspp["organizationalContainer"]
        del wspp["itimDN"]

        r = sesion.crearPolitica(self.ou.wsou, wspp, self.date)

        # la respuesta no envía el DN, entonces no se puede meter de una
        return r

    def modificar(self, sesion, changes={}):
        sesion = sesion.soapclient
        client = self.__pp_client

        itemFactory = client.type_factory("ns1")

        for attr,value in changes.items():
            setattr(self,attr,value)

        ents = self.__crearEntitlementList(sesion, self.entitlements)
        membs = self.__crearMembershipList(sesion, self.membership)

        wspp = itemFactory.WSProvisioningPolicy(
            description=self.description,
            name=self.name,
            entitlements=ents,
            membership=membs,
            priority=self.priority,
            scope=self.scope,
            enabled=self.enabled,
            itimDN=self.dn,
            caption=self.caption,
            keywords=self.keywords,
        )

        del wspp["organizationalContainer"]

        r = sesion.modificarPolitica(self.ou.wsou, wspp, self.date)

        return r

    def eliminar(self, sesion):
        sesion = sesion.soapclient
        r = sesion.eliminarPolitica(self.ou.wsou, self.dn, self.date)
        return r


class StaticRole:
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

    def __init__(
        self,
        sesion,
        dn=None,
        rol=None,
        role_attrs=None,
    ):
        """

        Args:
            sesion (isimws.Session): session object
            id (str): for role lookup
            rol (zeep.WSRole): for initialization after search
            role_attrs (dict):      name,
                                    description,
                                    parent (isimws.entities.OrganizationalContainer),
                                    classification: str (eg. role.classification.business). Defaults to "".
                                    access_option (int): 1: disable / 2: enable / 3: shared access
                                    access_category: access category. Defaults to None.
                                    owners: list of owner DNs. can be people or roles. Defaults to [].
        """
        # sesion = sesion.soapclient

        url = sesion.soapclient.addr + "WSRoleServiceService?wsdl"

        self.__role_client = sesion.soapclient.get_client(url)

        if role_attrs:

            self.name = role_attrs["name"]
            self.description = role_attrs["description"]
            self.ou = role_attrs["parent"]
            self.classification = (
                role_attrs["classification"] if role_attrs["classification"] else ""
            )

            role_attrs["access_option"]=str(role_attrs["access_option"])
            if role_attrs["access_option"] not in ["1", "2", "3"]:
                raise ValueError(
                    "Access option must be an int. 1: disable / 2: enable / 3: shared access"
                )
            self.access_option = role_attrs["access_option"]

            if role_attrs["access_option"] in ["2", "3"]:
                if not role_attrs["access_category"]:
                    raise ValueError("Si el rol es acceso, debe darle una categoría")
                self.access_category = role_attrs["access_category"]

            self.owners = role_attrs["owners"] if role_attrs["owners"] else []

        else:
            if dn:
                rol = sesion.soapclient.lookupRole(dn)

            self.name = rol["name"]
            self.description = rol["description"]
            self.dn = rol["itimDN"]

            attrs = {
                attr["name"]: [i for i in attr["values"]["item"]]
                for attr in rol["attributes"]["item"]
            }
            attrs = defaultdict(list, attrs)
            ou = attrs["erparent"][0]  # dn del contenedor
            self.parent=OrganizationalContainer(sesion,dn=ou)
            if attrs["erroleclassification"]:
                self.classification = attrs["erroleclassification"][0]
            if attrs["eraccessoption"]:
                self.access_option = attrs["eraccessoption"][0]
            if attrs["erobjectprofilename"]:
                self.access_category = attrs["erobjectprofilename"][0]
            self.owners = attrs["owner"]

    def crearAtributoRol(self, client, name, values):
        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        values = listFactory.ArrayOf_xsd_string(values)

        attr = itemFactory.WSAttribute(
            name=name, operation=0, values=values, isEncoded=False
        )

        return attr

    def crearWSRole(self, sesion):

        """
        A partir de la información de la instancia, devuelve un objeto WSRole para entregárselo al API de ISIM
        """
        # sesion=sesion.soapclient
        client = self.__role_client

        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        eraccesoption = self.crearAtributoRol(
            client, "eraccessoption", self.access_option
        )
        erRoleClassification = self.crearAtributoRol(
            client, "erRoleClassification", self.classification
        )

        if self.access_option in ["2", "3"]:
            erObjectProfileName = self.crearAtributoRol(
                client, "erObjectProfileName", self.access_category
            )
            lista_atributos = [eraccesoption, erRoleClassification, erObjectProfileName]
        else:
            lista_atributos = [eraccesoption, erRoleClassification]

        if self.owners is not None:
            owner = self.crearAtributoRol(client, "owner", self.owners)
            lista_atributos.append(owner)

        array_attributes = listFactory.ArrayOf_tns1_WSAttribute(lista_atributos)

        role = itemFactory.WSRole(
            attributes=array_attributes,
            select=False,
            name=self.name,
            description=self.description,
        )

        del role["itimDN"]
        # del role["erparent"]
        return role

    def crear(self, sesion):
        sesion = sesion.soapclient

        # client = self.__role_client

        wsrole = self.crearWSRole(sesion)

        r = sesion.crearRolEstatico(wsrole, self.ou.wsou)

        self.dn = r["itimDN"]
        return r

    def modificar(self, sesion,changes={}):
        sesion = sesion.soapclient
        # url = sesion.addr + "WSRoleServiceService?wsdl"
        client = self.__role_client

        for attr,value in changes.items():
            setattr(self,attr,value)

        wsrole = self.crearWSRole(sesion)
        wsattributes = wsrole["attributes"]["item"]

        errolename = self.crearAtributoRol(client, "errolename", self.name)
        description = self.crearAtributoRol(
            client, "description", wsrole["description"]
        )

        wsattributes.append(errolename)
        wsattributes.append(description)

        # print(wsattributes)

        r = sesion.modificarRolEstatico(self.dn, wsattributes)

        return r

    def eliminar(self, sesion, fecha=None):
        if fecha:
            raise NotImplementedError(
                "No se ha implementado la programación de tareas."
            )

        r = sesion.soapclient.eliminarRolEstatico(self.dn, fecha)

        return r


class OrganizationalContainer:
    def __init__(self, sesion, dn=None, organizational_container=None):
        if dn:
            self.wsou = sesion.soapclient.lookupContainer(dn)
            self.name = self.wsou.name
            self.dn = self.wsou["itimDN"]
            self.profile_name = self.wsou["profileName"]

            rest_profile_names={
                "BusinessPartnerOrganization":"bporganizations",
                "OrganizationalUnit":"organizationunits",
                "Organization":"organizations",
                "Location":"locations",
                "AdminDomain":"admindomains",
            }
            self.href=sesion.restclient.buscarOUs(rest_profile_names[self.profile_name],self.name)[0]["_links"]["self"]["href"]

        elif organizational_container:
            self.name = organizational_container["_links"]["self"]["title"]
            self.href = organizational_container["_links"]["self"]["href"]
            self.dn = organizational_container["_attributes"]["dn"]
            self.wsou = sesion.soapclient.lookupContainer(self.dn)
            self.profile_name = self.wsou["profileName"]

    def __eq__(self, o) -> bool:
        return self.dn==o.dn


class Person:

    profile_name = "Person"

    def __init__(self, sesion, person=None, href=None, person_attrs=None):

        self.changes = {}

        if person:
            self.href = person["_links"]["self"]["href"]
            self.dn = sesion.restclient.lookupPersona(self.href, attributes="dn")[
                "_attributes"
            ]["dn"]
            person_attrs = person["_attributes"]

        elif href:
            r = sesion.restclient.lookupPersona(href, attributes="*")
            assert (
                r["_links"]["self"]["href"] == href
            ), "Persona no encontrada o inválida"

            self.href = href
            self.dn = sesion.restclient.lookupPersona(self.href, attributes="dn")[
                "_attributes"
            ]["dn"]
            person_attrs = r["_attributes"]

        for k, v in person_attrs.items():
            setattr(self, k, v)

    def __setattr__(self, attr, val):
        if hasattr(self, attr):
            self.changes[attr] = val
        super().__setattr__(attr, val)

    def __init_subclass__(cls):

        try:
            getattr(cls, "profile_name")
        except AttributeError:
            raise TypeError(
                f"All classes based on the Person entity need their profile specified (Person/BPPerson/Your custom profile) in the profile_name attribute"
            )

        return super().__init_subclass__()

    def crear(self, sesion, parent: OrganizationalContainer, justificacion):
        orgid = parent.href.split("/")[-1]
        ret = sesion.restclient.crearPersona(self, orgid, justificacion)
        return ret

    def modificar(self, sesion, justificacion, changes={}):
        try:
            href = self.href
            
            self.changes.update(changes)
            # for attr,value in changes.items():
            #     setattr(self,attr,value)

            ret = sesion.restclient.modificarPersona(
                self.href, self.changes, justificacion
            )
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def solicitar_accesos(self, sesion, accesos, justificacion):

        ret = {}
        if len(accesos) > 0:
            ret = sesion.restclient.solicitarAccesos(accesos, self, justificacion)
        return ret

    def suspender(self, sesion, justificacion):

        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = sesion.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = sesion.soapclient.suspenderPersona(dn, justificacion)
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def restaurar(self, sesion, justificacion):
        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = sesion.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = sesion.soapclient.restaurarPersona(self.dn, justificacion)
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def eliminar(self, sesion, justificacion):

        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = sesion.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = sesion.soapclient.eliminarPersona(self.dn, justificacion)
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )


class Activity:
    def __init__(self, sesion, activity=None, id=None):

        if id:
            activity = sesion.restclient.lookupActividad(str(id))
            if "_attributes" not in activity.keys():
                raise NotFoundError(f"Actividad no encontrada {id}")

        self.request_href = activity["_links"]["request"]["href"]
        self.href = activity["_links"]["self"]["href"]
        self.workitem_href = activity["_links"]["workitem"]["href"]
        self.name = activity["_attributes"]["name"]
        self.type = activity["_attributes"]["type"]
        self.status = activity["_attributes"]["status"]["key"].split(".")[-1]
        self.requestee = activity["_links"]["requestee"]["title"]

    def completar(self, sesion, resultado, justificacion):
        """Permite OTs, Aprobaciones, RFIs"""
        act_dict = {"_attributes": {}, "_links": {"workitem": {}}}
        act_dict["_attributes"]["type"] = self.type
        act_dict["_attributes"]["name"] = self.name
        act_dict["_links"]["workitem"]["href"] = self.workitem_href

        assert self.status == "PENDING", "La actividad ya ha sido completada."
        r = sesion.restclient.completarActividades([act_dict], resultado, justificacion)

        return r


class Access:
    def __init__(self, access=None):

        if access:
            self.href = access["_links"]["self"]["href"]
            self.name = access["_links"]["self"]["title"]


class Service:
    def __init__(self, sesion, service=None):

        # if id:
        #     service=sesion.restclient.lookupServicio(str(id))
        #     if "_attributes" not in service.keys():
        #         raise NotFoundError(f"Servicio no encontrado {id}")

        if service:
            self.dn = service["itimDN"]
            self.profile_name = service["profileName"]
            self.name = service["name"]


class Group:
    def __init__(self, sesion, group=None):
        if group:
            self.name = group["name"]
            self.dn = group["itimDN"]
            self.id = group["id"]
            self.description = group["description"]
            self.profile_name = group["profileName"]
            self.attributes = {
                attr.name: [v for v in attr.values.item]
                for attr in group.attributes.item
            }
