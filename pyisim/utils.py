from typing import Dict, List, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pyisim.auth import Session
    from pyisim.entities import Activity, Person, Service


def activity_batch_complete(
    session: "Session",
    actividades: List["Activity"],
    resultado: Union[str, List[Dict[str, str]]],
    justification: str,
):
    """
    Completes activities in batch.

    Prefer this method to activity.complete() if more than one activity is being completed.

    All activities must be of the same type.

    Result values:

    * For approvals: "approve" / "reject"
    * For work orders: "successful" / "warning" / "failure"
    * For RFIs: List of {"name":attr_name, "value":attr_value}

    Args:
        session (Session): Active ISIM session.
        actividades (List[Activity]): List of activities to complete. All activities must be of the same type.
        resultado (Union[str,List[Dict[str,str]]]): Result value.
        justification (str): Request justification

    Returns:
        dict: REST API Response.
    """
    acts_dict = []

    for act in actividades:
        if act.status == "PENDING":
            act_dict = {"_attributes": {}, "_links": {"workitem": {}}}
            act_dict["_attributes"]["type"] = act.type
            act_dict["_attributes"]["name"] = act.name
            act_dict["_links"]["workitem"]["href"] = act.workitem_href

            acts_dict.append(act_dict)

    r = session.restclient.completarActividades(acts_dict, resultado, justification)

    return r


def get_account_defaults(
    session: "Session", service: "Service", person: "Person" = None
) -> List[Dict]:
    """
    Get account default attribute values

    Args:
        session (Session): Active ISIM Session
        service (Service): Account service
        person (Person, optional): Person to get the default attributes, if None then gets global defaults for the service. Defaults to None.

    Raises:
        KeyError: Raised if person has no reference to ISIM

    Returns:
        List[Dict]: List of default attributes for the account
    """
    if person:
        if not hasattr(person, "dn"):
            raise KeyError("Person must have a reference to ISIM (DN). Search for it.")

        result = session.soapclient.getDefaultAccountAttributesByPerson(
            service.dn, person.dn
        )
    else:
        result = session.soapclient.getDefaultAccountAttributes(service.dn)

    account_attrs = {}
    for a in result:
        attr_values = a["values"]["item"]
        if attr_values[0] and attr_values[0].strip():
            account_attrs[a["name"]] = (
                attr_values if len(attr_values) > 1 else attr_values[0]
            )

    return account_attrs
