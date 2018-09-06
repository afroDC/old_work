import multiprocessing as mp
import random
import string
import time
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL
from random import randint

import loadtester

# Gather the organizational inum  once so we don't waste cycles gathering it again.


# Change to your host
host = "example.gluu.org:1636"

# Input LDAP DN and Password in the following variables
password = 'secret'

# 'cn=directory manager,o=gluu' for OpenLDAP
DN = 'cn=directory manager'

testuser = 'example'
userlist = []

oInum = loadtester.getoInum(host,password,DN)

def getUserList():
    print("Gathering all test users into memory.")
    try:
        ldap_uri = "ldaps://{}".format(host)
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        searchBase = 'ou=people,o={},o=gluu'.format(oInum)
        conn.search(search_base = searchBase,
        search_filter = '(uid={}*)'.format(testuser),
        search_scope = SUBTREE,
        attributes=['uid'])
        for entry in conn.entries:
            userlist.append(entry['uid'])
        print("Done.")
        return userlist
    except Exception as ex:
        print("Cannot connect to host.")
        print(ex)

userlist = getUserList()

def worker(tasks):
    username = str(userlist[randint(0, len(userlist)-1)]) 
    loadtester.loadtest(username)

def main():

    pool = mp.Pool()
    total_tasks = 50000
    tasks = range(total_tasks)

    results = pool.map_async(worker, tasks).get(5000)
    pool.close()
    pool.join()


if __name__ == '__main__':
    main()
