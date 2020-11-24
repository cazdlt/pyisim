from typing import TYPE_CHECKING, Dict, List

from ..exceptions import NotFoundError, PersonNotFoundError
from ..response import Response
from .account import Account
from .organizational_container import OrganizationalContainer
from .role import DynamicRole, StaticRole

if TYPE_CHECKING:
    from pyisim.auth import Session
    from .access import Access


class Person:
    """
    Represents a Person object in ISIMs directory server

    Can be subclassed to represent Business Partner Persons or custom Person entities defined in your system
    """

    profile_name = "Person"

    def __init__(
        self,
        session: "Session",
        person: dict = None,
        href: str = None,
        dn: str = None,
        person_attrs: dict = None,
    ):
        """
        Args:
            session (Session): Active ISIM Session
            person (dict, optional): Used for initialization after search operations. Defaults to None.
            href (str, optional): Used for initialization for lookup operations. Defaults to None.
            dn (str,optional): Used for DN Lookup operations. Not implemented. Defaults to None.
            person_attrs: Dictionary of person attributes
        """

        self.changes = {}
        self.embedded = {}

        if dn:
            raise NotImplementedError("DN Lookup for Persons not implemented yet.")

        if person:
            self.href = person["_links"]["self"]["href"]
            self.__get_dn(session)
            person_attrs = person["_attributes"]

            embedded = person.get("_embedded")
            if embedded:
                self.__fill_embedded(session, embedded)

        elif href:
            r = session.restclient.lookup_person(href, attributes="*")
            if r["_links"]["self"]["href"] != href:
                raise NotFoundError(f"Person is invalid or not found: {href}")

            self.href = href
            self.__get_dn(session)
            person_attrs = r["_attributes"]

        for k, v in person_attrs.items():
            setattr(self, k, v)

    def __setattr__(self, attr, val):
        if hasattr(self, attr) and attr not in ("changes", "embedded", "href", "dn"):
            self.changes[attr] = val
        super().__setattr__(attr, val)

    def __init_subclass__(cls):

        try:
            getattr(cls, "profile_name")
        except AttributeError:
            raise TypeError(
                "All classes based on the Person entity need their profile specified (Person/BPPerson/Your custom profile) in the profile_name attribute"
            )

        return super().__init_subclass__()

    def add(
        self, session: "Session", parent: "OrganizationalContainer", justification: str
    ) -> Response:
        """
        Request to add the specified person into ISIM

        Args:
            session (Session): Active ISIM Session
            parent (OrganizationalContainer): Person Business Unit
            justification (str): Request justificacion

        Returns:
            Response: ISIM API Response
        """
        orgid = parent.href.split("/")[-1]

        person_data = self.__dict__.copy()
        person_data.pop("changes", "")
        person_data.pop("embedded", "")

        ret = session.restclient.add_person(
            person_data, self.profile_name, orgid, justification
        )
        return Response(session, ret)

    def __get_dn(self, session: "Session"):
        try:
            href = self.href
            if not hasattr(self, "dn"):
                person = session.restclient.lookup_person(href, attributes="dn")
                dn = person.get("_attributes", {}).get("dn")
                if dn is None or person["_links"]["self"]["href"] != href:
                    raise AttributeError
                self.dn = person["_attributes"]["dn"]
        except AttributeError:
            raise PersonNotFoundError(
                "Person has no reference to ISIM, search for it to link it."
            )

    def modify(self, session: "Session", justification: str, changes={}) -> Response:
        """
        Requests to modify the person in ISIM.

        Changes can be specified by modifying the instance attributes or through the changes dictionary

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justification
            changes (dict, optional): Attribute changes dictionary. Defaults to {}.

        Returns:
            Response: ISIM API Response
        """

        self.__get_dn(session)
        self.changes.update(changes)

        ret = session.restclient.modify_person(self.href, self.changes, justification)
        return Response(session, ret)

    def request_access(
        self, session: "Session", accesses: List["Access"], justification: str
    ) -> Response:
        """
        Requests access to the person

        Args:
            session (Session): Active ISIM Session
            accesses (List[pyisim.entities.Access]): List of accesses to request
            justification (str): Request justification

        Returns:
            Response: ISIM API Response
        """

        ret = {}
        self.__get_dn(session)

        if len(accesses) > 0:
            ret = session.restclient.request_access(accesses, self, justification)
            return Response(session, ret)
        else:
            return Response(
                session,
                None,
                content={"message": "List is empty, no access requested."},
            )

    def suspend(
        self, session: "Session", justification: str, suspend_accounts: bool = False
    ) -> Response:
        """
        Requests to suspend the person in ISIM

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justification

        Returns:
            Response: ISIM API Response
        """

        self.__get_dn(session)

        ret = session.soapclient.suspend_person_advanced(
            self.dn, suspend_accounts, None, justification
        )
        return Response(session, ret)

    def restore(
        self,
        session: "Session",
        justification: str,
        restore_accounts: bool = False,
        password: str = None,
    ) -> Response:
        """
        Requests to restore the person in ISIM

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justification
            restore_accounts (bool): Boolean to specify if accounts are to be restored
            password (str): Restored accounts password

        Returns:
            Response: ISIM API Response
        """

        self.__get_dn(session)

        ret = session.soapclient.restore_person(
            self.dn, restore_accounts, password, None, justification
        )
        return Response(session, ret)

    def delete(self, session: "Session", justification: str) -> Response:
        """
        Requests to delete the person in ISIM

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justification

        Returns:
            Response: ISIM API Response
        """

        self.__get_dn(session)

        ret = session.soapclient.delete_person(self.dn, justification)
        return Response(session, ret)

    def get_accounts(self, session: "Session") -> List[Account]:
        """
        Retrieves all registered accounts of the referenced person.

        Args:
            session (Session): Active ISIM Session

        Returns:
            List[Account]: List of the person account entities.
        """

        self.__get_dn(session)

        result = session.soapclient.get_accounts_by_owner(self.dn)
        return [Account(session, account=r) for r in result]

    def __fill_embedded(self, session: "Session", embedded: dict) -> None:

        for attr, value in embedded.items():
            href = value["_links"]["self"]["href"].lower()
            if "people" in href:
                self.embedded[attr] = [Person(session, person=value)]
            elif "organizationcontainers" in href:
                ou = [OrganizationalContainer(session, organizational_container=value)]
                self.embedded[attr] = ou

    def get_embedded(
        self, session: "Session", embedded: List[str] = None, roles=False
    ) -> Dict[str, List]:
        """
        Gets or updates the specified embedded attributes as PyISIM entities.
        Only works for attributes available in the _embedded REST API parameter and/or organizational roles.

        Args:
            embedded (List[str], optional): List of attributes to embed as PyISIM entities
            roles (bool, optional): Specifies to embed the person's roles

        Returns:
            Dict[str, List]: Dictionary of embedded entities.
        """

        self.__get_dn(session)

        if embedded:
            embeds = ",".join(embedded)
            p = session.restclient.lookup_person(self.href, embedded=embeds)

            values = p.get("_embedded")
            if values:
                self.__fill_embedded(session, values)

        if roles:
            self.__get_roles(session)

        return self.embedded

    def __get_roles(self, session: "Session") -> None:

        if not hasattr(self, "erroles"):
            raise KeyError("Person has no roles or was initialized without them.")

        roles = []
        for role_dn in self.erroles:
            r = session.soapclient.lookup_role(role_dn)
            attrs = {
                attr["name"]: [i for i in attr["values"]["item"]]
                for attr in r["attributes"]["item"]
            }
            if "erDynamicRole" in attrs["objectclass"]:
                roles.append(DynamicRole(session, dn=role_dn))
            else:
                roles.append(StaticRole(session, dn=role_dn))

        self.embedded["roles"] = roles
