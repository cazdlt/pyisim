# isim
Python client for IBM Security Identity Manager (ISIM/ITIM) web services (SOAP and REST APIs) <br>
Tested on ISIM 7.0.1 FP13 and ISIM 7.0.2 FP2
Due to API limitations some functionalities are served through ISIM's REST API and some other through ISIM SOAP Web Services. <br>


Usage example:

- Login
```py
from isimws.auth import Session
user="itim manager"
password="secret"
cert="./my_certificate.cer"
url="isim.deltaits.com"
sess=Session(url,user,password,cert)
```

*Every example after assumes you have already a valid Session object named sess*
- Creating people
```py
from isimws.entities import Person
info_persona={
    "employeenumber": "1015463230",
    "correo": "cazdlt@gmail.com",
    "title": "Especialista de producto",
    "departmentnumber":"IBM",
}
persona = Person(sess, person_attrs=info_persona)
persona.add(sess,"my org","my justification")
```
- Modifying people
```py
from isimws import search
persona = search.people(sess,Person,"employeenumber","1015463230",limit=1)[0]
persona.title="CEO"
persona.modify(sess,"my justification")
```

- Custom Person/BPPerson entities
```py
from isimws import Person
from isimws import search

class MyBPPerson(Person):
    
    profile_name="BPPerson"

    def __init__(self,info,first_name=None):
        if first_name is None:
                first_name = "Andrés"
        info["givenname"] = first_name

        super().__init__(person_attrs=info)

MyBPPerson({"sn":"Zamora"}).add(sess,"my org","New BPPerson")  
```

- Access request 
```py
from isimws import search
accesses=search.access(sess,filter="*Consulta*",limit=5)
person=search.people(session,by="givenname",filter="Juan",limit=1)[0]
person.request_access(session,accesses,"justification")
```

- Approve activity
```py
request_id="9585474949338"
actividad=search.activities(session,by="requestId",filter=request_id,limit=1)[0]
actividad.complete(sess,"Aprobado","justification")
```

- Fulfill RFI
```py
request_id="123483274614"
form=formulario_rfi=[{
                "name":"description",
                "value":[dn_rol],
            },...]
actividad=search.activities(session,by="requestId",filter=request_id)[0]
actividad.complete(sess,form,"justification")
```

- Update property files (ISIM VA)
```py
from isimws.va.auth import Session
from isimws.va.configure import update_property


u="admin@local"
p="secret"
url="isimva.deltaits.com"
cert="./mycert.cer"

s=Session(u,p,url,cert)

property_file="CustomLabels.properties"
property_name="scriptframework.properties"
property_value="ITIM.java.access.util"
update_property.create_or_update_property(session,property_file,property_name,property_value)
```

- Functionalities
    - TLS Client
    - Authentication
    - People
        - Add
        - Modify
        - Search
        - Lookup
        - Request access (and search/lookup)
        - Create custom Person entities (BPPerson, etc..)
    - Activities
        - Search
        - Lookup
        - Complete
            - Approvals
            - Work Orders
            - RFIs
    - Static roles
        - Search
        - Lookup
        - Add
        - Modify
        - Delete
    - Provisioning policies
        - Add
        - Modify
        - Search
        - Delete
    - Services
        - Search
    - ISIM VA Utilities:
        - Create/Search/Update property files

- TODO:
    - Improve documentation
        - Basic usage
        - Requirements
    - Improve activity search by request id (does not work with the default methods)
    - Add operations to services
    - Publish on PyPi
    - Normalize request responses
    - Translate docstrings and exceptions into english
        - And, if it's in spanish, everything else in the high level API (entities/search/auth)


