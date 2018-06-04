from __future__ import with_statement
from random import randint
import sys
import string
import time
import random
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL

# Replace with FQDN's of your LDAP servers separated by commas.
hosts = (
        "node1.example.org:1636",
        "node2.example.org:1636"
        )

# Input LDAP DN and Password in the following variables

password = 'secret'

# 'cn=directory manager' for OpenDJ

DN = 'cn=directory manager'

f = open('countries.txt')
countries = f.readlines()
countryLength = len(countries) - 1
f.close()

f = open('firstnames.txt')
firstNames = f.readlines()
firstNamesLength = len(firstNames) - 1
f.close()

f = open('lastnames.txt')
lastNames = f.readlines()
lastNamesLength = len(lastNames) -1
f.close()

def getCountry():
    return countries[randint(0,countryLength)].strip()

def getFirstName():
    return firstNames[randint(0,firstNamesLength)].strip() 

def getLastName():
    return lastNames[randint(0,lastNamesLength)].strip()

def getInumQuad(n=4):
    hexChars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    s = ""
    i = 0
    while i < n:
        s = s + hexChars[randint(0,15)]
        i = i + 1
    return s

def genCustNumber():
    chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    s = ""
    i = 0
    while i < 8:
        s = s + chars[randint(0,9)]
        i = i + 1
    return s

def removeSpaces(s=""):
    return "".join(s.split())

def uniqueInum():
    gluuPersonInum = "0000!{}.{}.{}.{}".format(getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
    return gluuPersonInum

f = open('company_names.txt')
companyNames = f.readlines()
f.close()

# Check the replication status of OpenLDAP
'''
def replicationStatus():
    compare = []
    counts = []
    for host in hosts:
        try:
            ldap_uri = "ldaps://{}".format(host)
            print('Connecting to {}'.format(host))
            server = Server(ldap_uri, use_ssl=True)
            conn = Connection(server, DN, password)

            conn.bind()
            conn.search(search_base='o=gluu', search_scope=BASE, search_filter='(objectclass=*)', attributes=['+'])
                
            # Add the contextCSN to the compare list
        
            compare.append(conn.response[0]['attributes']['contextCSN'])
                
            # Search for entries in LDAP
        
            conn.search(search_base = 'o=gluu',
                     search_filter = '(cn=*)',
                     search_scope = SUBTREE)
            common = conn.entries
        
            # Count the number of entries in LDAP
                
            countVar = '{} total users: {}'.format(host, sum(1 for _ in common))
        
            # Append to the counts list
                
            counts.append(str(countVar))
        
        except:
            print("{} seems down".format(host))
        
    # Add server entries to log

    log = open("replication_log.log","a+")
    i=1
    for count in counts:
        user_log_entry = '{} \n'.format(count)
        print(user_log_entry)
        log.write(user_log_entry)
        i = i + 1

    # Test whether the indexCSN's match, an indicator of whether replication is currently working.
    # Write these to a log file for monitoring
    print("Replication CSN's =", compare)
    try:
        if all(x==compare[0] for x in compare):
            print('CSN match')
            with open("replication_log.log","a") as log:
                log.write('CSNs Synced @ ' + time.strftime("%a, %d %b %Y %H:%M:%S\n"))
        else:
            print('Replication out of sync')
            with open("replication_log.log","a") as log:
                log.write('CSN Out of sync @ ' + time.strftime("%a, %d %b %Y %H:%M:%S\n"))

    except Exception as ex:
        print('Something went wrong...')
        print(ex)
    print("\nSleeping for", 1, "seconds\n")
    time.sleep(1)
'''

def getoInum():
    try:
        rand = randint(0,len(hosts)-1)
        host = hosts[rand]
        ldap_uri = "ldaps://{}".format(host)
        print('Attempting to get inum from {}'.format(ldap_uri))
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        conn.search(search_base = 'o=gluu',
        search_filter = '(o=*)',
        search_scope = SUBTREE)
        inumRAW = conn.entries[1].entry_dn
        inum = inumRAW.replace('o=','').replace(',gluu','')
        print("inum is: {}".format(inum))
        return inum
    except Exception as ex:
        print("Cannot connect to host.")
        print(ex)

oInum = getoInum()

# Build Users

def buildData():

    totalUsers = 0
    for companyName in companyNames:

        companyName = companyName.strip()
        ownerGroupInum = '{}!{}'.format(oInum, uniqueInum())
        oCountry = getCountry()
        employeeList= []
        gluuPersonInum = "0000!{}.{}.{}.{}".format(getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
        personInum = '{}!{}'.format(oInum, gluuPersonInum)

        employeeList.append(personInum)
        personFirstName = getFirstName()
        personLastName = getLastName()
        dn = 'inum={}!{},ou=people,o={},o=gluu'.format(oInum, uniqueInum(), oInum)
        object_class = ['top', 'gluuPerson', 'gluuCustomPerson', 'eduPerson']
        totalUsers = totalUsers + 1
        attributes = {}
        attributes['displayName'] = '{} {}'.format(personFirstName, personLastName)
        attributes['givenName'] = personFirstName
        attributes['iName'] = personFirstName
        attributes['uid'] = 'user.{}'.format(totalUsers)
        attributes['mail'] = '{}.{}@{}.{}'.format(personFirstName, personLastName, removeSpaces(companyName), oCountry)
        attributes['gluuStatus'] = 'active'
        attributes['sn'] = personLastName
        attributes['cn'] = personFirstName
        attributes['userPassword'] = 'secret'
        addToLDAP(dn,object_class,attributes)

        dn = 'inum={},ou=groups,o={},o=gluu'.format(ownerGroupInum, oInum)
        object_class = ['top', 'gluuGroup']
        attributes['gluuGroupType'] = 'gluuGroup'
        attributes['inum'] = ownerGroupInum
        attributes['gluuStatus'] = 'active'
        attributes['displayName'] = '{} Owner Group'.format(companyName)
        attributes['member'] = 'inum={},ou=people,o={},o=gluu'.format(employeeList[0], oInum)
        addToLDAP(dn,object_class,attributes)


# Add Users to LDAP

def addToLDAP(dn,object_class,attributes):
    try:
        rand = randint(0,len(hosts)-1)
        host = hosts[rand]
        ldap_uri = "ldaps://{}".format(host)
        print('Connecting to {} and adding users.'.format(host))
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        conn.add(dn,object_class,attributes)
    except Exception as ex:
        print("Cannot connect to host.")
        print(ex)

while True:

    # Add 10 users
    print('Adding users...')
    buildData()
    print('Users added. \n')
