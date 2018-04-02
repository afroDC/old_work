from random import randint
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL, ALL_ATTRIBUTES
import time

host = '<host>:1636'
DN = 'cn=directory manager'
# User 'cn=directory manager,o=gluu' for OpenLDAP
password = '<pass>'

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

def getoInum():
    try:
        ldap_uri = "ldaps://{}".format(host)
        print('Connecting to ', host)
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        conn.search(search_base = 'o=gluu',
        search_filter = '(o=*)',
        search_scope = SUBTREE)
        inumRAW = conn.entries[1].entry_dn
        inum = inumRAW.replace('o=','').replace(',gluu','')
        return inum
    except:
        print("Cannot connect to host.")

oInum = getoInum()

def addToLDAP(dn,object_class,attributes):
    try:
        ldap_uri = "ldaps://{}".format(host)
        print('Connecting to ', host)
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        conn.add(dn,object_class,attributes)
    except:
        print("Cannot connect to host.")

def buildData():
    totalUsers = 0
    for companyName in companyNames:

        companyName =companyName.strip()
        ownerGroupInum = '{}!{}'.format(oInum, uniqueInum())
        oCountry = getCountry()
        employeeList= []
        numPeople = randint(1,27)
        gluuPersonInum = "0000!{}.{}.{}.{}".format(getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
        personInum = '{}!{}'.format(oInum, gluuPersonInum)

        while numPeople > 0:

            numPeople = numPeople - 1
            totalUsers = totalUsers + 1
            employeeList.append(personInum)
            personFirstName = getFirstName()
            personLastName = getLastName()
            dn = 'inum={}!{},ou=people,o={},o=gluu'.format(oInum, uniqueInum(), oInum)
            object_class = ['top', 'gluuPerson', 'gluuCustomPerson', 'eduPerson']

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

buildData()
