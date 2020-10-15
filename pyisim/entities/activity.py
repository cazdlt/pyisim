from pyisim.exceptions import NotFoundError
from typing import Dict, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pyisim.auth import Session

class Activity:
    def __init__(self, session: "Session", activity=None, id: str=None):
        """
        Represents an ISIM Activity. Can do lookup using the id attribute.

        Args:
            session (Session): Active ISIM Session
            activity (zeep.WSActivity, optional): Activity object returned from ISIM REST API. Defaults to None.
            id (str, optional): Activity ID for lookup. Defaults to None.
        """

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

    def complete(self, session:"Session", result:Union[str,List[Dict[str,str]]], justification:str):
        """
        Completes the activity. As of now, only allows RFIs, Work Orders and Approval operations.

        Result values:

            * For approvals: "approve" / "reject"
            * For work orders: "successful" / "warning" / "failure"
            * For RFIs: List of {"name":attr_name, "value":attr_value}

        Args:
            session (Session): Active ISIM Session
            result (Union[str,List[Dict[str,str]]]): Result value.    
            justification (str): Activity justification

        Returns:
            dict: REST API Response
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
