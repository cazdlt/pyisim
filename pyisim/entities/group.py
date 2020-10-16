from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyisim.auth import Session


class Group:
    def __init__(self, session: "Session", group: dict = None):
        """
        Represents an ISIM service group. Holds all of its attributes and metadata.

        Initialized only through REST API calls in the pyisim.search.group() module function.

        Args:
            session (Session): Active ISIM Session
            group (dict, optional): Used for initialization after search operations. Defaults to None.
        """
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
