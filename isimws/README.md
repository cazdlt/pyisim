# isim
Python client for IBM Security Identity Manager web services (SOAP and REST APIs) <br>
Due to API limitations some functionalities are served through ISIM's REST API and some other through ISIM SOAP Web Services. 

- Functionalities
    - Authentication
    - Request Access 
    - Complete Manual Activities
        - Approval
        - Work Order
    - Create:
        - Person
            - Need to Modify isimws.classes.Person to match your attributes (for now)
        - BPPerson
            - Need to Modify isimws.classes.BPPerson to match your attributes (for now)
        - Static Roles
        - Provisioning Policies
    - Modify:
        - Static Roles
        - Provisioning Policies
    - Delete:
        - Services
    - Search: 
        - Workflow
        - Service
        - Static Role
        - Provisioning Policy
        - Person
        - BPPerson
        - OrgUnit
        - Access
        - Manual activity
        - Forms

- TODO:
    - Improve project structure
        - Use english for everything
    - Improve documentation
        - Basic usage
        - Batch loads
        - Requirements
    - Create class APIs for Service and Access items
    - Generalize Person and BPPerson attribute handling
        - *Abstract* class?
    - Add search to class initialization:
        - Person
        - Business Partner Person
        - Static Role
        - Provisioning Policy
    - Add at least modify and delete operations for Person classes
