from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from pyisim.auth import Session
    from .organizational_container import OrganizationalContainer
    from .access import Access


class Person:

    profile_name = "Person"

    def __init__(self, session, person=None, href=None, person_attrs=None):

        self.changes = {}

        if person:
            self.href = person["_links"]["self"]["href"]
            self.dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                "_attributes"
            ]["dn"]
            person_attrs = person["_attributes"]

        elif href:
            r = session.restclient.lookupPersona(href, attributes="*")
            assert (
                r["_links"]["self"]["href"] == href
            ), "Persona no encontrada o inválida"

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

    def add(self, session, parent: "OrganizationalContainer", justification):
        orgid = parent.href.split("/")[-1]
        ret = session.restclient.crearPersona(self, orgid, justification)
        return ret

    def modify(self, session, justification, changes={}):
        try:
            # href = self.href

            self.changes.update(changes)
            # for attr,value in changes.items():
            #     setattr(self,attr,value)

            ret = session.restclient.modificarPersona(
                self.href, self.changes, justification
            )
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def request_access(
        self, session: "Session", accesses: List["Access"], justification: str
    ):

        ret = {}
        if len(accesses) > 0:
            ret = session.restclient.solicitarAccesos(accesses, self, justification)
        return ret

    def suspend(self, session, justification):

        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = session.soapclient.suspenderPersona(dn, justification)
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def restore(self, session, justification):
        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = session.soapclient.restaurarPersona(self.dn, justification)
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )

    def delete(self, session, justification):

        try:
            try:
                dn = self.dn
            except AttributeError:
                dn = session.restclient.lookupPersona(self.href, attributes="dn")[
                    "_attributes"
                ]["dn"]
                self.dn = dn

            ret = session.soapclient.eliminarPersona(self.dn, justification)
            return ret
        except AttributeError:
            raise Exception(
                "Person has no reference to ISIM, search for it or initialize it with href to link it."
            )
