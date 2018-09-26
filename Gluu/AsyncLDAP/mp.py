import multiprocessing as mp
import random
import string
import time
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL
from random import randint

import multiprocess_addToLDAP

# Gather the organizational inum  once so we don't waste cycles gathering it again.

oInum = multiprocess_addToLDAP.getoInum()

def worker(tasks):
    argus = [tasks,oInum]
    multiprocess_addToLDAP.addToLDAP(argus)

def main():

    pool = mp.Pool()
    total_tasks = 50000
    tasks = range(total_tasks)

    results = pool.map_async(worker, tasks).get(5000)
    pool.close()
    pool.join()

if __name__ == '__main__':
    main()