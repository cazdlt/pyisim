from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyisim.auth import Session

class Service:
    def __init__(self, session: "Session", service=None):
        """
        Represents an ISIM Service. Initialized only through search.service() for now.

        Args:
            session (Session): Active ISIM Session
            service (dict, optional): Activity object returned from ISIM REST API. Defaults to None.
        """

        # if id:
        #     service=session.restclient.lookupServicio(str(id))
        #     if "_attributes" not in service.keys():
        #         raise NotFoundError(f"Servicio no encontrado {id}")

        if service:
            self.dn = service["itimDN"]
            self.profile_name = service["profileName"]
            self.name = service["name"]
