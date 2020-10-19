from collections import defaultdict
from .organizational_container import OrganizationalContainer
import dataclasses
from typing import Dict, List, Literal, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pyisim.auth import Session


@dataclasses.dataclass
class RoleAttributes:

    name: str
    """
    Role name
    """
    description: str
    """
    Role description
    """
    parent: OrganizationalContainer
    """
    Role Business Unit
    """
    classification: str
    """
    Role classification.
    Optional. Defaults to "".
    Example: "role.classification.business"
    """
    access_option: Literal[1, 2, 3]
    """
    Defines if role is an access.

    Options:

    * 1: Access disabled
    * 2: Access enabled
    * 3: Shared access
    """
    access_category: str = None
    """
    Role access category.
    Required if role is an access.
    Example: "Role:Access:Azure"
    """
    owners: List[str] = dataclasses.field(default_factory=list)
    """
    Role owners.
    List of owner DNs.
    Can be Person DNs or Role DNs
    """
    rule: str = None
    """
    Dynamic Role rule.
    LDAP Filter syntax.
    Required if dynamic role.
    """
    scope: Literal[1, 2] = 2
    """
    Dynamic Role scope.
    Only used in dynamic roles.
    Defaults to 2.

    Options:
    * 1: One level
    * 2: Subtree
    """


class Role:
    type = None

    def __init__(
        self,
        session: "Session",
        dn: str = None,
        rol=None,
        role_attrs: Union[RoleAttributes, Dict] = None,
    ):
        """
        Args:
            session (Session): Active ISIM Session
            dn (str, optional): Initialize with role DN for lookup into ISIM Directory Server. Defaults to None.
            rol (WSRole, optional): SOAP ProvisioningPolicy object to initialize after search operations. Defaults to None.
            role_attrs (Union[RoleAttributes,Dict], optional): Provisioning Policy attributes for initialization. Defaults to None.
        """

        url = session.soapclient.addr + "WSRoleServiceService?wsdl"

        self.__role_client = session.soapclient.get_client(url)

        if role_attrs:

            self.name = role_attrs["name"]
            self.description = role_attrs["description"]
            self.ou = role_attrs["parent"]
            self.classification = (
                role_attrs["classification"] if role_attrs["classification"] else ""
            )

            role_attrs["access_option"] = str(role_attrs["access_option"])
            if role_attrs["access_option"] not in ["1", "2", "3"]:
                raise ValueError(
                    "Access option must be an int. 1: disable / 2: enable / 3: shared access"
                )
            self.access_option = role_attrs["access_option"]

            if role_attrs["access_option"] in ["2", "3"]:
                if not role_attrs["access_category"]:
                    raise ValueError("If the role is an access, it must have category.")
                self.access_category = role_attrs["access_category"]

            self.owners = role_attrs["owners"] if role_attrs["owners"] else []

            if "rule" in role_attrs:
                self.rule = role_attrs["rule"]

            self.scope = role_attrs["scope"] if "scope" in role_attrs else 2

            if self.type not in ["static", "dynamic"]:
                raise Exception("Invalid role type.")

        else:
            if dn:
                rol = session.soapclient.lookupRole(dn)

            self.name = rol["name"]
            self.description = rol["description"]
            self.dn = rol["itimDN"]

            attrs = {
                attr["name"]: [i for i in attr["values"]["item"]]
                for attr in rol["attributes"]["item"]
            }

            if self.type == "static":
                if "erjavascript" in attrs:
                    raise ValueError(
                        "Static roles can't. have a rule (LDAP filter) defined. This might be a dynamic role."
                    )
            elif self.type == "dynamic":
                if "erjavascript" not in attrs:
                    raise ValueError(
                        "Dynamic roles must have a rule (LDAP filter) defined. This might be a static role."
                    )
            else:
                raise Exception("Invalid role type.")

            attrs = defaultdict(list, attrs)
            ou = attrs["erparent"][0]  # dn del contenedor
            self.parent = OrganizationalContainer(session, dn=ou)
            if attrs["erroleclassification"]:
                self.classification = attrs["erroleclassification"][0]
            if attrs["eraccessoption"]:
                self.access_option = attrs["eraccessoption"][0]
            if attrs["erobjectprofilename"]:
                self.access_category = attrs["erobjectprofilename"][0]

            if attrs["erjavascript"]:
                self.rule = attrs["erjavascript"][0]

            if attrs["erscope"]:
                self.scope = attrs["erscope"]

            self.owners = attrs["owner"]

    def __crearAtributoRol(self, client, name, values):
        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        values = listFactory.ArrayOf_xsd_string(values)

        attr = itemFactory.WSAttribute(
            name=name, operation=0, values=values, isEncoded=False
        )

        return attr

    def __crearWSRole(self, session):

        """
        A partir de la información de la instancia, devuelve un objeto WSRole para entregárselo al API de ISIM
        """
        # session=session.soapclient
        client = self.__role_client

        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        eraccesoption = self.__crearAtributoRol(
            client, "eraccessoption", self.access_option
        )
        erRoleClassification = self.__crearAtributoRol(
            client, "erRoleClassification", self.classification
        )

        if self.access_option in ["2", "3"]:
            erObjectProfileName = self.__crearAtributoRol(
                client, "erObjectProfileName", self.access_category
            )
            lista_atributos = [eraccesoption, erRoleClassification, erObjectProfileName]
        else:
            lista_atributos = [eraccesoption, erRoleClassification]

        if self.owners is not None:
            owner = self.__crearAtributoRol(client, "owner", self.owners)
            lista_atributos.append(owner)

        if self.type == "dynamic":
            rule = self.__crearAtributoRol(client, "erjavascript", self.rule)
            scope = self.__crearAtributoRol(client, "erscope", self.scope)
            lista_atributos.append(rule)
            lista_atributos.append(scope)

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

    def add(self, session: "Session"):
        """
        Requests to add the role into ISIM

        If role is static, and request succeeds, DN gets initialized immediatly.
        If role is dynamic, request process is sent to ISIM for evaluation.

        Args:
            session (Session): Active ISIM Session

        Returns:
            zeep.Response: SOAP Response to the request
        """
        session = session.soapclient

        # client = self.__role_client

        wsrole = self.__crearWSRole(session)

        if self.type == "static":
            r = session.crearRolEstatico(wsrole, self.ou.wsou)
            self.dn = r["itimDN"]
        else:
            r = session.crearRolDinamico(wsrole, self.ou.wsou)

        # self.dn = r["itimDN"]
        return r

    def modify(self, session: "Session", changes={}):
        """
        Requests to modify the role in ISIM

        Args:
            session (Session): Active ISIM Session
            changes (dict, optional): Changes dictionary. Defaults to {}.

        Returns:
            zeep.Response: SOAP Response to the request
        """
        session = session.soapclient
        # url = session.addr + "WSRoleServiceService?wsdl"
        client = self.__role_client

        for attr, value in changes.items():
            setattr(self, attr, value)

        wsrole = self.__crearWSRole(session)
        wsattributes = wsrole["attributes"]["item"]

        errolename = self.__crearAtributoRol(client, "errolename", self.name)
        description = self.__crearAtributoRol(
            client, "description", wsrole["description"]
        )

        wsattributes.append(errolename)
        wsattributes.append(description)

        # print(wsattributes)

        if self.type == "static":
            r = session.modificarRolEstatico(self.dn, wsattributes)
        else:
            r = session.modificarRolDinamico(self.dn, wsattributes)

        return r

    def delete(self, session: "Session", date=None):
        """
        Requests to delete role from ISIM

        Args:
            session (Session): Active ISIM Session
            date (datetime, optional): Not implemented yet. Defaults to None.

        Returns:
            zeep.Response: SOAP Response to the request
        """
        if date:
            raise NotImplementedError(
                "No se ha implementado la programación de tareas."
            )

        r = session.soapclient.eliminarRol(self.dn, date)

        return r


