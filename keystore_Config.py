import os.path
import subprocess

cmd_keytool = '/opt/jre/bin/keytool'
hostname = "c5.gluu.org"

def import_key(suffix) :
    defaultTrustStorePW = 'changeit'
    defaultTrustStoreFN = '/opt/jre/jre/lib/security/cacerts'
    certFolder = '/etc/certs'
    public_certificate = '%s/%s.crt' % (certFolder, suffix)
    subprocess.call([cmd_keytool, "-import", "-trustcacerts", "-alias", "%s_%s" % (hostname, suffix), \
                  "-file", public_certificate, "-keystore", defaultTrustStoreFN, \
                  "-storepass", defaultTrustStorePW, "-noprompt"])

def delete_key(suffix) :
    defaultTrustStorePW = 'changeit'
    defaultTrustStoreFN = '/opt/jre/jre/lib/security/cacerts'
    if os.path.isfile("/etc/certs/%s.crt" % (suffix)):
        subprocess.call([cmd_keytool, "-delete", "-alias", "%s_%s" % (hostname, suffix), \
                      "-keystore", defaultTrustStoreFN, \
                      "-storepass", defaultTrustStorePW,])


def configure_server():
    delete_key('httpd')
    delete_key('shibIDP')
    delete_key('idp-encryption')
    delete_key('idp-signing')
    delete_key('asimba')
    delete_key('openldap')
    import_key('httpd')
    import_key('shibIDP')
    import_key('idp-encryption')
    import_key('idp-signing')
    import_key('asimba')
    import_key('openldap')

configure_server()
