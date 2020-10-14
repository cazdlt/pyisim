from collections import defaultdict
from .organizational_container import OrganizationalContainer


class Role:
    type = None

    def __init__(
        self,
        session,
        dn=None,
        rol=None,
        role_attrs=None,
    ):
        """

        Args:
            session (pyisim.Session): session object
            id (str): for role lookup
            rol (zeep.WSRole): for initialization after search
            role_attrs (dict):      name,
                                    description,
                                    parent (pyisim.entities.OrganizationalContainer),
                                    classification: str (eg. role.classification.business). Defaults to "".
                                    access_option (int): 1: disable / 2: enable / 3: shared access
                                    access_category: access category. Defaults to None.
                                    owners: list of owner DNs. can be people or roles. Defaults to [].
                                    rule: required only if dynamic role.
                                    scope: required for dynamic roles
        """
        # session = session.soapclient

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

    def crearAtributoRol(self, client, name, values):
        itemFactory = client.type_factory("ns1")
        listFactory = client.type_factory("ns0")

        values = listFactory.ArrayOf_xsd_string(values)

        attr = itemFactory.WSAttribute(
            name=name, operation=0, values=values, isEncoded=False
        )

        return attr

    def crearWSRole(self, session):

        """
        A partir de la información de la instancia, devuelve un objeto WSRole para entregárselo al API de ISIM
        """
        # session=session.soapclient
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

        if self.type == "dynamic":
            rule = self.crearAtributoRol(client, "erjavascript", self.rule)
            scope = self.crearAtributoRol(client, "erscope", self.scope)
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

    def add(self, session):
        session = session.soapclient

        # client = self.__role_client

        wsrole = self.crearWSRole(session)

        if self.type == "static":
            r = session.crearRolEstatico(wsrole, self.ou.wsou)
            self.dn = r["itimDN"]
        else:
            r = session.crearRolDinamico(wsrole, self.ou.wsou)

        # self.dn = r["itimDN"]
        return r

    def modify(self, session, changes={}):
        session = session.soapclient
        # url = session.addr + "WSRoleServiceService?wsdl"
        client = self.__role_client

        for attr, value in changes.items():
            setattr(self, attr, value)

        wsrole = self.crearWSRole(session)
        wsattributes = wsrole["attributes"]["item"]

        errolename = self.crearAtributoRol(client, "errolename", self.name)
        description = self.crearAtributoRol(
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

    def delete(self, session, date=None):
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
        session,
        dn=None,
        rol=None,
        role_attrs=None,
    ):
        """
        Args:
        session (pyisim.Session): session object
        dn (str): for role lookup
        rol (zeep.WSRole): for initialization after search
        role_attrs (dict):      name,
                                description,
                                parent (pyisim.entities.OrganizationalContainer),
                                classification: str (eg. role.classification.business). Defaults to "".
                                access_option (int): 1: disable / 2: enable / 3: shared access
                                access_category: access category. Defaults to None.
                                owners: list of owner DNs. can be people or roles. Defaults to [].
                                rule: LDAP filter. Required.
                                scope (int, optional): policy scope (1=ONE_LEVEL / 2=SUBTREE). Defaults to 2.
        """

        if role_attrs and "rule" not in role_attrs:
            raise ValueError("Dynamic roles must have a rule (LDAP filter) defined")

        super().__init__(session, dn, rol, role_attrs)


class StaticRole(Role):

    type = "static"

    def __init__(
        self,
        session,
        dn=None,
        rol=None,
        role_attrs=None,
    ):
        """
        Args:
        session (pyisim.Session): session object
        dn (str): for role lookup
        rol (zeep.WSRole): for initialization after search
        role_attrs (dict):      name,
                                description,
                                parent (pyisim.entities.OrganizationalContainer),
                                classification: str (eg. role.classification.business). Defaults to "".
                                access_option (int): 1: disable / 2: enable / 3: shared access
                                access_category: access category. Defaults to None.
                                owners: list of owner DNs. can be people or roles. Defaults to [].
        """

        if role_attrs and "rule" in role_attrs:
            raise ValueError("Static roles can't have a rule (LDAP filter) defined")

        if role_attrs and "scope" in role_attrs:
            raise ValueError("Static roles can't have a scope defined")

        super().__init__(session, dn, rol, role_attrs)