class DynamicRole(Role):

    type = "dynamic"

    def __init__(
        self,
        session: "Session",
        dn: str = None,
        rol=None,
        role_attrs: Union[RoleAttributes, Dict] = None,
    ):
        """
        Child class for representing Static Roles.
        Inherits methods and behavior from Role class

        Args:
            session (Session): Active ISIM Session
            dn (str, optional): Initialize with role DN for lookup into ISIM Directory Server. Defaults to None.
            rol (WSRole, optional): SOAP ProvisioningPolicy object to initialize after search operations. Defaults to None.
            role_attrs (Union[RoleAttributes,Dict], optional): Provisioning Policy attributes for initialization. Defaults to None.
        """

        if dataclasses.is_dataclass(role_attrs):
            role_attrs = dataclasses.asdict(role_attrs)

        if role_attrs and role_attrs["rule"] is None:
            raise ValueError("Dynamic roles must have a rule (LDAP filter) defined")

        super().__init__(session, dn, rol, role_attrs)


class StaticRole(Role):

    type = "static"

    def __init__(
        self,
        session: "Session",
        dn: str = None,
        rol=None,
        role_attrs: Union[RoleAttributes, Dict] = None,
    ):
        """
        Child class for representing Static Roles.
        Inherits methods and behavior from Role class

        Args:
            session (Session): Active ISIM Session
            dn (str, optional): Initialize with role DN for lookup into ISIM Directory Server. Defaults to None.
            rol (WSRole, optional): SOAP ProvisioningPolicy object to initialize after search operations. Defaults to None.
            role_attrs (Union[RoleAttributes,Dict], optional): Provisioning Policy attributes for initialization. Defaults to None.
        """
        if dataclasses.is_dataclass(role_attrs):
            role_attrs = dataclasses.asdict(role_attrs)

        if role_attrs and "rule" in role_attrs and role_attrs["rule"] is not None:
            raise ValueError("Static roles can't have a rule (LDAP filter) defined")

        if role_attrs and "scope" in role_attrs and role_attrs["scope"] is not None:
            raise ValueError("Static roles can't have a scope defined")

        super().__init__(session, dn, rol, role_attrs)
