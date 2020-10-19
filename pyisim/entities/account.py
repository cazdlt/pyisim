from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyisim.auth import Session


class Account:
    def __init__(
        self,
        session: "Session",
        account: dict = None,
        account_attrs: dict = None,
    ):
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

    def add(self, session, owner, service, justification):

        attrs = self.__dict__
        attrs["owner"] = owner.dn
        wsattrs = []
        for name, value in attrs.items():
            wsattrs.append(
                {
                    "name": name,
                    "operation": 0,
                    "values": {"item": value if isinstance(value, list) else [value]},
                    "isEncoded": False,
                }
            )

        return session.soapclient.createAccount(
            service.dn, wsattrs, None, justification
        )

    def modify(self):
        # TODO
        raise NotImplementedError

    def suspend(self):
        # TODO
        raise NotImplementedError

    def restore(self):
        # TODO
        raise NotImplementedError

    def orphan(self):
        # TODO
        raise NotImplementedError

    def delete(self):
        # TODO
        raise NotImplementedError