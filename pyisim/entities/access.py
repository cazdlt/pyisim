from typing import TYPE_CHECKING
from .person import Person

if TYPE_CHECKING:
    from ..auth import Session


class Access:
    def __init__(self, session: "Session", access: dict = None, href: str = None):
        """
        ISIM Access entity. Used in person.request_access() method. Holds its name and URL.

        Initialized only through REST API calls in the pyisim.search.access() module function.

        Args:
            session (Session): Active ISIM API Session
            access (dict, optional): Used for initialization after search operations. Defaults to None.
            href (str): ISIM REST API Access href
        """

        if href:
            id = href.split("/")[-1]
            access = session.restclient.lookup_access(id)

        try:
            self.href = access["_links"]["self"]["href"]
            self.name = access["_links"]["self"]["title"]
        except:
            raise Exception("Access invalid or not found.")

        self.icon = access.get("_links", {}).get("icon", {}).get("href")

        attributes = access.get("_attributes", {})
        self.description = attributes.get("description")
        self.entity_type = attributes.get("entityType")
        self.category = attributes.get("accessCategory")
        self.profile = attributes.get("entityProfile")
        self.is_common = attributes.get("isCommon")
        self.tags = attributes.get("tags")
        self.additional_information = attributes.get("additionalInformation")
        self.badges = attributes.get("badges")

    def get_owners(self, session: "Session"):
        id = self.href.split("/")[-1]
        owners = session.restclient.get_access_owners(id)
        return [Person(session, o) for o in owners]

    def __eq__(self, o: object) -> bool:
        if type(o) is type(self):
            return self.href == o.href
        return False
