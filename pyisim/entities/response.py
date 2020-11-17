from .request import Request
from typing import TYPE_CHECKING
from zeep.helpers import serialize_object

if TYPE_CHECKING:
    from pyisim.auth import Session


class Response:
    def __init__(self, session: "Session", raw, content=None) -> None:

        if "zeep" in type(raw).__module__:
            self.raw = serialize_object(raw,dict)
            self.type="SOAP"
        else:
            self.raw=raw.json()
            self.type="REST"
        
        if "WSRequest" in type(raw).__name__:
            self.request = Request(session, request=raw)
        else:
            if raw.get("request_id"):
                request_id = raw["request_id"]
            elif raw.get("requestID"):
                request_id = raw["requestID"]
            elif raw.get("requestId"):
                request_id = raw["requestId"]
            elif raw.get("_links", {}).get("result", {}).get("href"):
                request_id = raw["_links"]["result"]["href"]
            else:
                request_id = None

            if request_id:
                self.request = Request(session, id=request_id)

        if content:
            self.content = content
