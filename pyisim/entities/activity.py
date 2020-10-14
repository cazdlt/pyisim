from pyisim.exceptions import NotFoundError


class Activity:
    def __init__(self, session, activity=None, id=None):

        if id:
            activity = session.restclient.lookupActividad(str(id))
            if "_attributes" not in activity.keys():
                raise NotFoundError(f"Activity not found: {id}")

        self.request_href = activity["_links"]["request"]["href"]
        self.href = activity["_links"]["self"]["href"]
        self.workitem_href = activity["_links"]["workitem"]["href"]
        self.name = activity["_attributes"]["name"]
        self.type = activity["_attributes"]["type"]
        self.status = activity["_attributes"]["status"]["key"].split(".")[-1]
        self.requestee = activity["_links"]["requestee"]["title"]

    def complete(self, session, result, justification):

        """Allows to complete:
        Approvals   (result: approve/reject)
        Work Orders (result: successful/warning/failure)
        RFI         (result=[
                        {'name':attr_name,'value':attr_value}, ...
                    ])
        """

        if self.type not in ["APPROVAL", "WORK_ORDER", "RFI"]:
            raise NotImplementedError(
                "Can only complete approvals, work orders and RFIs (for now)"
            )

        act_dict = {"_attributes": {}, "_links": {"workitem": {}}}
        act_dict["_attributes"]["type"] = self.type
        act_dict["_attributes"]["name"] = self.name
        act_dict["_links"]["workitem"]["href"] = self.workitem_href

        assert self.status == "PENDING", "Activity is already complete."
        r = session.restclient.completarActividades([act_dict], result, justification)

        return r
