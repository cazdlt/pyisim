import dataclasses
import datetime
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from .organizational_container import OrganizationalContainer
from ..response import Response

if TYPE_CHECKING:
    from ..auth import Session


@dataclasses.dataclass
class ProvisioningPolicyParameterValue:
    enforcement: Literal["allowed", "mandatory", "default", "excluded"]
    """
    Parameter enforcement type
    """
    type: Literal["constant", "regex", "null", "script"]
    """
    Parameter type
    """
    values: Union[None, str, list]
    """
    Parameter values

    Options:

    * str if type is regex or script
    * list if type is constant value
    * can be None if type is null

    """


@dataclasses.dataclass
class ProvisioningPolicyEntitlementValue:

    automatic: bool
    """
    True if entitlement is automatic
    """
    parameters: Dict[str, List[ProvisioningPolicyParameterValue]]
    """
    Dictionary representing entitlement parameters:

    * Keys: parameter name (attribute name)
    * Values: List of parameter values for each attribute.
    """
    workflow: Optional[str] = None
    """
    Account request workflow name.
    Optional. Defaults to None.
    """


@dataclasses.dataclass
class ProvisioningPolicyAttributes:

    name: str
    """
    Provisioning Policy name
    """

    description: str
    """
    Provisioning Policy description
    """

    parent: OrganizationalContainer
    """
    Provisioning Policy Business Unit
    """

    entitlements: Dict[str, ProvisioningPolicyEntitlementValue]
    """
    Dictionary of policy entitlements:

    * Keys (str): service dn / service profile name / "*" for all services
    * Values: Entitlement values for the target 
    """

    memberships: List[str]
    """
    Provisioning Policy membership list.

    Options:

    * List of role DNs
    * "*" for everyone
    * "Everyone that's not entitled through other policies" is not supported yet
    """

    priority: int
    """
    Provisioning Policy priority.
    Integer between 1 and 10000000
    """

    scope: Literal[1, 2] = 2
    """
    Provisioning Policy scope.
    Defaults to 2.

    Options:

    * 1: One level
    * 2: Subtree
    """

    enabled: bool = True
    """
    Optional. Defaults to true.
    """

    caption: str = ""
    """
    Provisioning Policy caption.
    Optional. Defaults  to "".
    """

    keywords: str = ""
    """
    Provisioning Policy keywords.
    Optional. Defaults  to "".
    """


class ProvisioningPolicy:
    def __init__(
        self,
        session: "Session",
        provisioning_policy=None,
        policy_attrs: Union[ProvisioningPolicyAttributes, Dict] = None,
    ):
        """
        Args:
            session (pyisim.Session): Custom / Default ISIM Session
            provisioning_policy (zeep.xsd.ProvisioningPolicy): SOAP ProvisioningPolicy object to initialize after search operations
            policy_attrs(dict or ProvisioningPolicyAttributes): Provisioning Policy attributes for initialization
        """

        # session = session.soapclient
        url = session.soapclient.addr + "WSProvisioningPolicyServiceService?wsdl"
        self.__pp_client = session.soapclient.get_client(url)

        local_tz = datetime.datetime.now().astimezone().tzinfo
        self.date = datetime.datetime.now(local_tz).isoformat()

        if dataclasses.is_dataclass(policy_attrs):
            policy_attrs = dataclasses.asdict(policy_attrs)

        if policy_attrs:
            self.description = policy_attrs["description"]
            self.name = policy_attrs["name"]
            self.ou = policy_attrs["parent"]  # .wsou
            self.entitlements = policy_attrs["entitlements"]
            self.membership = policy_attrs["memberships"]

            # probando
            # self.entitlements = self.__crearEntitlementList(
            #     session.soapclient, policy_attrs["entitlements"]
            # )
            # self.membership = self.__crearMembershipList(
            #     session.soapclient, policy_attrs["memberships"]
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
            #     rol=session.lookupProvisioningPolicy(dn)
            self.description = provisioning_policy["description"]
            self.name = provisioning_policy["name"]
            self.dn = provisioning_policy["itimDN"]
            self.ou = OrganizationalContainer(
                session, dn=provisioning_policy["organizationalContainer"]["itimDN"]
            )
            self.priority = provisioning_policy["priority"]
            self.scope = provisioning_policy["scope"]

            # self.entitlements = provisioning_policy["entitlements"]
            # for titularidad in self.entitlements.item:
            #     if titularidad.parameters.parameters is None:
            #         titularidad.parameters.parameters = {"item": []}

            self.entitlements = self.__traducirWSEntitlements(
                session.soapclient, provisioning_policy["entitlements"]
            )
            self.membership = [
                m["name"] for m in provisioning_policy["membership"]["item"]
            ]

            self.caption = provisioning_policy["caption"]
            self.keywords = provisioning_policy["keywords"]
            self.enabled = provisioning_policy["enabled"]

    def __traducirWSEntitlements(self, session, wsentitlements):
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

    def __crearEntitlementList(self, session, titularidades):
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
        # session=session.soapclient
        client = self.__pp_client

        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        entitlement_list = []

        for servicio, attrs in titularidades.items():

            if servicio == "*":  # Todos los servicios
                servicio_dn = "*"
                tipo_entitlement = 2

            elif "profile" in servicio.lower():  # Todos los servicios de un perfil
                # servicio_dn=session.buscarPerfilServicio(servicio) no sirve búsqueda de perfiles
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
                session.searchWorkflow(attrs["workflow"], self.ou.name)
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

    def __crearMembershipList(self, session, memberships):
        """
        Si recibe ["*"]: Devuelve 2;*
        Si recibe lista con nombres de roles: Devuelve array[1;rol1, 2;rol2, ...]
        """
        # session=session.soapclient
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

    def add(self, session: "Session") -> Response:
        """
        Requests to add provisioning policy into ISIM

        Args:
            session (Session): Active ISIM Session

        Returns:
            Response: ISIM API Response
        """
        session = session.soapclient
        client = self.__pp_client

        itemFactory = client.type_factory("ns1")

        ents = self.__crearEntitlementList(session, self.entitlements)
        membs = self.__crearMembershipList(session, self.membership)
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

        r = session.crearPolitica(self.ou.wsou, wspp, self.date)

        # la respuesta no envía el DN, entonces no se puede meter de una
        return Response(session, r)

    def modify(self, session: "Session", changes={}):
        """
        Requests to modify the provisioning policy in ISIM.
        Policy needs to be initialized (must have a DN attribute)

        Changes can be done through the changes dictionary or by modifying the instance attributes directly

        Args:
            session (Session): Active ISIM Session
            changes (dict, optional): Dictionary with attribute changes in the policy. Defaults to {}.

        Returns:
            Response: ISIM API Response
        """
        session = session.soapclient
        client = self.__pp_client

        itemFactory = client.type_factory("ns1")

        for attr, value in changes.items():
            setattr(self, attr, value)

        ents = self.__crearEntitlementList(session, self.entitlements)
        membs = self.__crearMembershipList(session, self.membership)

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

        r = session.modificarPolitica(self.ou.wsou, wspp, self.date)

        return Response(session, r)

    def delete(self, session: "Session") -> Response:
        """
        Requests to modify the provisioning policy in ISIM.

        Args:
            session (Session): Active ISIM Session

        Returns:
            Response: ISIM API Response
        """

        session = session.soapclient
        r = session.eliminarPolitica(self.ou.wsou, self.dn, self.date)
        return Response(session, r)
