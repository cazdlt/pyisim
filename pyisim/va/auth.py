import requests
from requests.auth import HTTPBasicAuth


class VASession:
    """
    Handles user session for the IBM Security Identity Manager Virtual Appliance
    """

    def __init__(self, username:str, password:str, base_url:str, certificate_path:str):
        """
        Performs login on specified ISIM Virtual Appliance URL

        Args:
            url (str): ISIM VA Base URL. Example: https://iam.isimva.com
            username (str): Login name of user
            password (str): User password
            certificate_path (str): Path to application server root certificate. Example: "./MyCA.cer"
        """
        self.username = username
        # self.password=password
        self.base_url = base_url
        # self.cert=certificate_path

        self.auth = HTTPBasicAuth(username, password)
        self.s = requests.Session()
        self.s.verify = certificate_path if certificate_path else None
