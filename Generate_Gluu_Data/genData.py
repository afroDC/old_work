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

def getOu(ou='', oInum=''):
    return """dn: ou=%s,o=%s,o=gluu'
objectclass: top
objectclass: organizationalUnit
ou=%s
""" % (ou, oInum, ou)

def removeSpaces(s=""):
    return "".join(s.split())

gluuInum = "@!%s.%s.%s.%s" % (getInumQuad(), getInumQuad(), getInumQuad(), getInumQuad())
totalUsers = 0

f = open('company_names.txt')
companyNames = f.readlines()
f.close()

for companyName in companyNames:
    companyName =companyName.strip()
    orgInumID = '%s.%s' % (getInumQuad(), getInumQuad())
    oInum = '%s!%s' % (gluuInum, orgInumID)
    ownerGroupInum = '%s!%s' % (oInum, getInumQuad())
    oCountry = getCountry()
    mailDomain = '%s.%s' % (removeSpaces(companyName), oCountry)
    oCustNumber = genCustNumber()
    print 'dn: o=%s,o=gluu' % oInum
    print 'objectclass: top'
    print 'objectclass: gluuOrganization'
    print 'o: %s' % oInum
    print 'displayName: %s' % companyName
    print 'gluuCustomerNumber: %s' % oCustNumber
    print 'status: active'
    print 'owner: %s' % ownerGroupInum
    print 'c: %s' % oCountry
    print
    print getOu("people", oInum)
    print
    employeeList= []
    numPeople = randint(1,27)
    while numPeople > 0:
        numPeople = numPeople - 1
        totalUsers = totalUsers + 1
        personInum = '%s!%s' % (oInum, getInumQuad())
        employeeList.append(personInum)
        personFirstName = getFirstName()
        personLastName = getLastName()
        print 'dn: inum=%s,ou=people,inum=%s,o=gluu' % (personInum, oInum)
        print 'objectclass: top'
        print 'objectclass: gluuPerson'
        print 'c: %s' % oCountry
        print 'displayName: %s %s' % (personFirstName, personLastName)
        print 'givenName: %s' % personFirstName
        print 'uid: user.%i' % totalUsers
        print 'inum: %s' % personInum
        print 'mail: %s.%s@%s.%s' % (personFirstName, personLastName, removeSpaces(companyName), oCountry)
        if len(employeeList) == 1:
            print 'memberOf: inum=%s,ou=groups,inum=%s,o=gluu' % (ownerGroupInum, oInum)
        print 'o: %s' % oInum
        print 'preferredLanguage: en'
        print 'gluuCustomerNumber: %s' % oCustNumber
        print 'gluuAPIKey: %s' % getInumQuad(40)
        print "secretQuestion: What is your mother's maiden name?"
        print 'secretAnswer: %s' % getLastName()
        print 'status: active'
        print 'sn: %s' % personLastName
        print 'timezone: UTC-06'
        print 'userpassword: password'
        print
    print getOu('groups', oInum)
    print "dn: inum=%s,ou=groups,inum=%s,o=gluu" % (ownerGroupInum, oInum)
    print "objectclass: top"
    print "objectclass: gluuGroup"
    print "inum: %s" % ownerGroupInum
    print "displayName: %s Owner Group" % companyName
    print "member: inum=%s,ou=people,inum=%s,o=gluu" % (employeeList[0], oInum)
    print
