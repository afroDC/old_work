# Gluu Kubernetes Templates

Order:

Persistence Volumes/Claims  
services  
ingress  
consul  
config-init (Run once as a Job)  
opendj  
oxauth  
oxtrust  

Launch all Persistence Volumes and Volume Claims:

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Volumes/volume-claims.yaml
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Volumes/volumes.yaml
```

In this default configuration, these are mapped to `/Data` in minikube. You can access them with `minikube ssh` and navigating to the directories. The can of course be adjusted to whatever persistence volume strategy you use.

Launch all service mappings:

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/consul-svc.yaml \
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/opendj-svc.yaml \
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/oxauth-svc.yaml \
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/oxtrust-svc.yaml
```

If you have the Nginx Ingress controller active, enable the ingress:

```
kubectl create -f https://github.com/afroDC/Dev/blob/master/Gluu/Gluubernetes/Ingress/ingress.yaml \
-f https://github.com/afroDC/Dev/blob/master/Gluu/Gluubernetes/Ingress/ingress-base.yaml \
-f https://github.com/afroDC/Dev/blob/master/Gluu/Gluubernetes/Ingress/ingress-well-known.yaml
```

Now you'll want to launch consul (until we finish our configuration wrapper for configMap):

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/StatefulSets/consul.yaml
```

Once that's up, launch `config-init` to load the configuration for Gluu Server into Consul. This should only be run once ever and you should dump the `config.json` from consul with the `dump` option:


###### Obviously change the values for `ADMIN_PW`, `EMAIL`, `DOMAIN`, `ORG_NAME`, `COUNTRY_CODE`, `STATE`, and `CITY`. Leave the rest.

```
wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Jobs/config-init.yaml
kubectl create -f ./config-init.yaml
```

Once that's completed you'll need to run OpenDJ:

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/StatefulSets/opendj.yaml
```

(Optional) Once OpenDJ has fully completed its start cycle, you can create an MMR replication topology with the following command:

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/StatefulSets/opendj-repl.yaml
```

Note that this is scalable, although not with persistence layers from what I  can assume.

Now launch oxTrust and oxAuth:

###### The `hostAliases` configuration inside of `oxauth.yaml` and `oxtrust.yam`l is optional if you have access to a DNS where the `domain` you entered before in `config-init` is resolvable from your machine. In minikube, you can set it to the `minikube ip` so you can access it through the Ingress Controller.

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Deployments/oxauth.yaml\
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Deployments/oxtrust.yaml
```

The `hostAliases` configuration inside of `oxauth.yaml` and `oxtrust.yam`l is optional if you have access to a DNS where the `domain` you entered before in `config-init` is resolvable from your machine. In minikube, you can set it to the `minikube ip` so you can access it through the Ingress Controller.

Note that these services are also scalable, with oxAuth being the workhorse of Gluu.
