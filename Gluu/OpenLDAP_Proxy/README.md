# Proxying LDAP

Requirements:

OpenLDAP Gold

It is possible to proxy LDAP read/write requests based on DN's.

For example I want all requests going to ou=people,o=gluu to go to one LDAP server and all requests for ou=clients,o=gluu to go to another. All other requests should go to another LDAP server. This would presumably optimize performance on disk.
