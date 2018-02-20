import os.path
import Properties
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

class Setup(object):

    def __init__(self, install_dir=None):
        self.install_dir = '.'
        self.cmd_ln = '/bin/ln'
        self.cmd_chmod = '/bin/chmod'
        self.cmd_chown = '/bin/chown'
        self.cmd_chgrp = '/bin/chgrp'
        self.cmd_mkdir = '/bin/mkdir'
        self.cmd_rpm = '/bin/rpm'
        self.cmd_dpkg = '/usr/bin/dpkg'
        self.opensslCommand = '/usr/bin/openssl'

        self.outputFolder = '%s/output' % self.install_dir

        self.jre_home = '/opt/jre'
        self.cmd_java = '%s/bin/java' % self.jre_home
        self.cmd_keytool = '%s/bin/keytool' % self.jre_home
        self.cmd_jar = '%s/bin/jar' % self.jre_home

        self.gluuOptFolder = '/opt/gluu'
        self.jetty_home = '/opt/jetty'

        self.jetty_base = '%s/jetty' % self.gluuOptFolder

        self.jetty_app_configuration = {
            'oxauth' : {'name' : 'oxauth',
                        'jetty' : {'modules' : 'deploy,http,logging,jsp,servlets,ext,http-forwarded,websocket'},
                        'memory' : {'ratio' : 0.3, "jvm_heap_ration" : 0.7, "max_allowed_mb" : 4096},
                        'installed' : False
                        },
            'identity' : {'name' : 'identity',
                            'jetty' : {'modules' : 'deploy,http,logging,jsp,ext,http-forwarded,websocket'},
                            'memory' : {'ratio' : 0.2, "jvm_heap_ration" : 0.7, "max_allowed_mb" : 2048},
                            'installed' : False
                            },
            'idp' : {'name' : 'idp',
                        'jetty' : {'modules' : 'deploy,http,logging,jsp,http-forwarded'},
                        'memory' : {'ratio' : 0.2, "jvm_heap_ration" : 0.7, "max_allowed_mb" : 1024},
                        'installed' : False
                        },
            'asimba' : {'name' : 'asimba',
                        'jetty' : {'modules' : 'deploy,http,logging,jsp,http-forwarded'},
                        'memory' : {'ratio' : 0.1, "jvm_heap_ration" : 0.7, "max_allowed_mb" : 1024},
                        'installed' : False
                        },
            'oxauth-rp' : {'name' : 'oxauth-rp',
                            'jetty' : {'modules' : 'deploy,http,logging,jsp,http-forwarded,websocket'},
                            'memory' : {'ratio' : 0.1, "jvm_heap_ration" : 0.7, "max_allowed_mb" : 512},
                            'installed' : False
                            },
            'passport' : {'name' : 'passport',
                            'node' : {},
                            'memory' : {'ratio' : 0.1, "max_allowed_mb" : 1024},
                            'installed' : False
                            }
        }
        self.os_types = ['centos', 'redhat', 'fedora', 'ubuntu', 'debian']
        self.os_type = None
        self.distFolder = '/opt/dist'
        self.distGluuFolder = '%s/gluu' % self.distFolder

        self.log = '%s/setup.log' % self.install_dir
        self.logError = '%s/setup_error.log' % self.install_dir
        self.oxPhotosFolder = "/var/ox/photos"
        self.oxTrustRemovedFolder = "/var/ox/identity/removed"
        self.oxTrustCacheRefreshFolder = "/var/ox/identity/cr-snapshots"

        self.run([self.cmd_mkdir, '-m', '775', '-p', self.oxPhotosFolder])
        self.run([self.cmd_mkdir, '-m', '775', '-p', self.oxTrustRemovedFolder])
        self.run([self.cmd_mkdir, '-m', '775', '-p', self.oxTrustCacheRefreshFolder])

        self.run([self.cmd_chown, '-R', 'root:gluu', self.oxPhotosFolder])
        self.run([self.cmd_chown, '-R', 'root:gluu', self.oxTrustRemovedFolder])
        self.run([self.cmd_chown, '-R', 'root:gluu', self.oxTrustCacheRefreshFolder])

        self.installOxTrust = True

    def install_oxtrust(self):

        self.logIt("Copying oxauth.war into jetty webapps folder...")

        jettyServiceName = 'identity'
        self.installJettyService(self.jetty_app_configuration[jettyServiceName], True)

        jettyServiceWebapps = '%s/%s/webapps' % (self.jetty_base, jettyServiceName)
        self.copyFile('%s/identity.war' % self.distGluuFolder, jettyServiceWebapps)

    def installJettyService(self, serviceConfiguration, supportCustomizations=False):
        serviceName = serviceConfiguration['name']
        self.logIt("Installing jetty service %s..." % serviceName)
        jettyServiceBase = '%s/%s' % (self.jetty_base, serviceName)
        jettyModules = serviceConfiguration['jetty']['modules']
        jettyModulesList = jettyModules.split(',')

        self.logIt("Preparing %s service base folders" % serviceName)
        self.run([self.cmd_mkdir, '-p', jettyServiceBase])

        # Create ./ext/lib folder for custom libraries only if installed Jetty "ext" module
        if "ext" in jettyModulesList:
            self.run([self.cmd_mkdir, '-p', "%s/lib/ext" % jettyServiceBase])

        # Create ./custom/pages and ./custom/static folders for custom pages and static resources, only if application supports them
        if supportCustomizations:
            if not os.path.exists("%s/custom" % jettyServiceBase):
                self.run([self.cmd_mkdir, '-p', "%s/custom" % jettyServiceBase])
            self.run([self.cmd_mkdir, '-p', "%s/custom/pages" % jettyServiceBase])
            self.run([self.cmd_mkdir, '-p', "%s/custom/static" % jettyServiceBase])
            self.run([self.cmd_mkdir, '-p', "%s/custom/libs" % jettyServiceBase])

        self.logIt("Preparing %s service base configuration" % serviceName)
        jettyEnv = os.environ.copy()
        jettyEnv['PATH'] = '%s/bin:' % self.jre_home + jettyEnv['PATH']

        self.run([self.cmd_java, '-jar', '%s/start.jar' % self.jetty_home, 'jetty.home=%s' % self.jetty_home, 'jetty.base=%s' % jettyServiceBase, '--add-to-start=%s' % jettyModules], None, jettyEnv)
        self.run([self.cmd_chown, '-R', 'jetty:jetty', jettyServiceBase])

        try:
            self.renderTemplateInOut(serviceName, '%s/jetty' % self.templateFolder, '%s/jetty' % self.outputFolder)
        except:
            self.logIt("Error rendering service '%s' defaults" % serviceName, True)
            self.logIt(traceback.format_exc(), True)

        jettyServiceConfiguration = '%s/jetty/%s' % (self.outputFolder, serviceName)
        self.copyFile(jettyServiceConfiguration, "/etc/default")
        self.run([self.cmd_chown, 'root:root', "/etc/default/%s" % serviceName])

        try:
            web_resources = '%s_web_resources.xml' % serviceName
            if os.path.exists('%s/jetty/%s' % (self.templateFolder, web_resources)):
                self.renderTemplateInOut(web_resources, '%s/jetty' % self.templateFolder, '%s/jetty' % self.outputFolder)
                self.copyFile('%s/jetty/%s' % (self.outputFolder, web_resources), self.jetty_base+"/"+serviceName+"/webapps")
        except:
            self.logIt("Error rendering service '%s' web_resources.xml" % serviceName, True)
            self.logIt(traceback.format_exc(), True)

        self.copyFile('%s/bin/jetty.sh' % self.jetty_home, '/etc/init.d/%s' % serviceName)
        source_string = '# Provides:          jetty'
        target_string = '# Provides:          %s' % serviceName
        self.run(['sed', '-i', 's/^%s/%s/' % (source_string, target_string), '/etc/init.d/%s' % serviceName])

        # Enable service autoload on Gluu-Server startup
        if self.os_type in ['centos', 'fedora', 'redhat']:
            if self.os_initdaemon == 'systemd':
                self.run(["/usr/bin/systemctl", 'enable', serviceName])
            else:
                self.run(["/sbin/chkconfig", serviceName, "on"])
        elif self.os_type in ['ubuntu', 'debian']:
            self.run(["/usr/sbin/update-rc.d", serviceName, 'defaults', '60', '20'])

        serviceConfiguration['installed'] = True

    def renderTemplateInOut(self, filePath, templateFolder, outputFolder):
        self.logIt("Rendering template %s" % filePath)
        fn = os.path.split(filePath)[-1]
        f = open(os.path.join(templateFolder, fn))
        template_text = f.read()
        f.close()

        # Create output folder if needed
        if not os.path.exists(outputFolder):
            os.makedirs(outputFolder)

        newFn = open(os.path.join(outputFolder, fn), 'w+')
        newFn.write(self.fomatWithDict(template_text, self.merge_dicts(self.__dict__, self.templateRenderingDict)))
        newFn.close()

    def install_gluu_components(self):
        self.install_oxtrust()
        
    def run(self, args, cwd=None, env=None, useWait=False, shell=False):
        self.logIt('Running: %s' % ' '.join(args))
        try:
            p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env, shell=shell)
            if useWait:
                code = p.wait()
                self.logIt('Run: %s with result code: %d' % (' '.join(args), code) )
            else:
                output, err = p.communicate()
                if output:
                    self.logIt(output)
                if err:
                    self.logIt(err, True)
        except:
            self.logIt("Error running command : %s" % " ".join(args), True)
            self.logIt(traceback.format_exc(), True)

    def logIt(self, msg, errorLog=False):
        if errorLog:
            f = open(self.logError, 'a')
            f.write('%s %s\n' % (time.strftime('%X %x'), msg))
            f.close()
        f = open(self.log, 'a')
        f.write('%s %s\n' % (time.strftime('%X %x'), msg))
        f.close()

    def detect_os_type(self):
        # TODO: Change this to support more distros. For example according to
        # http://unix.stackexchange.com/questions/6345/how-can-i-get-distribution-name-and-version-number-in-a-simple-shell-script
        distro_info = self.readFile('/etc/redhat-release', False)
        if distro_info == None:
            distro_info = self.readFile('/etc/os-release')

        if 'CentOS' in distro_info:
            return self.os_types[0]
        elif 'Red Hat' in distro_info:
            return self.os_types[1]
        elif 'Ubuntu' in distro_info:
            return self.os_types[3]
        elif 'Debian' in distro_info:
            return self.os_types[4]

        else:
            return self.choose_from_list(self.os_types, "Operating System")

    def readFile(self, inFilePath, logError=True):
        inFilePathText = None

        try:
            f = open(inFilePath)
            inFilePathText = f.read()
            f.close
        except:
            if logError:
                self.logIt("Error reading %s" % inFilePathText, True)
                self.logIt(traceback.format_exc(), True)

        return inFilePathText

    def writeFile(self, outFilePath, text):
        inFilePathText = None

        try:
            f = open(outFilePath, 'w')
            f.write(text)
            f.close()
        except:
            self.logIt("Error writing %s" % inFilePathText, True)
            self.logIt(traceback.format_exc(), True)

        return inFilePathText
        
    def detect_initd(self):
        return open(os.path.join('/proc/1/status'), 'r').read().split()[1]

    def install_gluu_components(self):
        if self.installLdap:
            progress_bar(25, "Installing Gluu components: LDAP")
            self.install_ldap_server()

        if self.installHttpd:
            progress_bar(25, "Installing Gluu components: HTTPD")
            self.configure_httpd()

        if self.installOxAuth:
            progress_bar(25, "Installing Gluu components: OxAuth")
            self.install_oxauth()

        if self.installOxTrust:
            progress_bar(25, "Installing Gluu components: oxtruest")
            self.install_oxtrust()

        if self.installSaml:
            progress_bar(25, "Installing Gluu components: saml")
            self.install_saml()

        if self.installAsimba:
            progress_bar(25, "Installing Gluu components: Asimba")
            self.install_asimba()

        if self.installOxAuthRP:
            progress_bar(25, "Installing Gluu components: OxAuthRP")
            self.install_oxauth_rp()

        if self.installPassport:
            progress_bar(25, "Installing Gluu components: Passport")
            self.install_passport()

    def promptForProperties(self):

        promptForMITLicense = self.getPrompt("Do you acknowledge that use of the Gluu Server is under the MIT license?","N|y")[0].lower()
        if promptForMITLicense != 'y':
            sys.exit(0)
        
        # IP address needed only for Apache2 and hosts file update
        if self.installHttpd:
            self.ip = self.get_ip()

        detectedHostname = None
        try:
            detectedHostname = socket.gethostbyaddr(socket.gethostname())[0]
        except:
            try:
                detectedHostname = os.popen("/bin/hostname").read().strip()
            except:
                self.logIt("No detected hostname", True)
                self.logIt(traceback.format_exc(), True)
        if detectedHostname:
            self.hostname = self.getPrompt("Enter hostname", detectedHostname)
        else:
            self.hostname = self.getPrompt("Enter hostname")

        # Get city and state|province code
        self.city = self.getPrompt("Enter your city or locality")
        self.state = self.getPrompt("Enter your state or province two letter code")

        # Get the Country Code
        long_enough = False
        while not long_enough:
            countryCode = self.getPrompt("Enter two letter Country Code")
            if len(countryCode) != 2:
                print "Country code must be two characters"
            else:
                self.countryCode = countryCode
                long_enough = True

        self.orgName = self.getPrompt("Enter Organization Name")
        self.admin_email = self.getPrompt('Enter email address for support at your organization')
        self.application_max_ram = self.getPrompt("Enter maximum RAM for applications in MB", '3072')
        randomPW = self.getPW()
        self.ldapPass = self.getPrompt("Optional: enter password for oxTrust and LDAP superuser", randomPW)

        promptForOxAuth = self.getPrompt("Install oxAuth OAuth2 Authorization Server?", "Yes")[0].lower()
        if promptForOxAuth == 'y':
            self.installOxAuth = True
        else:
            self.installOxAuth = False

        promptForOxTrust = self.getPrompt("Install oxTrust Admin UI?", "Yes")[0].lower()
        if promptForOxTrust == 'y':
            self.installOxTrust = True
        else:
            self.installOxTrust = False

        promptForLDAP = self.getPrompt("Install LDAP Server?", "Yes")[0].lower()
        if promptForLDAP == 'y':
            self.installLdap = True
            option = None
            while (option != 1) and (option != 2):
                try:
                    option = int(self.getPrompt("Install (1) Gluu OpenDJ (2) OpenLDAP Gluu Edition [1|2]", "1"))
                except ValueError:
                    option = None
                if (option != 1) and (option != 2):
                    print "You did not enter the correct option. Enter either 1 or 2."

            if option == 1:
                self.ldap_type = 'opendj'
            elif option == 2:
                self.ldap_type = 'openldap'
        else:
            self.installLdap = False

        promptForHTTPD = self.getPrompt("Install Apache HTTPD Server", "Yes")[0].lower()
        if promptForHTTPD == 'y':
            self.installHttpd = True
        else:
            self.installHttpd = False

        promptForShibIDP = self.getPrompt("Install Shibboleth SAML IDP?", "No")[0].lower()
        if promptForShibIDP == 'y':
            self.shibboleth_version = 'v3'
            self.installSaml = True
        else:
            self.installSaml = False

        promptForAsimba = self.getPrompt("Install Asimba SAML Proxy?", "No")[0].lower()
        if promptForAsimba == 'y':
            self.installAsimba = True
        else:
            self.installAsimba = False

        promptForOxAuthRP = self.getPrompt("Install oxAuth RP?", "No")[0].lower()
        if promptForOxAuthRP == 'y':
            self.installOxAuthRP = True
        else:
            self.installOxAuthRP = False

        promptForPassport = self.getPrompt("Install Passport?", "No")[0].lower()
        if promptForPassport == 'y':
            self.installPassport = True
        else:
            self.installPassport = False

            #if self.allowDeprecatedApplications:
            # Empty deprecated option

        promptForJCE = self.getPrompt("Install JCE 1.8?", "Yes")[0].lower()
        if promptForJCE == 'y':
            promptForJCELicense = self.getPrompt("You must accept the Oracle Binary Code License Agreement for the Java SE Platform Products to download this software. Accept License Agreement?", "Yes")[0].lower()
            if promptForJCELicense == 'y':
                self.installJce = True
            else:
                self.installJce = False
        else:
            self.installJce = False
    def copyFile(self, inFile, destFolder):
        try:
            shutil.copy(inFile, destFolder)
            self.logIt("Copied %s to %s" % (inFile, destFolder))
        except:
            self.logIt("Error copying %s to %s" % (inFile, destFolder), True)
            self.logIt(traceback.format_exc(), True)

if __name__ == '__main__':
    installox = Setup()
    installox.install_oxtrust()
'''
    setupOptions = {
        'install_dir': '.',
        'setup_properties': None,
        'noPrompt': False,
        'downloadWars': False,
        'installOxAuth': True,
        'installOxTrust': True,
        'installLDAP': True,
        'installHTTPD': True,
        'installSaml': False,
        'installAsimba': False,
        'installOxAuthRP': False,
        'installPassport': False,
        'allowPreReleasedApplications': False,
        'allowDeprecatedApplications': False,
        'installJce': False
    }
    if len(sys.argv) > 1:
        setupOptions = getOpts(sys.argv[1:], setupOptions)

    installObject = Setup(setupOptions['install_dir'])
    installObject.downloadWars = setupOptions['downloadWars']

    installObject.installOxTrust = setupOptions['installOxTrust']
    installObject.os_type = installObject.detect_os_type()
    installObject.os_initdaemon = installObject.detect_initd()
'''
