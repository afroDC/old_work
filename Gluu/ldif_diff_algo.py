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

    ldif_file = ldif2
    parser = parseLDIF(ldif_file)
    parser.parse()

    count = 0

    for entries in parser.all_records:
        hash = encode(entries)

        # Store count to compare with index to determine if amount of entries match. 

        count = count + 1
        if hash in index:
            continue
        else:
            print('Missing DN')
            # Here we should build a hash to value keystore and then present the user the actual dn
            print(hash)

    print count  

    if count == len(index):

        print('Equal Entries')
    
    # Simple logic to display the difference

    else:
        if count > len(index):
            print('There seem to be more entries in the new ldif. See below: ')
            print(count - len(index))
        elif len(index) > count:
            print('The new ldif is missing ' + str((len(index) - count)) + ' entries.')
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

    #ldif1 = 'people1.ldif'
    #ldif2 = 'people2.ldif'
    ldif1 = sys.argv[1]
    ldif2 = sys.argv[2]

    checkDiff(ldif1,ldif2)

