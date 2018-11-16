# Remove all traces of Casa from LDAP

from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL, ALL_ATTRIBUTES
from pyDes import triple_des, PAD_PKCS5
import shutil
import os
import sys
import base64

def decodeBindPass(encPass, key):

    # Decode the encoded password using the salt

    print('Decoding bindPassword..\n')

    cipher = triple_des(key)
    decodedPass = cipher.decrypt(base64.b64decode(encPass), padmode=PAD_PKCS5)

    return decodedPass

def parseLdapProperties():

    # Function to automatically gather bindDN, bindPassword and LDAP Server hostname from ox-ldap.properties

    '''
    Sample from ox-ldap.properties:

    bindDN: cn=directory manager
    bindPassword: QsSS4SreDVo=
    servers: c4.gluu.org:1636,c5.gluu.org:1636
    '''

    print('Gathering LDAP Server Properties..\n')

    ldapPropertiesFN = '/etc/gluu/conf/ox-ldap.properties'
    ldapFile = open(ldapPropertiesFN, 'r')
    saltFN = '/etc/gluu/conf/salt'

    # Gather salt for decoding
    f = open(saltFN)
    salt = f.read()
    f.close()
    salt = salt.split("=")[1].strip()

    # The information we're looking for
    props = [
            'bindDN',
            'bindPassword',
            'servers'
            ]
    # Assigning variables

    bindDN = ''
    bindPassword = ''
    host = ''

    # Parse through LDAP properties file for bind information

    for prop in props:
        for line in ldapFile:
            if prop in line:
                propTmp = line
                propTmp = propTmp.split(':', 1)
                propTmp = propTmp[1].split(',')
                propTmp = propTmp[0].strip()
                if props[0] in prop:
                    bindDN = propTmp
                    print bindDN
                    break
                elif props[1] in prop:
                    encodedPass = propTmp
                    bindPassword = decodeBindPass(encodedPass, salt)
                    print bindPassword
                    break
                elif props[2] in prop:
                    host = propTmp
                    print host
                    break

    config = {'bindDN':bindDN,'bindPassword':bindPassword,'host':host}

    return config

# LDAP Bind information
ldapProps = parseLdapProperties()
bindDN = ldapProps['bindDN']
bindPassword = ldapProps['bindPassword']
host = ldapProps['host']

def bindLDAP():

    # Bind to LDAP and return the connection

    ldap_uri = "ldaps://{}".format(host)
    print('Connecting to ' +  host)
    server = Server(ldap_uri, use_ssl=True)
    conn = Connection(server, bindDN, bindPassword)
    try:
        conn.bind()
    except:
        print('Could not bind to LDAP.')
    return conn

# Share a single LDAP connection between functions 

conn = bindLDAP()

def getoInum():

    # Gather the organizational inum of the LDAP server

    conn.search(search_base = 'o=gluu',
    search_filter = '(o=*)',
    search_scope = SUBTREE)
    inumRAW = conn.entries[1].entry_dn
    inum = inumRAW.replace('o=','').replace(',gluu','')
    print("inum is: {}".format(inum))
    return inum

oInum = getoInum()

def delCasaUserAttributes():

    print('Deleting Casa User Attributes..\n')

    attrs = [
                'oxPreferredMethod',
                'oxOTPDevices',
                'oxMobileDevices',
                'oxStrongAuthPolicy',
                'oxTrustedDevicesInfo',
                'oxUnlinkedExternalUids'
                ]
    
    # Iteratively use attrs for search filter to minimize returned users
    # I'm not sure if it's more beneficial to do an unindexed search on
    # the attribute, or pull all uid's, which could be quite a large number.

    for attr in attrs:

        conn.search(search_base = 'ou=people,o={0},o=gluu'.format(oInum),
        search_filter = '({0}=*)'.format(attr),
        search_scope = SUBTREE,
        attributes=ALL_ATTRIBUTES)

        for entry in conn.response:
            print('Removing {0} from '.format(attr) + entry['attributes']['uid'])
            conn.modify(entry['dn'],{attr: [(MODIFY_DELETE, [])]})

def delCustomScripts():

    print('Deleting Casa Custom Scripts..\n')

    scriptNames = [
            'client_registration',
            'casa'
            ]

    conn.search(search_base = 'ou=scripts,o={0},o=gluu'.format(oInum),
    search_filter = '(objectClass=*)',
    search_scope = SUBTREE,
    attributes='displayName')
    
    print conn.response
    
    for script in scriptNames:
        for entry in conn.response:
            if script in entry['attributes']['displayName']:
                print('Removing script {0}'.format(entry['attributes']['displayName']))
                conn.delete(entry['dn'])

def delCasaClients():

    print('Deleting Casa Clients..\n')

    conn.search(search_base = 'ou=clients,o={0},o=gluu'.format(oInum),
    search_filter = '(displayName=gluu-casa*)',
    search_scope = SUBTREE,
    attributes=ALL_ATTRIBUTES)

    for entry in conn.response:
        print('Removing client {0}'.format(entry['attributes']['displayName']))
        conn.delete(entry['dn'])

def delCasaFiles():

    print('Deleting Casa Files..\n')
    shutil.rmtree('/opt/gluu/jetty/casa/')
    os.remove('/etc/gluu/conf/casa.json')
    os.remove('/etc/default/casa')

delCasaUserAttributes()
delCasaClients()
delCustomScripts()
delCasaFiles()

print('Casa clean up complete!\n')
# Unbind LDAP connection
conn.unbind()