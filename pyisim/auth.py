import pyisim.rest as simrest
import pyisim.soap as simsoap
from pyisim.entities import Person


class Session:
    """
    Handles user session for the IBM Security Identity Manager application
    """

    def __init__(self, url:str, username:str, password:str, certificate_path:str):
        """
        Performs login on specified ISIM URL

        Args:
            url (str): ISIM Base URL. Example: https://iam.isim.com:9082
            username (str): Login name of user
            password (str): User password
            certificate_path (str): Path to application server root certificate. Example: "./MyCA.cer"
        """
        self.username = username
        self.restclient = simrest.ISIMClient(url, username, password, certificate_path)
        self.soapclient = simsoap.ISIMClient(url, username, password, certificate_path)

    def current_person(self, attributes="*") -> Person:
        """Returns the current logged in person entity.

        Args:
            attributes (str, optional): comma separated attributes to return. Defaults to "*".

        Returns:
            pyisim.entities.Person: Person entity of the currently logged user.
        """
        p = self.restclient.lookupCurrentPerson(attributes, "")
        return Person(self, person=p)
