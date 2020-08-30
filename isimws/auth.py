import isimws.rest as simrest
import isimws.soap as simsoap


class Session:
    """
    Maneja sesión conjunta de REST y SOAP
    """

    def __init__(self, url, username, password, certificate_path):
        self.username = username
        self.restclient = simrest.ISIMClient(url, username, password, certificate_path)
        self.soapclient = simsoap.ISIMClient(url, username, password, certificate_path)
