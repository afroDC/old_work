import multiprocessing as mp
import random
import string
import time
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL
from random import randint

import multiprocess_addToLDAP

# Gather the organizational inum  once so we don't waste cycles gathering it again.

oInum = multiprocess_addToLDAP.getoInum()

def mp_addToLDAP():
    for users in range(25000):
        argus = [users,oInum]
        p = mp.Process(target=multiprocess_addToLDAP.addToLDAP, args=(argus,))
        p.start()

if __name__ == '__main__':
    start = time.time()
    mp_addToLDAP()
    end = time.time()
    diff = end - start
    print("Adding 25,000 users took {} seconds".format(diff))
