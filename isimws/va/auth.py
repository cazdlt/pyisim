import requests
from requests.auth import HTTPBasicAuth

class Session():
    """
    Maneja sesión conjunta de REST y SOAP
    """
    def __init__(self, username, password, base_url, certificate_path):
        self.username=****
        # self.password=****
        self.base_url=base_url
        # self.cert=certificate_path

        self.auth=HTTPBasicAuth(username,password)
        self.s=requests.Session()
        self.s.verify=certificate_path if certificate_path else None

        