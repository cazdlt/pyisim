class Access:
    def __init__(self, access=None):
        """
        ISIM Access entity. Used in person.request_access() method. Holds its name and URL.

        Initialized only through REST API calls in the pyisim.search.access() module function.

        Args:
            access (dict, optional): Used for initialization after search operations. Defaults to None.
        """

        if access:
            self.href = access["_links"]["self"]["href"]
            self.name = access["_links"]["self"]["title"]
