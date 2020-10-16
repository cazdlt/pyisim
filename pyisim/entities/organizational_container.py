from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyisim.auth import Session


class OrganizationalContainer:
    def __init__(
        self, session: "Session", dn: str = None, organizational_container: dict = None
    ):
        """
        Represents an ISIM Business Unit. Can do lookup using the DN parameter or searched using the pyisim.search.organizational_container() module function

        Args:
            session (Session): Active ISIM Session
            dn (str, optional): Organizationl Container DN. Defaults to None.
            organizational_container (dict, optional): Used for initialization after search operations. Defaults to None.
        """
        if dn:
            self.wsou = session.soapclient.lookupContainer(dn)
            self.name = self.wsou.name
            self.dn = self.wsou["itimDN"]
            self.profile_name = self.wsou["profileName"]

            rest_profile_names = {
                "BusinessPartnerOrganization": "bporganizations",
                "OrganizationalUnit": "organizationunits",
                "Organization": "organizations",
                "Location": "locations",
                "AdminDomain": "admindomains",
            }
            self.href = session.restclient.buscarOUs(
                rest_profile_names[self.profile_name], self.name
            )[0]["_links"]["self"]["href"]

        elif organizational_container:
            self.name = organizational_container["_links"]["self"]["title"]
            self.href = organizational_container["_links"]["self"]["href"]
            self.dn = organizational_container["_attributes"]["dn"]
            self.wsou = session.soapclient.lookupContainer(self.dn)
            self.profile_name = self.wsou["profileName"]

    def __eq__(self, o) -> bool:
        return self.dn == o.dn
