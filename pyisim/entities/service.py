class Service:
    def __init__(self, session, service=None):

        # if id:
        #     service=session.restclient.lookupServicio(str(id))
        #     if "_attributes" not in service.keys():
        #         raise NotFoundError(f"Servicio no encontrado {id}")

        if service:
            self.dn = service["itimDN"]
            self.profile_name = service["profileName"]
            self.name = service["name"]
