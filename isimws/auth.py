import isimws.rest as simrest
import isimws.soap as simsoap

class Session():
    """
    Maneja sesión conjunta de REST y SOAP
    """
    def __init__(self, username, password, env="int", use_rest=True, use_soap=****):
        self.restclient=simrest.ISIMClient(username,password,env)
        self.soapclient=simsoap.ISIMClient(username,password,env)