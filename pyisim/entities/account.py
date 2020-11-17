from typing import TYPE_CHECKING

from ..response import Response

if TYPE_CHECKING:
    from pyisim.auth import Session

    from .person import Person
    from .service import Service


class Account:
    def __init__(
        self,
        session: "Session",
        account: dict = None,
        account_attrs: dict = None,
    ):
        """
        Represents an account.

        Args:
            session (Session): Active ISIM Session
            account (dict, optional): Acccount object returned from ISIM SOAP API. Defaults to None.
            account_attrs (dict, optional): Dictionary of person attributes. See: utils.get_account_defaults()
        """
        self.changes = {}

        if account:
            self.id = account["name"]
            self.dn = account["itimDN"]
            self.profile_name = account["profileName"]
            self.service_name = account["serviceName"]

            account_attrs = {}
            for a in account["attributes"]["item"]:
                attr_values = a["values"]["item"]
                if attr_values[0].strip():
                    account_attrs[a["name"]] = (
                        attr_values if len(attr_values) > 1 else attr_values[0]
                    )

        for k, v in account_attrs.items():
            setattr(self, k, v)

    def add(
        self,
        session: "Session",
        owner: "Person",
        service: "Service",
        justification: str,
    ) -> Response:
        """
        Request to add the specified account

        Args:
            session (Session): Active ISIM Session
            owner (Person): Account's owner
            service (Service): Account's service
            justification (str): Request justificacion

        Returns:
            Response: ISIM SOAP API Response
        """

        attrs = self.__dict__
        attrs["owner"] = owner.dn
        wsattrs = self.__create_wsattrs(attrs)

        wsrequest=session.soapclient.createAccount(
            service.dn, wsattrs, None, justification
        )

        return Response(session,wsrequest)

    def __setattr__(self, attr, val):
        if hasattr(self, attr):
            self.changes[attr] = val
        super().__setattr__(attr, val)

    def __create_wsattrs(self, attrs: dict) -> list:
        """
        Creates a WSAttributes[]-compatible object from a dictionary of attributes

        Args:
            attrs (dict): Account attributes

        Returns:
            list: List of WSAttributes
        """

        wsattrs = []
        for name, value in attrs.items():
            if name != "changes":
                wsattrs.append(
                    {
                        "name": name,
                        "operation": 0,
                        "values": {
                            "item": value if isinstance(value, list) else [value]
                        },
                        "isEncoded": False,
                    }
                )

        return wsattrs

    def modify(self, session: "Session", justification: str, changes={}) -> Response:
        """
        Requests to modify the account.

        Changes can be specified by modifying the instance attributes or through the changes dictionary

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justification
            changes (dict, optional): Attribute changes dictionary. Defaults to {}.

        Returns:
            Response: ISIM SOAP API Response
        """
        try:

            self.changes.update(changes)
            wsattrs = self.__create_wsattrs(self.changes)

            wsrequest = session.soapclient.modifyAccount(
                self.dn, wsattrs, None, justification
            )
            return Response(session,wsrequest)
        except AttributeError:
            raise Exception(
                "Account has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def suspend(self, session: "Session", justification: str) -> Response:
        """
        Request to suspend the specified account

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justificacion

        Returns:
            Response: ISIM API Response
        """
        try:
            wsrequest = session.soapclient.suspendAccount(self.dn, None, justification)
            return Response(session,wsrequest)
        except AttributeError:
            raise Exception(
                "Account has no reference to ISIM, search for it to link it"
            )

    def restore(self, session: "Session", password: str, justification: str) -> Response:
        """
        Request to restore the specified account

        Args:
            session (Session): Active ISIM Session
            password (str): Account's password
            justification (str): Request justificacion

        Returns:
            Response: ISIM SOAP API Response
        """
        try:
            wsrequest = session.soapclient.restoreAccount(
                self.dn, password, None, justification
            )
            return Response(session,wsrequest)
        except AttributeError:
            raise Exception(
                "Account has no reference to ISIM, search for it to link it"
            )

    def orphan(self, session: "Session") -> None:
        """
        Request to orphan the specified account

        Args:
            session (Session): Active ISIM Session

        Returns:
            None
        """
        try:
            session.soapclient.orphanSingleAccount(self.dn)
            return
        except AttributeError:
            raise Exception(
                "Account has no reference to ISIM, search for it to link it"
            )

    def delete(self, session: "Session", justification: str) -> Response:
        """
        Request to deprovision the specified account

        Args:
            session (Session): Active ISIM Session
            justification (str): Request justificacion

        Returns:
            Response: ISIM SOAP API Response
        """
        try:
            wsrequest = session.soapclient.deprovisionAccount(self.dn, None, justification)
            return Response(session,wsrequest)
        except AttributeError:
            raise Exception(
                "Account has no reference to ISIM, search for it to link it"
            )
