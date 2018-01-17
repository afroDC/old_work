#!/usr/bin/python

import os.path
import random
import shutil
import socket
import string
import time
import uuid
import json
import traceback
import subprocess
import sys
import getopt
import hashlib
import re
import glob
import base64


scim_rs_client_jks_fn = '/root/scim-rs.jks'
scim_rs_client_jks_pass = 'vETokYmuabU7'
dn_name = 'CN=oxAuth CA Certificates'
default_key_algs = 'RS256 RS384 RS512 ES256 ES384 ES512'
default_key_expiration = 365

jks_path = scim_rs_client_jks_fn
jsk_pwd = scim_rs_client_jks_pass

jre_home = '/usr/lib/jvm/java-7-openjdk-amd64/jre'
cmd_java = '%s/bin/java' % jre_home
cmd_keytool = '%s/bin/keytool' % jre_home

jetty_user_home = '/home/jetty'
jetty_user_home_lib = '%s/lib' % jetty_user_home

oxauth_keys_utils_libs = [ 'bcprov-jdk15on-*.jar', 'bcpkix-jdk15on-*.jar', 'commons-lang-*.jar',
                            'log4j-*.jar', 'commons-codec-*.jar', 'commons-cli-*.jar', 'commons-io-*.jar',
                            'jackson-core-*.jar', 'jackson-core-asl-*.jar', 'jackson-mapper-asl-*.jar', 'jackson-xc-*.jar',
                            'jettison-*.jar', 'oxauth-model-*.jar', 'oxauth-client-*.jar' ]

def findFiles(filePatterns, filesFolder):
    foundFiles = []
    try:
        for filePattern in filePatterns:
            fileFullPathPattern = "%s/%s" % (filesFolder, filePattern)
            for fileFullPath in glob.iglob(fileFullPathPattern):
                foundFiles.append(fileFullPath)
    except:
        print ("Error finding files %s in folder %s" % (":".join(filePatterns), filesFolder), True)
        print (traceback.format_exc(), True)

    return foundFiles


def generate_base64_string(lines, num_spaces):
    if not lines:
        return None

    plain_text = ''.join(lines)
    plain_b64encoded_text = plain_text.encode('base64').strip()

    if num_spaces > 0:
        plain_b64encoded_text = reindent(plain_b64encoded_text, num_spaces)

    return plain_b64encoded_text

def gen_openid_jwks_jks_keys(jks_path, jks_pwd, jks_create = True, key_expiration = None, dn_name = 'CN=oxAuth CA Certificates', key_algs = None):
    print ("Generating oxAuth OpenID Connect keys")

    if key_algs == None:
        key_algs = default_key_algs

    if key_expiration == None:
        key_expiration = default_key_expiration


    # We can remove this once KeyGenerator will do the same
    if jks_create == True:
        print ("Creating empty JKS keystore")
        # Create JKS with dummy key
        cmd = " ".join([cmd_keytool,
                        '-genkey',
                        '-alias',
                        'dummy',
                        '-keystore',
                        jks_path,
                        '-storepass',
                        jks_pwd,
                        '-keypass',
                        jks_pwd,
                        '-dname',
                        '"%s"' % dn_name])
        subprocess.call(['/bin/sh', '-c', cmd])

        # Delete dummy key from JKS
        cmd = " ".join([cmd_keytool,
                        '-delete',
                        '-alias',
                        'dummy',
                        '-keystore',
                        jks_path,
                        '-storepass',
                        jks_pwd,
                        '-keypass',
                        jks_pwd,
                        '-dname',
                        '"%s"' % dn_name])
        subprocess.call(['/bin/sh', '-c', cmd])

    oxauth_lib_files = findFiles(oxauth_keys_utils_libs, jetty_user_home_lib)

    cmd = " ".join([cmd_java,
                    "-Dlog4j.defaultInitOverride=true",
                    "-cp",
                    ":".join(oxauth_lib_files),
                    "org.xdi.oxauth.util.KeyGenerator",
                    "-keystore",
                    jks_path,
                    "-keypasswd",
                    jks_pwd,
                    "-sig_keys",
                    "%s" % key_algs,
                    "-enc_keys",
                    "%s" % key_algs,
                    "-dnname",
                    '"%s"' % dn_name,
                    "-expiration",
                    "%s" % key_expiration])
    args = ['/bin/sh', '-c', cmd]

    print ("Runnning: %s" % " ".join(args))
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, err = p.communicate()
        p.wait()
        if err:
            print (err, True)
        if output:
            return output.split(os.linesep)
    except:
        print ("Error running command : %s" % " ".join(args), True)
        print (traceback.format_exc(), True)

    return None

scim_rs_client_jwks = gen_openid_jwks_jks_keys(scim_rs_client_jks_fn, scim_rs_client_jks_pass)

generate_base64_string(scim_rs_client_jwks, 1)
