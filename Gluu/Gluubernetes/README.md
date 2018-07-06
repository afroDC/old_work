# Gluu Kubernetes Templates

Order:

Persistence Volumes/Claims
services
ingress
consul
config-init (Run as a Job)
opendj
oxauth
oxtrust

Launch all Persistence Volumes and Volume Claims:

```
kubectl create -f ./Volumes/volume-claims.yaml
kubectl create -f ./Volumes/volumes.yaml
```

In this default configuration, these are mapped to `/Data` in minikube. You can access them with `minikube ssh` and navigating to the directories. The can of course be adjusted to whatever persistence volume strategy you use.

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
kubectl create -f ./Jobs/config-init.yaml
```

Obviously change the values for `ADMIN_PW`, `EMAIL`, `DOMAIN`, `ORG_NAME`, `COUNTRY_CODE`, `STATE`, and `CITY`. Leave the rest.

Once that's completed you'll need to run OpenDJ:

```
kubectl create -f ./StatefulSets/opendj.yaml
```

(Optional) Once OpenDJ has fully completed its start cycle, you can create an MMR replication topology with the following command:

```
kubectl create -f ./StatefulSets/opendj-repl.yaml
```

Note that this is scalable, although not with persistence layers from what I  can assume.

Now launch oxTrust and oxAuth:

```
kubectl create -f ./Deployments/oxauth.yaml \
-f ./Deployments/oxtrust.yaml
```

The `hostAliases` configuration inside of `oxauth.yaml` and `oxtrust.yam`l is optional if you have access to a DNS where the `domain` you entered before in `config-init` is resolvable from your machine. In minikube, you can set it to the `minikube ip` so you can access it through the Ingress Controller.

Note that these services are also scalable, with oxAuth being the workhorse of Gluu.
