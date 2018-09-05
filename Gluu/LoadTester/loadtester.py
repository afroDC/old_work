import requests
import urllib3
import time
from random import randint
from base64 import b64encode
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL

urllib3.disable_warnings()

login = 'https://example.gluu.org/identity/home.htm'
logout = 'https://example.gluu.org/identity/logout'

testuser = 'example'
password = 'secret'
userlist = []

def getoInum(host,password,DN):
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

def loadtest(username):

    r = requests.get(login, verify=False)

    if r.status_code == 200:
        print('Initial request successful.')
        time.sleep(1) 
    else:
        print r.status_code

    r = requests.get(login, auth=(username,password), verify=False)

    if r.status_code == 200:
        print('Logged in as {}'.format(username))
        r = requests.get(logout, verify=False)
        if r.status_code == 200:
            print('Logged out as {}'.format(username))
        else:
            print r.status_code
    else:
        print('Login failed.')
        print r.status_code
