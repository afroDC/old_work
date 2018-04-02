from __future__ import with_statement
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL, ALL_ATTRIBUTES


# Code to delete all users in an LDAP for developmental purposes.

# insert hostname or ip here
host = '<host>:1636' 
# For OpenLDAP
# DN = 'cn=directory manager,o=gluu'
# For OpenDJ use:
DN = 'cn=directory manager'
password = '<pass>'

def delAll():
    try:
        ldap_uri = "ldaps://{}".format(host)
        print('Connecting to ', host)
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)

        conn.bind()
        conn.search(search_base = 'o=gluu',
        search_filter = '(&(cn=*)(!(uid=admin)))',
        search_scope = SUBTREE,
        attributes=ALL_ATTRIBUTES)

        for entry in conn.response:
            print(entry['dn'])
            conn.delete(entry['dn'])
        conn.unbind()

    except:
        print("Cannot connect to host.")

delAll()
