# PyISIM

[![PyPI version shields.io](https://img.shields.io/pypi/v/pyisim)](https://pypi.python.org/pypi/pyisim/)
[![PyPI status](https://img.shields.io/pypi/status/pyisim)](https://pypi.python.org/pypi/pyisim/)
[![PyPI license](https://img.shields.io/pypi/l/pyisim)](https://pypi.python.org/pypi/pyisim/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

<!-- https://img.shields.io/pypi/l/pyisim -->

Python client for IBM Security Identity Manager (ISIM / ITIM) web services (SOAP and REST APIs) <br>
Tested on ISIM 7.0.1 FP13 and ISIM 7.0.2 FP2
Due to API limitations some functionalities are served through ISIM's REST API and some other through ISIM SOAP Web Services.

## Docs
You can read the full documentation [here](https://pyisim.readthedocs.io/en/latest/)

## Examples

-   Login

```py
from pyisim.auth import Session
user="itim manager"
password="secret"
cert="./my_certificate.cer"
url="iam.isim.com"
sess=Session(url,user,password,cert)
```

_Every example after assumes you have already a valid Session object named sess_

-   Creating people

```py
from pyisim.entities import Person
info_persona={
    "employeenumber": "1015463230",
    "correo": "cazdlt@gmail.com",
    "title": "Especialista de producto",
    "departmentnumber":"IBM",
}
persona = Person(sess, person_attrs=info_persona)
persona.add(sess,"my org","my justification")
```

-   Modifying people

```py
from pyisim import search
persona = search.people(sess,Person,"employeenumber","1015463230",limit=1)[0]
persona.title="CEO"
persona.modify(sess,"my justification")
```

-   Custom Person/BPPerson entities

```py
from pyisim import Person
from pyisim import search

class MyBPPerson(Person):

    profile_name="BPPerson"

    def __init__(self,info,first_name=None):
        if first_name is None:
                first_name = "Andrés"
        info["givenname"] = first_name

        super().__init__(person_attrs=info)

MyBPPerson({"sn":"Zamora"}).add(sess,"my org","New BPPerson")
```

-   Access request

```py
from pyisim import search
accesses=search.access(sess,search_filter="*Consulta*",limit=5)
person=search.people(session,by="givenname",search_filter="Juan",limit=1)[0]
person.request_access(session,accesses,"justification")
```

-   Approve activity

```py
request_id="9585474949338"
actividad=search.activities(session,by="requestId",search_filter=request_id,limit=1)[0]
actividad.complete(sess,"approve","justification")
```

-   Fulfill RFI

```py
request_id="123483274614"
form=[
    {
        "name":"description",
        "value":[dn_rol],
    },
    ...
]
actividad=search.activities(session,by="requestId",search_filter=request_id)[0]
actividad.complete(sess,form,"justification")
```

-   Update property files (ISIM VA)

```py
from pyisim.va.auth import VASession
from pyisim.va.configure import update_property


u="admin@local"
p="secret"
url="iam.isimva.com"
cert="./mycert.cer"

s=VASession(u,p,url,cert)

property_file="CustomLabels.properties"
property_name="scriptframework.properties"
property_value="ITIM.java.access.util"
update_property.create_or_update_property(s,property_file,property_name,property_value)
```

## Functionalities

|    Entities\Operations    | Search | DN Lookup | Add | Delete | Suspend | Restore |      Modify     |
|:-------------------------:|:------:|:---------:|:---:|:------:|:-------:|:-------:|:---------------:|
|           People          |    ✓   |           |  ✓  |    ✓   |    ✓    |    ✓    |        ✓        |
|       Dynamic Roles       |    ✓   |     ✓     |  ✓  |    ✓   |         |         |        ✓        |
|        Static Roles       |    ✓   |     ✓     |  ✓  |    ✓   |         |         |        ✓        |
|   Provisioning Policies   |    ✓   |           |  ✓  |    ✓   |         |         |        ✓        |
|         Activities        |    ✓   |           |     |        |         |         |    (Complete)   |
| Organizational Containers |    ✓   |     ✓     |     |        |         |         |                 |
|          Services         |    ✓   |           |     |        |         |         |                 |
|           Access          |    ✓   |           |     |        |         |         |    (Request)    |
|           Groups          |    ✓   |           |     |        |         |         |                 |
|          Accounts         |    ✓   |           |  ✓  |    ✓   |    ✓    |    ✓    |  ✓ (and orphan) |

<br>

-   ISIM VA Utilities:
    -   Authentication
    -   Create/Search/Update property files

## TODO
*in priority order*
1. Normalize request responses
2. Add operations to services
    -   DN Lookup
    -   Add
    -   Modify
    -   Delete
    -   Test connection
3. Add some complex use cases to the documentation
4. Fix formatting (use snake_case, use english) on the client classes (soap.py, rest.py)

