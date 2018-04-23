#!/bin/sh

KV=c5.gluu.org

######## Install OpenDJ ########

OPENDJ_VERSION=3.0.0.gluu-SNAPSHOT
OPENDJ_DOWNLOAD_URL=http://ox.gluu.org/maven/org/forgerock/opendj/opendj-server-legacy/${OPENDJ_VERSION}/opendj-server-legacy-${OPENDJ_VERSION}.zip

wget -q "$OPENDJ_DOWNLOAD_URL" -P /tmp \
    && mkdir -p /opt \
    && unzip -qq /tmp/opendj-server-legacy-${OPENDJ_VERSION}.zip -d /opt \
    && rm -f /tmp/opendj-server-legacy-${OPENDJ_VERSION}.zip

cp requirements.txt /tmp/requirements.txt
pip install -U pip \
    && pip install -r /tmp/requirements.txt --no-cache-dir

mkdir -p /etc/certs
cp schemas/96-eduperson.ldif /opt/opendj/template/config/schema/
cp schemas/101-ox.ldif /opt/opendj/template/config/schema/
cp schemas/77-customAttributes.ldif /opt/opendj/template/config/schema/
cp -r templates/* /opt/templates
cp scripts/* /opt/scripts

mkdir -p /opt/opendj/locks

GLUU_KV_HOST=$KV GLUU_LDAP_INIT=true python ./scripts/opendj.py

######## Install Jetty and oxServices ########

distFolder=/opt/dist
distAppFolder=$distFolder/app
gluuOptFolder=/opt/gluu
jre_home=/opt/jre

jetty_version=9.3.15.v20161220
jetty_dist=/opt/jetty-9.3
jettyTemp=$jetty_dist/temp
jetty_home=/opt/jetty
jettyArchive=jetty-distribution-$jetty_version.tar.gz
jetty_base=$gluuOptFolder/jetty

mkdir -p $jettyTemp
chown -R jetty:jetty $jettyTemp

jettyDestinationPath=$jetty_dist/jetty-distribution-$jetty_version

tar -xzf $distAppFolder/$jettyArchive -C $jetty_dist --no-xattrs --no-same-owner --no-same-permissions

ln -sf $jettyDestinationPath $jetty_home
chmod -R 755 $jettyDestinationPath/bin/

chown -R jetty:jetty $jettyDestinationPath
chown -h jetty:jetty $jetty_home

mkdir -p $jetty_base
chown -R jetty:jetty $jetty_base

######## Install oxTrust ########

jettyServiceBase=$jetty_base/identity

mkdir -p $jettyServiceBase

mkdir -p $jettyServiceBase/lib/ext/
mkdir -p $jettyServiceBase/custom/
mkdir -p $jettyServiceBase/custom/pages
mkdir -p $jettyServiceBase/custom/static
mkdir -p $jettyServiceBase/custom/libs

java -jar $jetty_home/start.jar jetty.home=$jetty_home jetty.base=$jettyServiceBase --add-to-start='deploy,http,logging,jsp,ext,http-forwarded,websocket'

chown -R jetty:jetty $jettyServiceBase

cp $distFolder/gluu/identity.war $jettyServiceBase/webapps

# Copy web_resources.xml to $jetty_base/identity/webapps

GLUU_KV_HOST=$KV python ./scripts/oxtrust.py
./scripts/upload_cert.sh

######## Install oxAuth ########

jettyServiceBase=$jetty_base/oxauth

mkdir -p $jettyServiceBase

mkdir -p $jettyServiceBase/lib/ext/
mkdir -p $jettyServiceBase/custom/
mkdir -p $jettyServiceBase/custom/pages
mkdir -p $jettyServiceBase/custom/static
mkdir -p $jettyServiceBase/custom/libs

java -jar $jetty_home/start.jar jetty.home=$jetty_home jetty.base=$jettyServiceBase --add-to-start='deploy,http,logging,jsp,ext,http-forwarded,websocket'

chown -R jetty:jetty $jettyServiceBase

cp $distFolder/gluu/oxauth.war $jettyServiceBase/webapps

GLUU_KV_HOST=$KV python ./scripts/oxauth.py
