import json
from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from pyisim.va.auth import VASession


def list_files(session: "VASession") -> Dict:
    """
    Lists property files.

    Args:
        session ("VASession"): Active ISIM Virtual Appliance Session

    Returns:
        dict: Dictionary of property files
    """

    url = f"{session.base_url}/v1/property/propertyfiles"

    headers = {"Accept": "application/json"}

    r = session.s.get(url, headers=headers, auth=session.auth)
    return json.loads(r.content)


def get_property_value(session: "VASession", property_file:str, property_name:str=None)->Dict:
    """
    Get values of properties in a property file

    Args:
        session ("VASession"): Active ISIM VA Session
        property_file (str): Name of the property file
        property_name (str, optional): Property name. Lists all properties in the file if None. Defaults to None.

    Returns:
        Dict: Property values.
    """
    url = f"{session.base_url}/v1/property"

    params = {
        "PropertyFile": property_file,
    }
    if property_name:
        params["PropertyName"] = property_name

    headers = {"Accept": "application/json"}

    r = session.s.get(url, params=params, headers=headers, auth=session.auth)

    return json.loads(r.content)


def add_property(session: "VASession", property_file:str, property_name:str, property_value:str)->str:
    """
    Adds property to file

    Args:
        session ("VASession"): Active ISIM VA Session
        property_file (str): Property file name
        property_name (str): Property name
        property_value (str): Property value

    Returns:
        str: Reason code of response
    """
    url = f"{session.base_url}/v1/property"

    data = {
        "PropertyFile": property_file,
        "PropertyName": property_name,
        "PropertyValue": property_value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    r = session.s.post(url, json=data, headers=headers, auth=session.auth)

    return r.reason


def update_property(session: "VASession", property_file:str, property_name:str, property_value:str)->str:
    """
    Updates property

    Args:
        session ("VASession"): Active ISIM VA Session
        property_file (str): Property file name
        property_name (str): Property name
        property_value (str): Property value

    Returns:
        str: Reason code of response
    """
    url = f"{session.base_url}/v1/property"

    data = {
        "PropertyFile": property_file,
        "PropertyName": property_name,
        "PropertyValue": property_value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    r = session.s.put(url, json=data, headers=headers, auth=session.auth)

    return r.reason


def delete_property(session: "VASession", property_file:str, property_name:str=None):
    """
    Deletes property file or property in file

    Args:
        session ("VASession"): Active ISIM VA Session
        property_file (str): Property file name
        property_name (str, optional): Property name. Deletes file if none. Defaults to None.

    Returns:
        JSON Response: ISIM VA Response
    """
    url = f"{session.base_url}/v1/property"

    params = {
        "PropertyFile": property_file,
    }
    if property_name:
        params["PropertyName"] = property_name

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    r = session.s.delete(url, params=params, headers=headers, auth=session.auth)

    return r


def create_or_update_property(session: "VASession", property_file:str, property_name:str, property_value:str)-> str:
    """
    If property does not exist, creates it. If property exists, update it

    Args:
        session ("VASession"): Active ISIM VA Session
        property_file (str): Property file name
        property_name (str): Property name
        property_value (str): Property value

    Returns:
        str: Result of operation
    """
    old_value = get_property_value(session, property_file, property_name)

    if "result" in old_value.keys() and old_value["result"] == "property_not_found":
        r = "Adding: " + add_property(
            session, property_file, property_name, property_value
        )
    else:
        if property_value == old_value["PropertyValue"]:
            r = "No changes"
        else:
            r = "Updating: " + update_property(
                session, property_file, property_name, property_value
            )

    return r
