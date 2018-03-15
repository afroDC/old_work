import os
import sys
import ldap
import ldif
import shelve
import hashlib
import time

def parseLDIF(ldif_file):

    file = open(ldif_file, 'rb')

    return ldif.LDIFRecordList(file)

    file.close()

# Hashing to build fixed length indexes for the index table.

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
        # Hash only the dn's as there will be data entry differences in version upgrades
        # but the dn's will be the same.

        hash = encode(entries[0])
        index.append(hash)
        count = count + 1
    return index

def checkDiff(ldif1,ldif2):

    index = buildIndex(ldif1)

    ldif_file = ldif2
    parser = parseLDIF(ldif_file)
    parser.parse()

    count = 0

    new_index = []

    for entries in parser.all_records:

        hash = encode(entries[0])
        new_index.append(hash)

        # Store count to compare with index to determine if amount of entries match. 
        count = count + 1

        if hash in index:
            continue
        else:
            print('Missing DN')
            # Here we should build a hash to value keystore and then present the user the actual dn

    if count == len(index):

        print('Equal Entries')

    
    # Simple logic to display the difference

    else:
        if count > len(index):
            print('There seem to be more entries in the new ldif. See below: ')
            print(count - len(index))
        elif len(index) > count:
            print('The new ldif is missing ' + str((len(index) - count)) + ' entries.')
            print('They are as follows:')

            c = 0

            for i in range(len(index)):
                try:
                    if new_index[i] in index:
                        continue
                except:
                    print(index[i])
                    c = c + 1
            print c

if __name__ == '__main__':

    '''
    # For performance, it's preferable that the initial ldif's be loaded into shelves

    ldif1 = sys.argv[1]
    ldif2 = sys.argv[2]
    index = 'index'

    ldapShelve1 = shelve.open(ldif1)
    ldapShelve2 = shelve.open(ldif2)
    indexShelve = shelve.open(index)
    '''
    
    checkDiff(ldif1,ldif2)

    # Test performance
    '''
    ldif1 = sys.argv[1]
    ldif2 = sys.argv[2]

    t0 = time.time()
    checkDiff(ldif1,ldif2)
    t1 = time.time()

    total = t1-t0
    print(total)
    '''

