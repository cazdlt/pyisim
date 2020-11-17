from pyisim.exceptions import NotFoundError
from typing import List, TYPE_CHECKING
from .account import Account
from ..response import Response

if TYPE_CHECKING:
    from pyisim.auth import Session
    from .organizational_container import OrganizationalContainer
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
        person_attrs: dict = None,
    ):
        """
        Args:
            session (Session): Active ISIM Session
            person (dict, optional): Used for initialization after search operations. Defaults to None.
            href (str, optional): Used for initialization for lookup operations. Defaults to None.
            person_attrs: Dictionary of person attributes
        """

        self.changes = {}

        if person:
            self.href = person["_links"]["self"]["href"]
            self.dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                "_attributes"
            ]["dn"]
            person_attrs = person["_attributes"]

        elif href:
            r = session.restclient.lookupPersona(href, attributes="*")
            if r["_links"]["self"]["href"] != href:
                raise NotFoundError(f"Invalid or not found person: {href}")

            self.href = href
            self.dn = session.restclient.lookupPersona(self.href, attributes="dn")[
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
        ret = session.restclient.crearPersona(self, orgid, justification)
        return Response(session, ret)

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
        try:
            # href = self.href

            self.changes.update(changes)
            # for attr,value in changes.items():
            #     setattr(self,attr,value)

            ret = session.restclient.modificarPersona(
                self.href, self.changes, justification
            )
            return Response(session, ret)
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

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
        if len(accesses) > 0:
            ret = session.restclient.solicitarAccesos(accesses, self, justification)
        return Response(session, ret)

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

        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = session.soapclient.suspendPersonAdvanced(
                dn, suspend_accounts, None, justification
            )
            return Response(session, ret)
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

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
        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = session.soapclient.restaurarPersona(
                self.dn, restore_accounts, password, None, justification
            )
            return Response(session, ret)
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def delete(self, session: "Session", justification: str) -> Response:
        """
        Requests to delete the person in ISIM

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justification

        Returns:
            Response: ISIM API Response
        """

        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = session.soapclient.eliminarPersona(self.dn, justification)
            return Response(session, ret)
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def get_accounts(self, session: "Session") -> List[Account]:
        """
        Retrieves all registered accounts of the referenced person.

        Args:
            session (Session): Active ISIM Session

        Returns:
            List[Account]: List of the person account entities.
        """

        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            result = session.soapclient.getAccountsByOwner(self.dn)
            return [Account(session, account=r) for r in result]

        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )
