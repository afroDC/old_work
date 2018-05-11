#!/bin/bash


# Take environment variables as local variables for modifying service registry entries. Run and import all the service registry entries before running the rkt commands.

DEFAULTDIR="/opt/volumes/"

echo "For persistence of data in container environments, it's necessary to define"
echo "location to store data, which rkt will use to mount and persist information."

read -p "Enter the default directory for persistent storage: [${DEFAULTDIR}]    " DEFAULTDIR

case "$DEFAULTDIR" in
            "") DEFAULTDIR="/opt/volumes/";;
            * )   ;;
        esac

if [[ ${DEFAULTDIR: -1} = / ]]
then
    read -p "Is this the correct directory: $DEFAULTDIR?" choiceCont
        case "$choiceCont" in
                y|Y ) ;;
                n|N ) exit 1 ;;
                * )   ;;
        esac
else DEFAULTDIR=$DEFAULTDIR//
    read -p "Is this the correct directory: $DEFAULTDIR?" choiceCont
        case "$choiceCont" in
                y|Y ) ;;
                n|N ) exit 1 ;;
                * )   ;;
        esac
fi

makeDirectories ()
{
    echo "Creating all the necessary directories for data persistence.."
    mkdir -p \
        ${DEFAULTDIR}opendj/config \
        ${DEFAULTDIR}opendj/ldif \
        ${DEFAULTDIR}opendj/logs \
        ${DEFAULTDIR}opendj/db \
        ${DEFAULTDIR}opendj/flag \
        ${DEFAULTDIR}oxauth/custom/pages \
        ${DEFAULTDIR}oxauth/custom/static \
        ${DEFAULTDIR}oxauth/lib/ext \
        ${DEFAULTDIR}oxauth/logs \
        ${DEFAULTDIR}oxtrust/custom/pages \
        ${DEFAULTDIR}oxtrust/custom/static \
        ${DEFAULTDIR}oxtrust/lib/ext \
        ${DEFAULTDIR}oxtrust/logs \
        ${DEFAULTDIR}shared-shibboleth-idp \
        ${DEFAULTDIR}consul
}

launchConsul ()
{
    systemd-run --slice=machine rkt run \
    --net=host \
    --insecure-options=image \
    --dns 8.8.8.8 \
    --hostname consul \
    --set-env CONSUL_BIND_INTERFACE=lo \
    --set-env CONSUL_BIND_ADDRESS=lo \
    docker://consul \
    --exec /usr/local/bin/docker-entrypoint.sh -- agent -dev -ui -client 127.0.0.1
}

launchConfig ()
{
    echo "Please Input the following:"
    read -p "Domain name:  " DOMAIN
    read -p "Email:        " EMAIL
    read -p "Country:      " COUNTRY
    read -p "State:        " STATE
    read -p "City:         " CITY
    read -p "Organization: " ORGANIZATION
    read -p "Admin Pass:   " PASS

    case "$PASS" in
        "") 
        echo "Password cannot be empty"
        exit 1
        ;; 
        *) 
        ;;
    esac

    echo

    read -p "Continue with the above settings? [Y/n]" choiceCont

    case "$choiceCont" in
            y|Y ) echo Deploying Configuration. This may take a moment..  ;;
            n|N ) exit 1 ;;
            * )   ;;
    esac

    rkt run \
    --insecure-options=image \
    --net=host \
    --dns 8.8.8.8 \
    --dns 127.0.0.1 \
    --dns-search service.consul \
    docker://gluufederation/config-init:3.1.2_dev \
    --"exec=python" \
    -- entrypoint.py generate \
    --admin-pw "${PASS}" \
    --email "${EMAIL}" \
    --kv-host=consul.service.consul \
    --ldap-type=opendj \
    --domain "${DOMAIN}" \
    --org-name "${ORGANIZATION}" \
    --country-code "${COUNTRY}" \
    --state "${STATE}" \
    --city "${CITY}"
}

