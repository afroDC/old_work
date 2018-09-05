from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL
from random import randint

# Change to your host
host = "c6.gluu.org:1636"

# Input LDAP DN and Password in the following variables
password = 'secret'

# 'cn=directory manager,o=gluu' for OpenLDAP
DN = 'cn=directory manager'

# Gather the organizational inum so we can search under scripts

def getoInum():
    try:
        ldap_uri = "ldaps://{}".format(host)
        print('Attempting to determine organization inum from {}'.format(ldap_uri))
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        print('Connected.')
        conn.search(search_base = 'o=gluu',
        search_filter = '(o=*)',
        search_scope = SUBTREE)
        inumRAW = conn.entries[1].entry_dn
        inum = inumRAW.replace('o=','').replace(',gluu','')
        print("oInum is: {}".format(inum))
        return inum
    except Exception as ex:
        print("Cannot connect to host.")
        print(ex)

def getInumQuad(n=4):
    hexChars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    s = ""
    i = 0
    while i < n:
        s = s + hexChars[randint(0,15)]
        i = i + 1
    return s

def uniqueInum():
    gluuPersonInum = "0000!{}.{}.{}.{}".format(getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
    return gluuPersonInum

def addToLDAP(args):
    
    users = args[0]
    oInum = args[1]
    testuser = 'example'

    userToAdd = testuser + str(users).zfill(5)
    print ("Adding User: " + userToAdd)
    personFirstName = testuser
    personLastName = str(users).zfill(5)
    personInum = 'inum={}!{}'.format(oInum, uniqueInum())
    dn = '{},ou=people,o={},o=gluu'.format(personInum, oInum)
    object_class = ['top', 'gluuPerson', 'gluuCustomPerson', 'eduPerson']
    
    attributes = {}
    attributes['displayName'] = '{} {}'.format(personFirstName, personLastName)
    attributes['givenName'] = personFirstName
    attributes['iName'] = personFirstName
    attributes['uid'] = userToAdd
    attributes['mail'] = '{}.{}@gluu.org'.format(personFirstName, personLastName)
    attributes['gluuStatus'] = 'active'
    attributes['sn'] = personLastName
    attributes['cn'] = personFirstName
    attributes['userPassword'] = 'secret'

    try:
        ldap_uri = "ldaps://{}".format(host)
        print('Connecting to {} and adding users.'.format(host))
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        conn.add(dn,object_class,attributes)
        result = conn.result
        if "success" in result.values():
            print("Success.")
            conn.unbind()
        else:
            print("Failed:")
            print conn.result
            conn.unbind()
    except Exception as ex:
        print("Cannot connect to host.")
        print(ex)
