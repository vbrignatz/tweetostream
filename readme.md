# Installs

You need to install docker ([see here](https://docs.docker.com/get-docker/)).
Minikube

# MongoDB

Utilisation de `bitnami/mongodb`

Ajout du dépot :
```
helm repo add bitnami https://charts.bitnami.com/bitnami
```

Lancement :
<!-- ```
helm install mongo --set auth.rootPassword=secretpassword,auth.username=my-user,auth.password=secretpassword,auth.database=my-database mongodb-chart
``` -->
```
helm install mongo mongodb-chart
```

The hostname of mongo will be : `mongo-mongodb.default.svc.cluster.local`

To connect to your database from outside the cluster execute the following commands:
```
kubectl port-forward --namespace default svc/mongo-mongodb 27018:27017
mongosh --host 127.0.0.1 --port 27018 --authenticationDatabase admin -p secretpassword
```

La chart crée :
 - Deployment
 - Pods
 - Replicaset
 - Service
 - ConfigMap
 - Persistent Colume Claim
 - Secret
 - Persistent Volume
 - Service Account

# Zookeeper

## 1. Deploy a zookeeper client pod with configuration:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: zookeeper-client
  namespace: default
spec:
  containers:
  - name: zookeeper-client
    image: confluentinc/cp-zookeeper:6.1.0
    command:
      - sh
      - -c
      - "exec tail -f /dev/null"
```
```
kubectl apply -f zookeeper-client.yml
```

## 2. Log into the Pod

```
kubectl exec -it zookeeper-client -- /bin/bash
```

## 3. Use zookeeper-shell to connect in the zookeeper-client Pod:

```
zookeeper-shell cp-helm-charts-1655190265-cp-zookeeper:2181
```

## 4. Explore with zookeeper commands, for example:

### Gives the list of active brokers

```
ls /brokers/ids
```

### Gives the list of topics

```
ls /brokers/topics
```

### Gives more detailed information of the broker id '0'

```
get /brokers/ids/0
```

# Kafka

To connect from a client pod:

## 1. Deploy a kafka client pod with configuration:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: kafka-client
  namespace: default
spec:
  containers:
  - name: kafka-client
    image: confluentinc/cp-enterprise-kafka:6.1.0
    command:
      - sh
      - -c
      - "exec tail -f /dev/null"
```
```
kubectl apply -f kafka-client.yml
```

## 2. Log into the Pod

```
kubectl exec -it kafka-client -- /bin/bash
```

## 3. Explore with kafka commands:

### Create the topic
```
kafka-topics --zookeeper cp-helm-charts-1655190265-cp-zookeeper-headless:2181 --topic cp-helm-charts-1655190265-topic --create --partitions 1 --replication-factor 1 --if-not-exists
```

### Create a message
```
MESSAGE="`date -u`"
```

### Produce a test message to the topic
```
echo "$MESSAGE" | kafka-console-producer --broker-list cp-helm-charts-1655190265-cp-kafka-headless:9092 --topic cp-helm-charts-1655190265-topic
```

### Consume a test message from the topic
```
kafka-console-consumer --bootstrap-server cp-helm-charts-1655190265-cp-kafka-headless:9092 --topic cp-helm-charts-1655190265-topic --from-beginning --timeout-ms 2000 --max-messages 1 | grep "$MESSAGE"
```

# Program

If using minikube
```
eval $(minikube docker-env)
```

```
docker compose -f docker/docker-compose.yml build
helm install twitto app-helm
```

```
helm delete twitto
```
<!-- 
# MongoDB

## Deploy operator

```
helm install helm-charts/charts/community-operator --generate-names
```

## 1. Deploy client Pod with configuration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongo-client
  namespace: default
spec:
  containers:
  - name: mongo-client
    image: mongo
    command:
      - sh
      - -c
      - "exec tail -f /dev/null"
    resources:
      limits:
        memory: 512Mi
        cpu: "1"
      requests:
        memory: 256Mi
        cpu: "0.2"
```
```
kubectl apply -f mongo-client.yml
```

## Connect to database

```
MONGO_URI="$(mkctl get mdbc example-mongodb -o jsonpath='{.status.mongoUri}')"
kubectl exec -it mongo-client -- mongosh mongodb://my-user:secretpassword@example-mongodb-0.example-mongodb-svc.default.svc.cluster.local:27017,example-mongodb-1.example-mongodb-svc.default.svc.cluster.local:27017,example-mongodb-2.example-mongodb-svc.default.svc.cluster.local:27017
```

```
Role,RoleBinding,CustomResourceDefinition,ServiceAccount
```


```
mkctl apply -f https://raw.githubusercontent.com/mongodb/mongodb-kubernetes-operator/master/config/crd/bases/mongodbcommunity.mongodb.com_mongodbcommunity.yaml
``` -->