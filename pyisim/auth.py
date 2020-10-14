import pyisim.rest as simrest
import pyisim.soap as simsoap
from pyisim.entities import Person


class Session:
    """
    Handles user session in REST and SOAP APis
    """

    def __init__(self, url, username, password, certificate_path):
        self.username = username
        self.restclient = simrest.ISIMClient(url, username, password, certificate_path)
        self.soapclient = simsoap.ISIMClient(url, username, password, certificate_path)

    def current_person(self, attributes="*", embedded=""):
        """Returns the current logged in person entity.

        Args:
            attributes (str, optional): comma separated attributes to return. Defaults to "*".
            embedded (str, optional): comma separated embedded attributes to return. Defaults to "".

        Returns:
            pyisim.entities.Person: Person entity of the currently logged user.
        """
        p = self.restclient.lookupCurrentPerson(attributes, embedded)
        return Person(self, person=p)
