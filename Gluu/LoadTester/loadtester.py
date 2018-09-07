import requests
import urllib3
import time
from random import randint
from base64 import b64encode
from ldap3 import Server, Connection, MODIFY_REPLACE, MODIFY_ADD, MODIFY_DELETE, SUBTREE, ALL, BASE, LEVEL

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

login = 'https://example.gluu.org/identity/home.htm'
logout = 'https://example.gluu.org/identity/logout'

userpassword = 'secret'
userlist = []

def getoInum(host,password,DN):
    try:
        ldap_uri = "ldaps://{}".format(host)
        print('Attempting to determine organization inum from {}'.format(ldap_uri))
        server = Server(ldap_uri, use_ssl=True)
        conn = Connection(server, DN, password)
        conn.bind()
        print('Connected.')
        conn.search(search_base = 'o=gluu',
        search_filter = '(o=*)',
        search_scope = SUBTREE)
        inumRAW = conn.entries[1].entry_dn
        inum = inumRAW.replace('o=','').replace(',gluu','')
        print("oInum is: {}".format(inum))
        return inum
    except Exception as ex:
        print("Cannot connect to host.")
        print(ex)

def loadtest(username):
    # Build session states
    t0 = time.time()
    r = requests.get(login, verify=False)
    if r.status_code == 200:
        #print('Initial request successful.')
        t0 = time.time()
        # Log user in
        r = requests.get(login, auth=(username,userpassword), verify=False)
        if r.status_code == 200:
            #print('Logged in as {}'.format(username))
            t1 = time.time() - t0
            loadlog = open("activity.log", "a")
            timelog = open("times.log", "a")
            loadlog.write("{} [SUCCESS] {} {} logged in.\n".format(time.asctime( time.localtime(time.time()) ), str(r.status_code), username))
            timelog.write("{} [SUCCESS] {} Login took {} seconds.\n".format(time.asctime( time.localtime(time.time()) ), username, str(t1)))
            loadlog.close()
            timelog.close()

            t0 = time.time()
            # Log user out
            r = requests.get(logout, verify=False)
            if r.status_code == 200:
                #print('Logged out as {}'.format(username))
                t1 = time.time() - t0
                loadlog = open("activity.log", "a")
                timelog = open("times.log", "a")
                loadlog.write("{} [SUCCESS] {} {} logged out.\n".format(time.asctime( time.localtime(time.time()) ), str(r.status_code), username))
                timelog.write("{} [SUCCESS] {} Logout took {} seconds.\n".format(time.asctime( time.localtime(time.time()) ), username, str(t1)))
                loadlog.close()
                timelog.close()
            else:
                print("{} [ERROR] {} Logout failed. Please check error.log.".format(time.asctime( time.localtime(time.time()) ), str(r.status_code)))
                t1 = time.time() - t0
                loadErrorlog = open("error.log", "a")
                timelog = open("times.log", "a")
                loadErrorlog.write("{} [ERROR] {} Logout failed for user {}\n".format(time.asctime( time.localtime(time.time()) ), str(r.status_code), username))
                loadErrorlog.write("{} [FAILED] \n{}\n{}\n".format(time.asctime( time.localtime(time.time()) ), str(r.reason), str(r.text)))
                timelog.write("{} [FAILED] {} Logout failed and took {} seconds to return a response.\n".format(time.asctime( time.localtime(time.time()) ), username, str(t1)))
                loadErrorlog.close()
                timelog.close()
        else:
            print("{} [ERROR] {} Login failed. Please check error.log.".format(time.asctime( time.localtime(time.time()) ), str(r.status_code)))
            t1 = time.time() - t0
            loadErrorlog = open("activity.log", "a")
            timelog = open("times.log", "a")
            loadErrorlog.write("{} [ERROR] {} Login failed for user {}\n".format(time.asctime( time.localtime(time.time()) ), str(r.status_code), username))
            loadErrorlog.write("{} [FAILED] \n{}\n{}\n".format(time.asctime( time.localtime(time.time()) ), str(r.reason), str(r.text)))
            timelog.write("{} [FAILED] {} Login failed and took {} seconds to return a response.\n".format(time.asctime( time.localtime(time.time()) ), username, str(t1)))
            loadErrorlog.close()
            timelog.close()
    else:
        print("{} [ERROR] {} Session connection failed. Please check error.log.".format(time.asctime( time.localtime(time.time()) ), str(r.status_code)))
        t1 = time.time() - t0
        loadErrorlog = open("error.log", "a")
        timelog = open("times.log", "a")
        loadErrorlog.write("{} [ERROR] {}\n".format(time.asctime( time.localtime(time.time()) ), str(r.status_code)))
        loadErrorlog.write("{} [FAILED] \n{}\n{}\n".format(time.asctime( time.localtime(time.time()) ), str(r.reason), str(r.text)))
        timelog.write("{} [FAILED] {} Session connection failed and took {} seconds to return a response.\n".format(time.asctime( time.localtime(time.time()) ), username,  str(t1)))
        loadErrorlog.close()
        timelog.close()
