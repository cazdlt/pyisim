import requests
import json
from requests.auth import HTTPBasicAuth


def list_files(session):

    url = f"https://{session.base_url}/v1/property/propertyfiles"

    headers = {"Accept": "application/json"}

    r = session.s.get(url, headers=headers, auth=session.auth)
    return json.loads(r.content)


def get_property_value(session, property_file, property_name=None):
    url = f"https://{session.base_url}/v1/property"

    params = {
        "PropertyFile": property_file,
    }
    if property_name:
        params["PropertyName"] = property_name

    headers = {"Accept": "application/json"}

    r = session.s.get(url, params=params, headers=headers, auth=session.auth)

    return json.loads(r.content)


def add_property(session, property_file, property_name, property_value):
    url = f"https://{session.base_url}/v1/property"

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


def update_property(session, property_file, property_name, property_value):
    url = f"https://{session.base_url}/v1/property"

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


def delete_property(session, property_file, property_name=None):
    url = f"https://{session.base_url}/v1/property"

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


def create_or_update_property(session, property_file, property_name, property_value):
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
