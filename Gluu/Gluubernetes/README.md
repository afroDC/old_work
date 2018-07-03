# Gluu Kubernetes Templates

## Be aware these examples do not currently contain a persistence layer are purely for developmental purposes.

Order:

services
ingress
consul
config-init
opendj
oxauth
oxtrust

Launch all service mappings:

```
kubectl create -f ./Services/consul-svc.yaml \
-f ./Services/opendj-svc.yaml \
-f ./Services/oxauth-svc.yaml \
-f ./Services/oxtrust-svc.yaml
```

If you have the Nginx Ingress controller active, enable the ingress:

```
kubectl create -f ./Ingress/ingress.yaml \
-f ./Ingress/ingress-base.yaml \
-f ./Ingress/ingress-well-known.yaml
```

Now you'll want to launch consul (until we finish our configuration wrapper for configMap):

```
kubectl create -f ./StatefulSets/consul.yaml
```

Once that's up, launch `config-init` to load the configuration for Gluu Server into Consul:

```
kubectl run config-init --image=gluufederation/config-init:latest --attach=true --restart=Never -- generate --admin-pw secret --email 'dc@gluu.org' --domain dev.kube.org --org-name 'Gluu, Inc' --country-code US --state TX --city Austin --kv-host consul --ldap-type opendj
```

Obviously change the values for `admin-pw`, `--email`, `--domain`, `--org-name`, `--country-code`, `--state`, and `--city`. Leave the rest.

Once that's completed you'll need to run OpenDJ:

```
kubectl create -f ./StatefulSets/opendj.yaml
```

(Optional) Once OpenDJ has fully completed its start cycle, you can replicate with the following command:

```
kubectl create -f ./StatefulSets/opendj-repl.yaml
```

Note that this is scalable.

Now launch oxTrust and oxAuth:

```
kubectl create -f ./Deployments/oxauth.yaml \
-f ./Deployments/oxtrust.yaml
```

The `hostAliases` option inside of oxauth.yaml and oxtrust.yaml is optional if you have access to a DNS where the `domain` you entered before in `config-init` is resolvable from your machine.

Note that these services are also scalable.
