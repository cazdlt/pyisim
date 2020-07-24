# isim
Python client for IBM Security Identity Manager (ISIM/ITIM) web services (SOAP and REST APIs) <br>
Tested on ISIM 7.0.1 FP13 and ISIM 7.0.2 FP2
Due to API limitations some functionalities are served through ISIM's REST API and some other through ISIM SOAP Web Services. <br>

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
