# isim
Python client for IBM Security Identity Manager (ISIM/ITIM) web services (SOAP and REST APIs) <br>
Tested on ISIM 7.0.1 FP13 and ISIM 7.0.2 FP2
Due to API limitations some functionalities are served through ISIM's REST API and some other through ISIM SOAP Web Services. <br>

Usage example:

- Login
```py
from isimws.auth import Session
user=****
password=****
cert="./my_certificate.cer"
sess=Session(user,password,cert)
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
persona = Person(sess, **info_persona)
persona.crear(sess,"my justification")
```
- Modifying people
```py
from isimws import search
persona = search.people(sess,Person,"employeenumber","1015463230",limit=1)[0]
persona.title="Gerente"
persona.modificar(sess,"my justification")
```

- Custom Person/BPPerson entities
```py
from isimws import Person
from isimws import search
class MyBPPerson(Person):
    
    orgid = search.ou("Organization","IBM").id
    profile_name="BPPerson"
    excluded_attributes=["cn","sn","givenname","employeenumber","erlocale"]

    def __init__(self,first_name,**kwargs):
        if first_name is None:
                first_name = "Andrés"
        self.givenname = nombre

        for attr, value in kwargs.items():
            setattr(self, attr, value)

MyBPPerson("Juan",**info_persona).crear(sess,"New BPPerson")  
```

- Access request 
```py
from isimws import search
accesses=search.access(sess,filter="*Consulta*",limit=5)
person=search.people(sesion,MyBPPerson,"givenname","Juan",limit=1)[0]
person.solicitar_accesos(sesion,accesses,"justification")
```

- Approve activity
```py
request_id="9585474949338"
actividad=search.activities(sesion,by="requestId",filter=request_id,limit=1)[0]
actividad.completar(sess,"Aprobado","justification")
```

- Fulfill RFI
```py
request_id="123483274614"
form=formulario_rfi=[{
                "name":"description",
                "value":[dn_rol],
            },...]
actividad=search.activities(sesion,by="requestId",filter=request_id)[0]
actividad.completar(sess,form,"justification")
```

- Functionalities
    - TLS Client
    - Authentication
    - Access request
    - Complete Manual Activities
        - Approval
        - Work Order
        - RFI
    - Create:
        - Person (and custom Person entities)
        - BPPerson (and custom BPPPerson entities)
        - Static Roles
        - Provisioning Policies
    - Modify:
        - Person (and custom Person entities)
        - BPPerson (and custom BPPPerson entities)
        - Static Roles
        - Provisioning Policies
    - Delete:
        - Services
    - Search: 
        - Most things
        - Currently implementing interfaces to ease this task


- TODO:
    - Improve project structure
        - Use english for everything
    - Improve documentation
        - Basic usage
        - Batch loads
        - Requirements
    - Create class bindings for all searchable items
    - Delete operations for Person classes
    - Generalize policy and role creation
    - Improve initialization after search operations
