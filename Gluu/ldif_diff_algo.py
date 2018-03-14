import os
import sys
import ldap
import ldif
import shelve
import hashlib

def parseLDIF(ldif_file):

    file = open(ldif_file, 'rb')

    return ldif.LDIFRecordList(file)

# Hashing to build fixed length indexes for reference.

def encode(entry):
    h = hashlib.sha1()
    h.update(str(entry))
    return h.hexdigest()

def buildIndex(ldif1):

    ldif_file = ldif1
    parser = parseLDIF(ldif_file)
    parser.parse()
    index = []
    count = 0
    for entries in parser.all_records:
        hash = encode(entries)
        index.append(hash)
        count = count + 1
    return index

def checkDiff(ldif1,ldif2):

    index = buildIndex(ldif1)

    ldif_file = ldif1
    parser = parseLDIF(ldif_file)
    parser.parse()
    for entries in parser.all_records:
        hash = encode(entries)
        if hash in index:
            continue
        else:
            print('Missing DN')
            # Here we should build a hash to value keystore and then present the user the actual dn
            print(hash)

if __name__ == '__main__':

    '''
    # For performance, it's preferable that the ldif's be loaded into shelves

    ldif1 = 'ldif1'
    ldif2 = 'ldif2'
    index = 'index'

    ldapShelve1 = shelve.open(ldif1)
    ldapShelve2 = shelve.open(ldif2)
    indexShelve = shelve.open(index)
    '''

    ldif1 = 'ldif1.ldif'
    ldif2 = 'ldif2.ldif'

    checkDiff(ldif1,ldif2)

