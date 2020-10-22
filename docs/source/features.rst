================
Features
================

Currently, the library consists of 7 modules for the ISIM application
server and an inner package for working with ISIM7 Virtual Appliance.
However, from the 7 modules you (most likely) will only interact with
the authorization, search and entities API.

The library uses
`Requests <https://requests.readthedocs.io/en/master/>`__ and
`Zeep <https://docs.python-zeep.org/en/master/>`__ extensively for
communication with ISIM APIs.

The following are the currently available
features in it for the ISIM Application Server. Authorization (login) is
clearly also available.

+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|    Entities\Operations    | Search | DN Lookup | Add | Delete | Suspend | Restore |      Modify     |
+===========================+========+===========+=====+========+=========+=========+=================+
|           People          |    ✓   |           |  ✓  |    ✓   |    ✓    |    ✓    |        ✓        |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|       Dynamic Roles       |    ✓   |     ✓     |  ✓  |    ✓   |         |         |        ✓        |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|        Static Roles       |    ✓   |     ✓     |  ✓  |    ✓   |         |         |        ✓        |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|   Provisioning Policies   |    ✓   |           |  ✓  |    ✓   |         |         |        ✓        |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|         Activities        |    ✓   |           |     |        |         |         |    (Complete)   |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
| Organizational Containers |    ✓   |     ✓     |     |        |         |         |                 |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|          Services         |    ✓   |           |     |        |         |         |                 |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|           Access          |    ✓   |           |     |        |         |         |    (Request)    |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|           Groups          |    ✓   |           |     |        |         |         |                 |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+
|          Accounts         |    ✓   |           |  ✓  |    ✓   |    ✓    |    ✓    |  ✓ (and orphan) |
+---------------------------+--------+-----------+-----+--------+---------+---------+-----------------+

The following are the currently available features in it for the ISIM7 Virtual Appliance. 
Authorization (login) is clearly also available:

* Search system properties 
* Create system properties 
* Modify system properties