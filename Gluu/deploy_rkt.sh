#!/bin/bash


# Take environment variables as local variables for modifying service registry entries. Run and import all the service registry entries before running the rkt commands.

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
    rkt run \
    --insecure-options=image \
    --net=host \
    --dns 8.8.8.8 \
    --dns 127.0.0.1 \
    --dns-search service.consul \
    docker://gluufederation/config-init:3.1.2_dev \
    --"exec=python" \
    -- entrypoint.py generate \
    --admin-pw secret \
    --email dc@gluu.org \
    --kv-host=consul.service.consul \
    --ldap-type=opendj \
    --domain c5.gluu.org \
    --org-name 'Gluu Inc.' \
    --country-code US \
    --state TX \
    --city Austin
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

# Launch consul

launchConsul
sleep 2

# Build initial service entries so that NGINX doesn't fail on launch. oxTrust is dependent upon it.

buildServiceRegistration oxauth
buildServiceRegistration oxtrust
buildServiceRegistration ldap


# Launch all other containers

echo Deploying Configuration. This may take a moment..

launchConfig
launchLdap
launchNginx
launchoxAuth
launchoxTrust
