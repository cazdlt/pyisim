==========================
Examples
==========================

Login
--------------------

.. code:: py

    from pyisim.auth import Session
    user="itim manager"
    password="secret"
    cert="./my_certificate.cer"
    url="iam.isim.com"
    sess=Session(url,user,password,cert)

*Every example after assumes you have already a valid Session object
named sess*

Creating people
--------------------

.. code:: py

    from pyisim.entities import Person
    info_persona={
        "employeenumber": "1015463230",
        "correo": "cazdlt@gmail.com",
        "title": "Specialist",
        "departmentnumber":"Github",
    }
    persona = Person(sess, person_attrs=info_persona)
    persona.add(sess,"my org","my justification")

Modifying people
--------------------

.. code:: py

    from pyisim import search
    persona = search.people(sess, by="employeenumber", search_filter="1015463230", limit=1)[0]
    persona.title="CEO"
    persona.modify(sess, "my justification")
    

Obtaining the current logged in person and doing stuff
------------------------------------------------------------

*There are create, modify, search, suspend, request access, restore and delete operations available for people*

.. code:: py

    from pyisim.auth import Session

    s=Session(url, "cazdlt", "secretpw", "my_certificate.cer")
    me=s.current_person()
    me.modify(s, "my justification", changes={"mail":"cazdlt@gmail.com"})
    me.suspend(s, "suspending myself", suspend_accounts=True)

Custom Person/BPPerson entities
----------------------------------------

.. code:: py

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

Access request
--------------------

.. code:: py

    from pyisim import search
    accesses=search.access(sess, search_filter="*Consulta*", limit=5)
    person=search.people(session, by="givenname", search_filter="Juan",limit=1)[0]
    person.request_access(session,accesses, "justification")

Approve activity
--------------------

.. code:: py

    request_id="9585474949338"
    actividad=search.activities(
        session,
        by="requestId",
        search_filter=request_id,
        limit=1
    )[0]
    actividad.complete(sess, "approve", "justification")

Fulfill RFI
--------------------

.. code:: py

    request_id="123483274614"
    form=[
        {
            "name":"title",
            "value":["Analyst"],
        },
    ]
    actividad = search.activities(session, by="requestId", search_filter=request_id)[0]
    actividad.complete(sess, form, "justification")

Creating roles
--------------------

*Static and Dynamic role use the same methods, but* ``rule`` *and* ``scope`` *attributes are specific to dynamic roles.*

*Documentation on role attributes is under the* ``RoleAttributes`` *dataclass. Initializing roles can also be done using this data class. This can be used to get intellicode and type hinting.*

.. code:: py

    from pyisim.auth import Session
    from pyisim import search
    from pysim.entities import DynamicRole

    s=Session(url, "cazdlt", "secretpw", "my_certificate.cer")

    parent = search.organizational_container(s, "organizations", "My Organization")[0]

    owners = search.people(s, by="employeenumber", search_filter="1015463230")
    owners_roles = search.roles(s, search_filter="ITIM Administrators")

    # creación
    name="dynrol_prueba"
    rolinfo = {
        "name": name,
        "description": "dynrol_prueba",
        "parent": parent,
        "classification": "role.classification.business",
        "access_option": 2,
        "access_category": "Role",
        "owners": [o.dn for o in owners] + [o.dn for o in owners_roles],
        "rule": "(title=ROLETEST)",
    }
    rol = DynamicRole(s, role_attrs=rolinfo)
    rol.add(s)

More role operations
--------------------

.. code:: py

    from pyisim.auth import Session
    from pyisim import search

    s=Session(url, "cazdlt", "secretpw", "my_certificate.cer")

    rol=search.roles(s,search_filter="My Role")

    #can modify using the object attributes
    rol.description = "new description"
    rol.modify(s) 

    #can also modify using a changes dictionary
    changes={"description":"newer description"}
    rol.modify(s,changes) 

    rol.delete(s)

Creating provisioning policies
----------------------------------------

*Documentation on provisioning policy attributes is under the* ``ProvisioningPolicyAttributes``, ``ProvisioningPolicyEntitlementValue`` *and* ``ProvisioningPolicyParameterValue`` *dataclasses. Initializing policies can also be done using this data classes. This can be used to get intellicode and type hinting.*

*Modification and deletion are done the same way as the other entities (with* ``policy.modify()`` *and* ``policy.delete()`` *)*

.. code:: py

    from pyisim.auth import Session
    from pyisim import search
    from pysim.entities import ProvisioningPolicy

    s=Session(url, "cazdlt", "secretpw", "my_certificate.cer")

    name="test"
    parent = search.organizational_container(s, "organizations", test_org)[0]
    service = search.service(s, parent, search_filter="Directorio Activo")[0]

    #I know this can get very complex, so the library is also very flexible
    entitlements = {
        service.dn: {
            "automatic": False,
            "workflow": None,
            "parameters": {
                "ercompany": [
                    {
                        "enforcement": "Default",
                        "type": "script",
                        "values": "return 'test';",
                    },
                    {
                        "enforcement": "Excluded",
                        "type": "null",
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["test1", "test2"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "Constant",
                        "values": ["test3"],
                    },
                    {
                        "enforcement": "Allowed",
                        "type": "REGEX",
                        "values": r"^[\s\w]+$",
                    },
                ],
                "eradfax": [
                    {
                        "enforcement": "Allowed",
                        "type": "constant",
                        "values": ["1018117"],
                    }
                ],
            },
        },
        "*": {"automatic": False, "workflow": None, "parameters": {}},
    }
    policy = {
        "description": "test",
        "name": name,
        "parent": parent,
        "priority": 10000,
        "memberships": [x.dn for x in search.roles(s, search_filter="Auditor")],
        "enabled": False,
        "entitlements": entitlements,
    }
    pp = ProvisioningPolicy(s, policy_attrs=policy)
    pp.add(s)

Custom sessions
----------------------------------------

.. code:: py

    from pyisim.auth import Session

    class CustomISIMEnvironment(Session):
        
        def __init__(self, username,password,env):

            urls = {
                "dev": "https://dev.myisim.com:9082",
                "qa": "https://qa.myisim.com:9082",
                "pr": "https://www.myisim.com"
            }

            cert = "myCA.crt"

            super().__init__(urls[env],username,password,cert)

Update property files (ISIM VA)
----------------------------------------

.. code:: py

    from pyisim.va.auth import Session
    from pyisim.va.configure import update_property


    u="admin@local"
    p="secret"
    url="iam.isimva.com"
    cert="./mycert.cer"

    s=Session(u,p,url,cert)

    property_file="CustomLabels.properties"
    property_name="scriptframework.properties"
    property_value="ITIM.java.access.util"
    update_property.create_or_update_property(session,property_file,property_name,property_value)