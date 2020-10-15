import requests
from requests.auth import HTTPBasicAuth


class VASession:
    """
    Handles REST API Session in ISIM Virtual Appliance
    """

    def __init__(self, username, password, base_url, certificate_path):
        self.username = username
        # self.password=password
        self.base_url = base_url
        # self.cert=certificate_path

        self.auth = HTTPBasicAuth(username, password)
        self.s = requests.Session()
        self.s.verify = certificate_path if certificate_path else None
