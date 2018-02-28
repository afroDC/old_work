from random import *

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
    gluuPersonInum = "0000!%s.%s.%s.%s" % (getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
    return gluuPersonInum

gluuInum = "@!%s.%s.%s.%s" % (getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
totalUsers = 0

f = open('company_names.txt')
companyNames = f.readlines()
f.close()

for companyName in companyNames:
    companyName =companyName.strip()
    oInum = '@!FAB8.F546.45D4.69B5!0001!58FA.DA00' # Change this inum to your organizations inum
    ownerGroupInum = '%s!%s' % (oInum, uniqueInum())
    oCountry = getCountry()
    mailDomain = '%s.%s' % (removeSpaces(companyName), oCountry)
    oCustNumber = genCustNumber()
    employeeList= []
    numPeople = randint(1,27)
    gluuPersonInum = "0000!%s.%s.%s.%s" % (getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
    personInum = '%s!%s' % (oInum, gluuPersonInum)
    while numPeople > 0:
        numPeople = numPeople - 1
        totalUsers = totalUsers + 1
        employeeList.append(personInum)
        personFirstName = getFirstName()
        personLastName = getLastName()
        mail = "%s.%s@%s.%s" % (personFirstName, personLastName, removeSpaces(companyName), oCountry)
        print 'dn: inum=%s!%s,ou=people,o=%s,o=gluu' % (oInum, uniqueInum(), oInum)
        print 'objectclass: top'
        print 'objectclass: gluuPerson'
        print 'objectclass: gluuCustomPerson'
        print 'objectclass: eduPerson'
        print 'displayName: %s %s' % (personFirstName, personLastName)
        print 'givenName: %s' % personFirstName
        print 'iName: %s' % personFirstName
        print 'oxTrustEmail: {"operation":null,"value":"%s","display":"%s","primary":true,"reference":null,"type":"other"}' % (mail, mail)
        print 'uid: user.%i' % totalUsers
        print 'inum: %s!%s' % (oInum, uniqueInum())
        print 'mail: %s.%s@%s.%s' % (personFirstName, personLastName, removeSpaces(companyName), oCountry)
        print 'gluuStatus: active'
        print 'sn: %s' % personLastName
        print 'cn: %s' % personFirstName
        print 'userPassword: password'
        print 'oxCreationTimestamp: 20171128170625.547Z'
        print
#    print getOu('groups', oInum)
    print "dn: inum=%s,ou=groups,o=%s,o=gluu" % (ownerGroupInum, oInum)
    print "objectclass: top"
    print "objectclass: gluuGroup"
    print "gluuGroupType: gluuManagerGroup"
    print "inum: %s" % ownerGroupInum
    print "gluuStatus: active"
    print "displayName: %s Owner Group" % companyName
    print "member: inum=%s,ou=people,o=%s,o=gluu" % (employeeList[0], oInum)
    print
