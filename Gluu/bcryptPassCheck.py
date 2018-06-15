from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL
from passlib.hash import bcrypt
import base64
import hashlib


# This function is designed using the ldap3 library to get the designated users hashed password. This isn't necessary and any mechanism to gather the LDAP password is all that is needed. Change the uid to the user you want to test against below.

def getPass():
    try:
        host = 'localhost:1636'
        DN = 'cn=Directory Manager,o=gluu'
        password = 'secret'
        ldap_uri = "ldaps://{}".format(host)
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        conn.search('o=gluu', '(&(objectclass=gluuCustomPerson)(uid=Chris))',attributes=['userPassword'])
        for entry in conn.response:
            attr = entry['attributes']
            for key,val in attr.items():
                return val[0]
    except:
        print("Cannot connect to host.")

# Extracting the salt from the hashed password, so we can use it when hashing our challenge password
# A BCRYPT password is something along these lines: {BCRYPT}$2b$08$/VUckiwlBrKUc0kPgttHVOjIeUy20022lhIoeMoWTY4rznAUkG6gq
# {BCRYPT} is the name of the scheme obviously
# $2b$ means it will always use the 'safe', modern version of the algorithm
# 08 is the work factor aka number of rounds in passlib.
# The next 22 bytes of data are the random salt.
# The rest is the actual hash.
# Enhanced from the guidance of https://github.com/wclarie/openldap-bcrypt

key = getPass()
key = key[8:]
key = key.split("$")[3].strip()
key = key[0:22]

# Gather the stored user hashed password.

storedPass = getPass()

# Hash our challenge password.

challenge_hash = bcrypt.using(salt=key,rounds=8).hash('test')

# Appending BCRYPT to challenge password for matching. This isn't necessary if you strip the BCRYPT from the hashed password.

challenge_hash = "{BCRYPT}" + challenge_hash

print str(storedPass).strip() == str(challenge_hash).strip()

# I can't get this equality match to work

if storedPass.strip() is challenge_hash.strip():
    print("Stored Hashed Password:    " + storedPass)
    print("Challenge Hashed Password: " + challenge_hash)
    print("Match!")
else:
    print("Stored Hashed Password:    " + storedPass)
    print("Challenge Hashed Password: " + challenge_hash)
    print("No Match..")
