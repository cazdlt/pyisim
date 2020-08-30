import requests
import json
from requests.auth import HTTPBasicAuth


def list_files(sesion):

    url = f"https://{sesion.base_url}/v1/property/propertyfiles"

    headers = {"Accept": "application/json"}

    r = sesion.s.get(url, headers=headers, auth=sesion.auth)
    return json.loads(r.content)


def get_property_value(sesion, property_file, property_name=None):
    url = f"https://{sesion.base_url}/v1/property"

    params = {
        "PropertyFile": property_file,
    }
    if property_name:
        params["PropertyName"] = property_name

    headers = {"Accept": "application/json"}

    r = sesion.s.get(url, params=params, headers=headers, auth=sesion.auth)

    return json.loads(r.content)


def add_property(sesion, property_file, property_name, property_value):
    url = f"https://{sesion.base_url}/v1/property"

    data = {
        "PropertyFile": property_file,
        "PropertyName": property_name,
        "PropertyValue": property_value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    r = sesion.s.post(url, json=data, headers=headers, auth=sesion.auth)

    return r.reason


def update_property(sesion, property_file, property_name, property_value):
    url = f"https://{sesion.base_url}/v1/property"

    data = {
        "PropertyFile": property_file,
        "PropertyName": property_name,
        "PropertyValue": property_value,
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    r = sesion.s.put(url, json=data, headers=headers, auth=sesion.auth)

    return r.reason


def delete_property(sesion, property_file, property_name=None):
    url = f"https://{sesion.base_url}/v1/property"

    params = {
        "PropertyFile": property_file,
    }
    if property_name:
        params["PropertyName"] = property_name

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    r = sesion.s.delete(url, params=params, headers=headers, auth=sesion.auth)

    return r


def create_or_update_property(sesion, property_file, property_name, property_value):
    old_value = get_property_value(sesion, property_file, property_name)

    if "result" in old_value.keys() and old_value["result"] == "property_not_found":
        r = "Adding: " + add_property(
            sesion, property_file, property_name, property_value
        )
    else:
        if property_value == old_value["PropertyValue"]:
            r = "No changes"
        else:
            r = "Updating: " + update_property(
                sesion, property_file, property_name, property_value
            )

    return r