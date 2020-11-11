from typing import TYPE_CHECKING
from ..exceptions import NotFoundError

if TYPE_CHECKING:
    from pyisim.auth import Session

class Request:
    def __init__(self, session: "Session", request=None, id:str=None) -> None:

        if id:
            try:
                request=session.soapclient.getRequest(id)
            except Exception as e:
                raise NotFoundError(f"Request {id} not found.")
        
        self.time_completed=request["timeCompleted"]
        self.subject_profile=request["subjectProfile"]
        self.result=request["result"]
        self.select=request["select"]
        self.description=request["description"]
        self.result_detail=request["resultDetail"]
        self.process_type_string=request["processTypeString"]
        self.title=request["title"]
        self.owner=request["owner"]
        self.process_state_string=request["processStateString"]
        self.status=request["status"]
        self.requestee=request["requestee"]
        self.time_submitted=request["timeSubmitted"]
        self.subject=request["subject"]
        self.request_id=request["requestId"]
        self.process_type=request["processType"]
        self.subject_service=request["subjectService"]
        self.status_string=request["statusString"]
        self.process_state=request["processState"]
        self.time_scheduled=request["timeScheduled"]
        


    def get_children(self,):
        # TODO
        pass

    def get_pending_activities(self,):
        # TODO
        pass

    def abort(self,):
        # TODO
        pass
