import sys
import string
import time
import random

from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL

# Replace with FQDN's of your LDAP servers separated by commas
hosts = (
        )
# Input LDAP DN and Password in the following variables
password = ''
DN       = 'cn=directory manager,o=gluu'
def getName():
    name = ''
    for i in range(10):
        name += random.choice(string.letters)
    return name

def replicationStatus():
    compare = []
    for host in hosts:
        try:
            ldap_uri = "ldaps://{}:1636".format(host)
            server = Server(ldap_uri, use_ssl=True)
            conn = Connection(server, DN, password)

            conn.bind()
            conn.search(search_base='o=gluu', search_scope=BASE, search_filter='(objectclass=*)', attributes=['+'])

            #print host, conn.response[0]['attributes']['contextCSN']
            compare.append(conn.response[0]['attributes']['contextCSN'])
        except:
            print host, "seems down"

    # Test whether the indexCSN's match, an indicator of whether replication is currently working.
    # Write these to a log file for monitoring

    try:
        if all(x==compare[0] for x in compare):
            print 'CSN match'
            with open("replication_log.log","a") as log:
                log.write('Synced @ ' + time.strftime("%a, %d %b %Y %H:%M:%S\n"))
        else:
            print 'Replication out of sync'
            with open("replication_log.log","a") as log:
                log.write('Out of sync @ ' + time.strftime("%a, %d %b %Y %H:%M:%S\n"))

    except:
        print 'Something went wrong...'
    print "\nSleeping for", 1, "seconds\n"
    time.sleep(1)

def addUser():
    try:
        host = random.choice(hosts)

        ldap_uri = "ldaps://{}:1636".format(host)
        server = Server(ldap_uri)

        conn = Connection(server, DN, password)
        conn.bind()

        uid = '{0}@{1}'.format(time.time(), host)

        name = getName()
        sn = getName()

        cn = name + ' ' + sn

        dn = "cn={}, o=gluu".format(cn)

        attributes={
                                         'objectClass': ['top', 'inetOrgPerson'],
                                         'givenname': name,
                                         "cn": cn,
                                         'sn': sn,
                                         'uid': uid,


                                     }


        conn.add(dn, attributes=attributes )


        print "User added to", host

    except:
        print host, "seems to be down"

while True:
    n = 10
    i = 0
    while n>i:
        addUser()
        i = i +1
    replicationStatus()