dumpConfig ()
{
    echo Saving configuration to $DEFAULTDIR/config.json

    rkt run \
    --insecure-options=image \
    --net=host \
    --dns 8.8.8.8 \
    --dns 127.0.0.1 \
    --dns-search service.consul \
    --volume volume-consul-config,kind=host,source=$DEFAULTDIR/consul/,readOnly=false \
    --mount volume=volume-consul-config,target=/opt/config-init/db/ \
    docker://gluufederation/config-init:3.1.2_dev \
    --"exec=python" \
    -- entrypoint.py dump \
    --kv-host=consul.service.consul
}

launchLdap ()
{
    systemd-run --slice=machine rkt run \
        --net=host \
        --hostname ldap \
        --insecure-options=image \
        --dns 127.0.0.1 \
        --dns 8.8.8.8 \
        --dns-search service.consul \
        --volume volume-opendj-conf,kind=host,source=$DEFAULTDIR/opendj/config,readOnly=false \
        --mount volume=volume-opendj-conf,target=/opt/opendj/config \
        --volume volume-ldif,kind=host,source=$DEFAULTDIR/opendj/ldif,readOnly=false \
        --mount volume=volume-ldif,target=/opt/opendj/ldif \
        --volume volume-opendj-logs,kind=host,source=$DEFAULTDIR/opendj/logs,readOnly=false \
        --mount volume=volume-opendj-logs,target=/opt/opendj/logs \
        --volume volume-opendj-db,kind=host,source=$DEFAULTDIR/opendj/db,readOnly=false \
        --mount volume=volume-opendj-db,target=/opt/opendj/db \
        --volume volume-flag,kind=host,source=$DEFAULTDIR/opendj/flag,readOnly=false \
        --mount volume=volume-flag,target=/flag \
        --set-env GLUU_KV_HOST=consul.service.consul \
        --set-env GLUU_LDAP_INIT=true \
        --set-env GLUU_LDAP_INIT_PORT=1636 \
        --set-env GLUU_LDAP_ADDR_INTERFACE=eth0 \
        --set-env GLUU_OXTRUST_CONFIG_GENERATION=true \
        docker://gluufederation/opendj:3.1.2_dev

    # Rebuild service entry with IP address of container

    buildServiceRegistration ldap
}

launchoxAuth () 
{
    systemd-run --slice=machine rkt run \
        --net=host \
        --insecure-options=image \
        --hostname oxauth \
        --dns 127.0.0.1 \
        --dns 8.8.8.8 \
        --dns-search service.consul \
        --volume volume-oxauth-custom-pages,kind=host,source=$DEFAULTDIR/oxauth/custom/pages,readOnly=false \
        --mount volume=volume-oxauth-custom-pages,target=/opt/gluu/jetty/oxauth/custom/pages \
        --volume volume-oxauth-custom-static,kind=host,source=$DEFAULTDIR/oxauth/custom/static,readOnly=false \
        --mount volume=volume-oxauth-custom-static,target=/opt/gluu/jetty/oxauth/custom/static \
        --volume volume-oxauth-lib-ext,kind=host,source=$DEFAULTDIR/oxauth/lib/ext,readOnly=false \
        --mount volume=volume-oxauth-lib-ext,target=/opt/gluu/jetty/oxauth/lib/ext \
        --volume volume-oxauth-logs,kind=host,source=$DEFAULTDIR/oxauth/logs,readOnly=false \
        --mount volume=volume-oxauth-logs,target=/opt/gluu/jetty/oxauth/logs \
        --set-env GLUU_KV_HOST=consul.service.consul \
        --set-env GLUU_LDAP_URL=ldap.service.consul:1636 \
        docker://gluufederation/oxauth:3.1.2_dev-8081

    # Rebuild service entry with IP address of container

    buildServiceRegistration oxauth
}

