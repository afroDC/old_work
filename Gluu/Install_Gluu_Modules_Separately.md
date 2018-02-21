3 servers

```
auth.example.org (1st Gluu-oxAuth/Apache2)
id.example.org (2nd Gluu-Identity/Apache2)
ldap.example.org (3rd Gluu-LDAP)
```

1) Run setup.py on my first Gluu server only installing `oxAuth`,`Apache2` and `JCE`. Use the oxAuth server as your hostname here. Mine is auth.example.org

2) After the install is finished, copy the setup.properties.last file to the other 2 servers as setup.properties.

3) Modify the setup.properties files on the second Gluu to install `Identity`, `Apache2`, `JCE`. Nothing else changes.

```
...
installOxAuth=False
...
installOxTrust=True
...
installHttpd=True
...
installLdap=False
...
```
- Run `setup.py`

4) Same as step 3 but install LDAP and JCE. Don't change anything else.

```
...
installOxAuth=False
...
installOxTrust=False
...
installHttpd=False
...
installLdap=True
...
```

- Run `setup.py`

5) Now copy the `openldap.pkcs12` file from the OpenLDAP server to both ox servers and configure the /etc/gluu/conf/ox-ldap.properties to identify ldap.example.org (My LDAP server) as the authentication server.

```
bindDN: cn=directory manager,o=gluu
bindPassword: hMaIEkcLjwk=
servers: ldap.example.org:1636  <---------------- this will say "localhost:1636"
```

6) 7) Open your Identity server to external connections. On your Identity/oxTrust server, inside Gluu, modify `/etc/default/identity`

```
JETTY_HOME=/opt/jetty
JETTY_BASE=/opt/gluu/jetty/identity
JETTY_USER=jetty
JETTY_ARGS="jetty.http.host=0.0.0.0 jetty.http.port=8082" <------- change this from localhost to 0.0.0.0
TMPDIR=/opt/jetty-9.3/temp
```

- This is where you'll need to work on your network layer for protecting port 8082 communication between the oxAuth and Identity server i.e. firewall etc.

7) edit `/etc/httpd/conf.d/https_gluu.conf` on the oxAuth server (auth.example.org) to point to the identity server (id.example.org):

```
...
        <Location /identity>
                ProxyPass http://id.example.org:8082/identity retry=5 	   <------ identity FQDN here
                ProxyPassReverse http://id.example.org:8082/identity	   <------ identity FQDN here
                Order allow,deny
                Allow from all
        </Location>
...
```

8) Open LDAP to external communication by modifying `/opt/symas/etc/openldap/symas-openldap.conf`, changing `HOST_LIST="ldaps://127.0.0.1:1636/"` to `HOST_LIST="ldaps://0.0.0.0:1636/"`

- `service solserver restart` for the changes to take effect.

- LDAP communication on 1636 is SSL, so no firewall configurations are necessary here

9) In JXPlorer I connect to ldap.example.org (My LDAP server) and change my o=gluu -> appliances -> inum= xxxx.xxxx.xxxx.xxxx!0002 -> oxIDPAuthentication entry from servers\": [\"localhost:1636\"] to servers\": [\"ldap.example.org:1636\"]

10) Copy all certs from oxAuth server to Identity server and run `keystore_Config.py` script

- Make sure to modify the `hostname` in `keystore_Config` to the hostname of your oxAuth server, we used earlier when installing Gluu on the first machine.

```
import os.path
import subprocess

cmd_keytool = '/opt/jre/bin/keytool'
hostname = "auth.example.org" <------ Change this to your oxAuth server

...
```

11) Restart identity on the identity server and restart oxauth on the oxauth server to reload settings.

auth.example.org
```
service oxauth restart
```

id.example.org
```
service identity restart
```

Now you should be able to log in to Gluu through your oxAuth FQDN (auth.example.org in my case)
