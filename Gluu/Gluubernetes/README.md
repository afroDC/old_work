# Gluu Kubernetes Templates

Requirements:

Minikube or Kubernetes environment

Order:

1) Persistence Volumes/Claims  
1) Services  
1) Ingress  
1) Consul  
1) Config-init (Run once as a Job)  
1) OpenDJ  
1) oxAuth  
1) oxTrust  

## Launch Volumes

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Volumes/volume-claims.yaml
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Volumes/volumes.yaml
```

In this default configuration, these are mapped to `/Data` in minikube. You can access them with `minikube ssh` and navigating to the directories. The can of course be adjusted to whatever persistence volume strategy you use.

## Launch Services

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/consul-svc.yaml \
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/opendj-svc.yaml \
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/oxauth-svc.yaml \
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/oxtrust-svc.yaml
```

## Deploy Gluu Server Ingress

```
kubectl create -f https://github.com/afroDC/Dev/blob/master/Gluu/Gluubernetes/Ingress/ingress.yaml \
-f https://github.com/afroDC/Dev/blob/master/Gluu/Gluubernetes/Ingress/ingress-base.yaml \
-f https://github.com/afroDC/Dev/blob/master/Gluu/Gluubernetes/Ingress/ingress-well-known.yaml
```

## Launch Consul

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/StatefulSets/consul.yaml
```

## Build configuration

- Once consul is up, launch `config-init` to load the configuration for Gluu Server into Consul. This should only be run once ever and you should dump the `config.json` from consul with the `dump` option:

- Change the values for `ADMIN_PW`, `EMAIL`, `DOMAIN`, `ORG_NAME`, `COUNTRY_CODE`, `STATE`, and `CITY` leaving the rest, and launch the job.

```
wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Jobs/config-init.yaml
kubectl create -f ./config-init.yaml
```

## Prepare to Launch OpenDJ

Rendering the LDIF into OpenDJ the first time, affords you the opportunity to modify some configuration upon inception. For that reason there may be some addition steps you might want to take. If you want to scale oxAuth for load-balancing, you'll need to configure redis instances. Both of these steps defined below about redis are optional, but your scalability and redundancy will be limited.

### Standalone Redis Server (Optional)

Redis will serve the role of a shared cache for the stateless service oxAuth. This stores session data and tokens if configured in Gluu Server. Because of that, add the following environment (env) variables to the `opendj.yaml`:

```
GLUU_CACHE_TYPE 
GLUU_REDIS_URL
GLUU_REDIS_TYPE 
- name: GLUU_CACHE_TYPE 
  value: "REDIS"
- name: GLUU_REDIS_URL
  value: "redis:6379"
- name: GLUU_REDIS_TYPE 
  value: "STANDALONE"
```

And launch the redis service and a redis instance:

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Services/redis-svc.yaml \
-f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/StatefulSets/redis.yaml
```

### Cluster Redis Server (Optional)

```
https://github.com/afroDC/Dev/blob/master/Gluu/Gluubernetes/StatefulSets/redis-cluster.yaml
```

This will create 6 (Preferably use 9 across 3 nodes for redundancy) stateful redis servers that are cluster ready. You still have to connect them to eachother, so gather the IP addresses of each redis-cluster node using `kubectl get pods -o wide`, then take those ip addresses and input them here: 

```
kubectl run --tty -i --image=iromli/redis-trib create --replicas 2 <redis-cluster-0_ip>:6379 \ 
<redis-cluster-1_ip>:6379 \  
<redis-cluster-2_ip>:6379 \
<redis-cluster-3_ip>:6379 \
<redis-cluster-4_ip>:6379 \
<redis-cluster-5_ip>:6379
```

Type `yes` and press enter. This will build and enable to the cluster.

The `opendj.yaml` will also need to be modified like so:

```
- name: GLUU_REDIS_URL
  value: "<redis-cluster-0_ip>:6379,<redis-cluster-1_ip>:6379,<redis-cluster-2_ip>:6379,<redis-cluster-3_ip>:6379,<redis-cluster-4_ip>:6379,<redis-cluster-5_ip>:6379"
- name: GLUU_REDIS_TYPE 
  value: "CLUSTER"
```

## Launch OpenDJ


```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/StatefulSets/opendj.yaml
```

- (Optional) When OpenDJ has fully completed its start cycle, you can create an MMR replication topology with the following command:

```
kubectl create -f https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/StatefulSets/opendj-repl.yaml
```

Note that this is scalable, although not with persistence layers from what I can tell.

# Launch oxAuth and oxTrust

The `hostAliases` configuration inside of `oxauth.yaml` and `oxtrust.yaml` is optional if you have access to a DNS where the `domain` you entered before in `config-init` is resolvable from your machine. In minikube, you can set it to the `minikube ip` so you can access it through the Ingress Controller. Make adjustments as necessary then launch the services.

```
wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Deployments/oxauth.yaml
wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Gluubernetes/Deployments/oxtrust.yaml
kubectl create -f oxauth.yaml
-f oxtrust.yaml
```

Currently oxAuth is scalable to an undetermined amount of nodes as long as redis was configured as the cache store previously.