launchoxTrust () 
{
    systemd-run --slice=machine rkt run \
        --net=host \
        --insecure-options=image \
        --hostname oxtrust \
        --dns 127.0.0.1 \
        --dns 8.8.8.8 \
        --dns-search service.consul \
        --volume volume-oxtrust-custom-pages,kind=host,source=$DEFAULTDIR/oxtrust/custom/pages,readOnly=false \
        --mount volume=volume-oxtrust-custom-pages,target=/opt/gluu/jetty/identity/custom/pages \
        --volume volume-oxtrust-custom-static,kind=host,source=$DEFAULTDIR/oxtrust/custom/static,readOnly=false\
        --mount volume=volume-oxtrust-custom-static,target=/opt/gluu/jetty/identity/custom/static \
        --volume volume-oxtrust-lib-ext,kind=host,source=$DEFAULTDIR/oxtrust/lib/ext,readOnly=false \
        --mount volume=volume-oxtrust-lib-ext,target=/opt/gluu/jetty/identity/lib/ext \
        --volume volume-oxtrust-logs,kind=host,source=$DEFAULTDIR/oxtrust/logs,readOnly=false \
        --mount volume=volume-oxtrust-logs,target=/opt/gluu/jetty/identity/logs \
        --volume volume-shared-shibboleth-idp,kind=host,source=$DEFAULTDIR/shared-shibboleth-idp,readOnly=false \
        --mount volume=volume-shared-shibboleth-idp,target=/opt/shared-shibboleth-idp \
        --set-env GLUU_KV_HOST=consul.service.consul \
        --set-env GLUU_LDAP_URL=ldap.service.consul:1636 \
        --set-env GLUU_OXAUTH_BACKEND=oxauth.service.consul:8081 \
        --hosts-entry=$(ip route get 1 | awk '{print $NF;exit}')=c5.gluu.org \
        docker://gluufederation/oxtrust:3.1.2_dev-8082

        # Rebuild service entry with IP address of container

    buildServiceRegistration oxtrust
}

launchNginx ()
{
    systemd-run --slice=machine rkt run \
        --net=host \
        --insecure-options=image \
        --dns 127.0.0.1 \
        --dns 8.8.8.8 \
        --dns-search service.consul \
        --hostname nginx \
        --set-env GLUU_KV_HOST=consul.service.consul \
        --set-env GLUU_OXAUTH_BACKEND=oxauth.service.consul:8081 \
        --set-env GLUU_OXTRUST_BACKEND=oxtrust.service.consul:8082 \
        docker://gluufederation/nginx:3.1.2_dev
}

buildServiceRegistration () 
{
    
    case $1 in
        oxauth)
            key=oxauth
            port=8081
            consulAddr=localhost
            IP=$(rkt list | grep ${key} | awk '{print $11}' | cut -d'=' -f2)
            ;;
        oxtrust)
            key=oxtrust
            port=8082
            consulAddr=localhost
            IP=$(rkt list | grep ${key} | awk '{print $11}' | cut -d'=' -f2)
            ;;
        ldap)
            key=ldap
            port=1636
            consulAddr=localhost
            IP=$(rkt list | grep ${key} | awk '{print $11}' | cut -d'=' -f2)
            ;;
    esac
    cat /opt/template.json | \
    sed "s,<Name>,${key},g" | \
    sed "s,<IP>,${IP},g" | \
    sed "s,<Port>,${port},g" > /opt/${key}.json 
    curl -X PUT --data-binary @/opt/${key}.json http://$consulAddr:8500/v1/agent/service/register
}


# Create directories
echo ------------------------------------------
makeDirectories
echo ------------------------------------------
# Launch consul
echo
echo ------------------------------------------
echo "Launching consul"
echo ------------------------------------------
echo
launchConsul
sleep 2

# Build initial service entries so that NGINX doesn't fail on launch. oxTrust is dependent upon it.

buildServiceRegistration oxauth
buildServiceRegistration oxtrust
buildServiceRegistration ldap


# Launch all other containers
echo
launchConfig
echo
echo ------------------------------------------
echo Configuration loaded to consul.
echo ------------------------------------------
echo
echo ------------------------------------------
echo Saving Configuration to $DEFAULTDIR/consul/config.json...
echo ------------------------------------------
echo
dumpConfig
echo ------------------------------------------
echo Launching LDAP
echo ------------------------------------------
launchLdap
echo
echo ------------------------------------------
echo Launching NGINX
launchNginx
echo ------------------------------------------
echo
echo Launching oxauth
launchoxAuth
echo
echo ------------------------------------------
echo Launching oxTrust
echo ------------------------------------------
echo
launchoxTrust
echo
echo ------------------------------------------
echo "Gluu Server launched. Please allow some time for the processes to finish starting..."
echo "Note that 502 Bad Gateway warnings mean the service hasn't started."
echo ------------------------------------------
