from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL, ALL_ATTRIBUTES

# Remove all traces of Casa from LDAP

host = 'server:1636' 
DN = 'cn=directory manager'
password = 'secret'

def bindLDAP():

    ldap_uri = "ldaps://{}".format(host)
    print('Connecting to ' +  host)
    server = Server(ldap_uri, use_ssl=True)
    conn = Connection(server, DN, password)
    try:
        conn.bind()
    except:
        print('Could not bind to LDAP.')
    return conn

conn = bindLDAP()

def getoInum():

    conn.search(search_base = 'o=gluu',
    search_filter = '(o=*)',
    search_scope = SUBTREE)
    inumRAW = conn.entries[1].entry_dn
    inum = inumRAW.replace('o=','').replace(',gluu','')
    print("inum is: {}".format(inum))
    return inum

oInum = getoInum()

def delCasaUserAttributes():

    attrs = [
                'oxPreferredMethod',
                'oxOTPDevices',
                'oxMobileDevices',
                'oxStrongAuthPolicy',
                'oxTrustedDevicesInfo',
                'oxUnlinkedExternalUids'
                ]
    
    # Connect to LDAP and return all user entries

    conn.search(search_base = 'o=gluu',
    search_filter = '(uid=*)',
    search_scope = SUBTREE,
    attributes=ALL_ATTRIBUTES)

    print('Deleting Casa Attributes From All Users..')

    for entry in conn.response:
        for attr in attrs:
            if attr in entry['attributes']:
                print('Removing {0} from '.format(attr) + entry['attributes']['uid'])
                conn.modify(entry['dn'],{attr: [(MODIFY_DELETE, [])]})

def delCustomScripts():

    print('Deleting Casa Custom Scripts..')

    conn.search(search_base = 'o=gluu',
    search_filter = '(uid=*)',
    search_scope = SUBTREE,
    attributes=ALL_ATTRIBUTES)
    
    # something

def delCasaClients():

    print('Deleting Casa Clients..')

    conn.search(search_base = 'ou=clients,o={0},o=gluu'.format(oInum),
    search_filter = '(displayName=gluu-casa*)',
    search_scope = SUBTREE,
    attributes=ALL_ATTRIBUTES)

    for entry in conn.response:
        print('Removing client {0}'.format(entry['attributes']['displayName']))
        conn.delete(entry['dn'])

delCasaUserAttributes()
delCasaClients()

# Unbind LDAP connection
conn.unbind()
