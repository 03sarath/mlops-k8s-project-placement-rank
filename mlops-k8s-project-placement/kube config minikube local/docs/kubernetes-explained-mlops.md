# Kubernetes Config — Explained for MLOps Students

> These notes explain every section of `deployment.yaml` and `service.yaml`
> in simple language. Read this alongside the actual YAML files.

---

## What Problem Does Kubernetes Solve?

Imagine you trained an ML model and packaged it as a Docker container.
You can run it on one machine — but what happens when:

- That machine crashes?
- 1000 users hit the API at the same time?
- You release a new version of the model?

Kubernetes (K8s) handles all of this automatically. It keeps your ML model
running, scales it, and lets you update it without any downtime.

---

## File 1 — `deployment.yaml`

A **Deployment** tells Kubernetes *how* to run your ML model container —
how many copies, what image, how much memory/CPU, and how to check if it is healthy.

---

### `apiVersion` and `kind`

```yaml
apiVersion: apps/v1
kind: Deployment
```

Every Kubernetes file starts with these two lines.

- **apiVersion** tells Kubernetes which version of its API to use.
  `apps/v1` is the stable, production-ready version for Deployments.
- **kind** tells Kubernetes what type of object you are creating.
  Here we are creating a `Deployment`.

Think of it like the file header — Kubernetes reads this first to understand
what instruction you are giving it.

---

### METADATA

```yaml
metadata:
  name: recruitment-rank-app
  labels:
    app: recruitment-rank-app
    tier: ml-serving
```

- **name** is the unique identifier of this Deployment inside the cluster.
  You use this name when running commands like `kubectl get deployment recruitment-rank-app`.

- **labels** are key-value tags you attach to any Kubernetes object.
  They have no effect by themselves — but other objects (like a Service)
  use labels to find and connect to the right pods.

  Think of labels like sticky notes on a folder. The Service reads the note
  to know which pods to send traffic to.

---

### REPLICAS

```yaml
replicas: 2
```

This is one of the most important concepts in Kubernetes.

A **replica** is a running copy of your ML model container (called a Pod).

- `replicas: 1` — One copy running. If it crashes, your API goes down.
- `replicas: 2` — Two copies running. If one crashes, the other keeps serving predictions.
- `replicas: 5` — Five copies. Can handle much more traffic in parallel.

**Why does this matter for MLOps?**
In production, you never want a single copy of your model. If the pod crashes
while a user is making a request, they get an error. With 2+ replicas,
Kubernetes simply routes the next request to the healthy pod.

This is called **high availability**.

---

### REVISION HISTORY

```yaml
revisionHistoryLimit: 3
```

Every time you deploy a new version of your model, Kubernetes saves a snapshot
of the old version. This is called a **revision**.

- `revisionHistoryLimit: 3` means Kubernetes keeps the last 3 old versions.
- If your new model version breaks production, you can go back instantly with:
  ```
  kubectl rollout undo deployment/recruitment-rank-app
  ```

Think of it like version history in Google Docs — you can always go back.

We set it to `3` instead of the default `10` to avoid wasting cluster storage.

---

### SELECTOR

```yaml
selector:
  matchLabels:
    app: recruitment-rank-app
```

The Deployment needs to know which pods it is responsible for managing.
It finds them using the **selector** — it looks for pods that have the label
`app: recruitment-rank-app`.

**Important rule:** The selector must exactly match the labels you put
on the pod template below. If they don't match, Kubernetes cannot connect
the Deployment to its pods and will throw an error.

---

### POD TEMPLATE

```yaml
template:
  metadata:
    labels:
      app: recruitment-rank-app
  spec:
    containers:
      - name: placement-app
        image: 03sarath/recruitment-rank-app:v1
        imagePullPolicy: Always
```

This section describes the **pod** — the actual running unit that Kubernetes creates.

- **template.metadata.labels** — these are the labels that go ON the pod.
  They must match the `selector.matchLabels` above.

- **containers.name** — a name for the container inside the pod.
  One pod can have multiple containers, so each needs a name.

- **containers.image** — the Docker image to run. Kubernetes pulls this
  from Docker Hub (or your private registry). The `:v1` at the end is the tag —
  you change this to `:v2`, `:v3` etc. when you release a new model version.

- **imagePullPolicy: Always** — every time a pod starts, Kubernetes pulls
  a fresh copy of the image from the registry. This ensures you always run
  the latest version of the tag, not a cached old copy.

---

### RESOURCE REQUESTS & LIMITS

```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "250m"
  limits:
    memory: "256Mi"
    cpu: "500m"
```

This is where you tell Kubernetes how much compute your ML model needs.
There are two parts — **requests** and **limits** — and they do different things.

#### Requests — "What I need to start"

- `memory: "128Mi"` — the pod needs at least 128 MiB of RAM.
- `cpu: "250m"` — the pod needs at least 250 millicores (0.25 of one CPU core).

Kubernetes uses requests to **schedule** the pod. It finds a node (machine)
that has at least this much free capacity and places the pod there.

If no node has enough free resources, the pod stays in `Pending` state
until capacity is available.

#### Limits — "The maximum I am allowed"

- `memory: "256Mi"` — if the pod uses more than 256 MiB, Kubernetes **kills it**
  (you see `OOMKilled` in the logs — Out Of Memory Killed).
- `cpu: "500m"` — if the pod tries to use more than 0.5 CPU, it is **throttled**
  (slowed down, not killed).

#### Why both matter for MLOps

ML models can be unpredictable with memory — a large input batch or a memory
leak can cause one pod to consume all the RAM on a node, starving other pods.
Limits act as a safety fence. Without them, one misbehaving pod can crash
an entire node.

#### What is a millicore (m)?

1000m = 1 full CPU core.
So `250m` = a quarter of one CPU core.
This lets Kubernetes pack multiple pods on one machine efficiently.

---

### READINESS PROBE

```yaml
readinessProbe:
  httpGet:
    path: /
    port: 9696
  initialDelaySeconds: 15
  periodSeconds: 10
  failureThreshold: 3
  successThreshold: 1
```

#### What it does

A Readiness Probe is a health check that Kubernetes runs to ask:
**"Is this pod ready to receive traffic?"**

Kubernetes sends an HTTP GET request to `http://localhost:9696/` inside the pod.

- If the app returns HTTP 200 → pod is **Ready** → traffic is sent to it.
- If the app returns an error or does not respond → pod is **Not Ready** → traffic is NOT sent to it.

#### Why this is critical for ML models

When your ML model pod starts, it does not serve predictions immediately.
The container starts, Python loads, then the model weights are loaded into memory.
For a large model, this can take 15–60 seconds.

**Without a Readiness Probe:** Kubernetes marks the pod Ready as soon as the
container process starts — not when the model is actually loaded. Users get
errors because requests arrive before the model is ready.

**With a Readiness Probe:** Kubernetes waits until the `/` endpoint returns 200
before sending any traffic. Users only reach fully-loaded model instances.

#### What each field means

| Field | Value | Meaning |
|---|---|---|
| `initialDelaySeconds` | 15 | Wait 15 seconds after the container starts before the first check. Gives the model time to load. |
| `periodSeconds` | 10 | After the first check, repeat every 10 seconds. |
| `failureThreshold` | 3 | If it fails 3 times in a row → mark pod as Not Ready. |
| `successThreshold` | 1 | If it succeeds once after being Not Ready → mark it Ready again. |

---

### LIVENESS PROBE

```yaml
livenessProbe:
  httpGet:
    path: /
    port: 9696
  initialDelaySeconds: 30
  periodSeconds: 30
  failureThreshold: 3
  successThreshold: 1
```

#### What it does

A Liveness Probe asks: **"Is this pod still alive and working?"**

It uses the same HTTP GET check. But the consequence is different:

- If the check fails `failureThreshold` times → Kubernetes **kills and restarts** the container.

#### Readiness vs Liveness — the key difference

| | Readiness Probe | Liveness Probe |
|---|---|---|
| Question it asks | "Ready for traffic?" | "Still alive?" |
| What happens on failure | Pod removed from traffic rotation | Pod is killed and restarted |
| Used for | Model loading wait | Stuck/deadlocked/crashed process |

#### A simple way to remember it

- **Readiness** = "Don't send me customers yet, I'm not open."
- **Liveness** = "I've stopped responding, please restart me."

#### Why `initialDelaySeconds: 30` for liveness?

The liveness delay (30s) is longer than the readiness delay (15s) intentionally.

If liveness started at 15s and the model is still loading at that point,
Kubernetes would think the pod is dead and restart it — creating an infinite
restart loop. By giving it 30s, the model has time to load and start
returning 200 before the liveness check even begins.

---

### UPDATE STRATEGY

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

#### What it does

This controls how Kubernetes replaces old pods with new ones when you
deploy a new model version.

`RollingUpdate` means: gradually replace old pods one at a time,
rather than shutting everything down and restarting (which would cause downtime).

#### How a rolling update works step by step

Assume you have 2 pods running model v1 and you deploy model v2:

1. Kubernetes spins up 1 extra pod running v2 (`maxSurge: 1` → 3 pods total).
2. The new v2 pod goes through the Readiness Probe check.
3. Once v2 is Ready, Kubernetes terminates 1 old v1 pod → back to 2 pods.
4. Repeat until all pods are running v2.

#### What each field means

| Field | Value | Meaning |
|---|---|---|
| `maxSurge` | 1 | At most 1 extra pod above the replica count during an update. |
| `maxUnavailable` | 0 | Never take a pod down before a new one is ready. Zero downtime. |

#### Why this matters for MLOps

Model deployment in production cannot have downtime. Users making predictions
during a deployment must still get responses. With `maxUnavailable: 0`,
Kubernetes never removes an old pod until the new one is confirmed healthy.

---

## File 2 — `service.yaml`

A **Service** gives your pods a stable network address. Pods are temporary —
they get new IP addresses every time they restart. A Service sits in front
of all the pods and provides one permanent address that never changes.

---

### `apiVersion` and `kind`

```yaml
apiVersion: v1
kind: Service
```

- `apiVersion: v1` — Services belong to the core Kubernetes API (no `apps/` prefix).
- `kind: Service` — we are creating a Service object.

---

### METADATA

```yaml
metadata:
  name: recruitment-rank-app
  labels:
    app: recruitment-rank-app
```

Same concept as the Deployment metadata.

- **name** — the name of the Service. When other pods inside the cluster
  want to call this ML model API, they use this name as the hostname.
  For example: `http://recruitment-rank-app/predict`

- **labels** — tags on the Service object itself. Good practice to keep
  them consistent with the Deployment labels.

---

### SERVICE TYPE

```yaml
type: LoadBalancer
```

Kubernetes has three main Service types. Choosing the right one depends on
where your cluster is running.

| Type | What it does | Use when |
|---|---|---|
| `ClusterIP` | Internal only. No external access. | Pod-to-pod communication inside the cluster. |
| `NodePort` | Opens a port on every node. Accessible from outside via `NodeIP:Port`. | Local development, bare-metal clusters, Minikube. |
| `LoadBalancer` | Provisions a cloud load balancer with a public IP. | AWS (EKS), Google Cloud (GKE), Azure (AKS). |

We use `LoadBalancer` here. In a cloud cluster this automatically creates a
public-facing load balancer. In **Minikube** (local), the EXTERNAL-IP will
show `<pending>` — this is normal. To access it locally, run:

```
minikube service recruitment-rank-app
```

This opens a tunnel and gives you a working URL.

---

### SELECTOR

```yaml
selector:
  app: recruitment-rank-app
```

This is how the Service finds the pods to route traffic to.

The Service looks for all pods that have the label `app: recruitment-rank-app`
and sends incoming requests to whichever ones are currently **Ready**
(passing the Readiness Probe).

**This is the connection point between Service and Deployment.**

If you change the label in the Deployment but forget to update it here,
the Service will find zero pods and return connection errors to all callers.

---

### PORT MAPPING

```yaml
ports:
  - name: http
    protocol: TCP
    port: 80
    targetPort: 9696
```

This defines how traffic flows from the outside world into the pod.

```
User / Client
     |
     | calls port 80
     ▼
  Service (port: 80)
     |
     | forwards to port 9696
     ▼
  Pod (Flask/FastAPI app listening on 9696)
```

| Field | Value | Meaning |
|---|---|---|
| `name` | http | A name for this port mapping. Useful when you have multiple ports. |
| `protocol` | TCP | Standard for HTTP APIs. Use UDP only for special cases. |
| `port` | 80 | The port clients use to call the Service. Standard HTTP port. |
| `targetPort` | 9696 | The port the application inside the pod is actually listening on. Must match `containerPort` in deployment.yaml. |

#### Why different ports?

Your Flask/FastAPI app listens on port 9696 (the developer's choice).
But users and other services expect a web API on port 80 (the standard HTTP port).
The Service translates between them — users call `80`, the request arrives at `9696`.

---

## File 3 — `hpa.yaml`

A **HorizontalPodAutoscaler (HPA)** watches your Deployment and automatically
increases or decreases the number of running pods based on real-time load.

You set the minimum and maximum replica count, and Kubernetes handles the
scaling decisions for you — no manual intervention needed.

---

### `apiVersion` and `kind`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
```

- `autoscaling/v2` is the stable, modern version of the HPA API.
  It supports multiple metrics (CPU, memory, custom). Always use `v2` — the older
  `v1` only supported CPU.
- `kind: HorizontalPodAutoscaler` — this is the object type we are creating.

---

### METADATA

```yaml
metadata:
  name: recruitment-rank-hpa
  labels:
    app: recruitment-rank-app
```

- **name** — the identifier for this HPA object. You can check it with
  `kubectl get hpa recruitment-rank-hpa`.
- **labels** — kept consistent with the Deployment so it is easy to filter
  all objects belonging to this app together.

---

### TARGET DEPLOYMENT

```yaml
scaleTargetRef:
  apiVersion: apps/v1
  kind: Deployment
  name: recruitment-rank-app
```

This tells the HPA **which Deployment to control**.

- `apiVersion: apps/v1` — the API version of the target (must match Deployment).
- `kind: Deployment` — HPA can also target a StatefulSet, but Deployment is most common.
- `name: recruitment-rank-app` — must exactly match the `metadata.name` in `deployment.yaml`.

When the HPA decides to scale up or down, it edits the `replicas` field on
this Deployment automatically.

---

### REPLICA BOUNDS

```yaml
minReplicas: 2
maxReplicas: 8
```

These are the **guardrails** for the HPA — it will never go below `minReplicas`
or above `maxReplicas` regardless of the load.

| Field | Value | Meaning |
|---|---|---|
| `minReplicas` | 2 | Even at zero traffic, keep 2 pods running (high availability). |
| `maxReplicas` | 8 | Never create more than 8 pods (protects against runaway scaling and cost). |

**Why `minReplicas: 2` and not 1?**

If you set `minReplicas: 1`, during a quiet period the HPA will scale down to
a single pod. If that pod crashes, your API has zero instances until a new one
starts. `minReplicas: 2` ensures there is always a backup.

**Why cap `maxReplicas`?**

Without a maximum, a traffic spike (or a bug sending infinite requests) could
create hundreds of pods, consuming all cluster resources and causing a large
cloud bill. The maximum is your safety ceiling.

---

### SCALING METRICS

```yaml
metrics:

  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70

  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

Metrics tell the HPA **what to measure** when deciding to scale.

We have two metrics here — CPU and Memory. If **either** of them crosses
its threshold, the HPA will scale up.

#### CPU Metric

```yaml
name: cpu
target:
  type: Utilization
  averageUtilization: 70
```

- Kubernetes measures average CPU usage across all pods as a percentage
  of each pod's `resources.requests.cpu`.
- `averageUtilization: 70` means: if the average CPU across all pods
  goes above 70%, add more pods.

**Example with numbers:**

Your pod has `requests.cpu: 250m`. 70% of that = 175m.

- 1 pod using 200m of CPU → average = 200m → above 175m → HPA scales up.
- 3 pods each using 100m → average = 100m → below 175m → HPA can scale down.

#### Memory Metric

```yaml
name: memory
target:
  type: Utilization
  averageUtilization: 80
```

- Same idea as CPU but measures RAM usage as a percentage of `requests.memory`.
- `averageUtilization: 80` → scale up when average memory exceeds 80% of requested.

**Why does memory scaling matter for ML?**

ML inference can be memory-intensive. Loading large feature vectors or running
batch predictions can spike memory usage. Scaling on memory ensures pods are
not getting OOMKilled under heavy load.

#### How the HPA decides how many pods to add

The formula Kubernetes uses internally:

```
desired replicas = ceil( current replicas × (current metric / target metric) )
```

For example — CPU scenario:
- `current replicas = 2`
- `current average CPU utilization = 90%`
- `target = 70%`
- `desired = ceil( 2 × 90/70 ) = ceil(2.57) = 3`

Kubernetes will add 1 pod, bringing the total to 3.

---

### How HPA Works with the Deployment

The HPA does not create pods itself. It simply **changes the `replicas` field**
on the Deployment. The Deployment controller then creates or removes pods.

```
High Traffic
    │
    ▼
HPA checks metrics every 15 seconds
    │
    │  CPU average > 70%?
    ▼
HPA updates: deployment replicas: 2 → 3
    │
    ▼
Deployment creates 1 new pod
    │
    ▼
New pod passes Readiness Probe
    │
    ▼
Service routes traffic to all 3 pods
```

When traffic drops, the HPA scales back down — but it waits 5 minutes
before scaling down to avoid flapping (scaling up and down rapidly).

---

### Important Requirement — Metrics Server

HPA reads CPU and memory metrics from a component called the **Metrics Server**.

In Minikube, it is not enabled by default. Enable it with:

```bash
minikube addons enable metrics-server
```

Without it, the HPA will show `unknown` for metrics and will not scale.

In cloud clusters (EKS, GKE, AKS), the Metrics Server is usually pre-installed.

---

## Quick Reference — How Everything Connects

```
hpa.yaml                      deployment.yaml                service.yaml
────────                       ───────────────                ────────────
scaleTargetRef:                metadata.labels:               selector:
  name: recruitment-rank-app ──►  app: recruitment-rank-app ◄── app: recruitment-rank-app
                                                                      │
                               template.metadata.labels:              │ Service sends
                                 app: recruitment-rank-app ◄──────────┘ traffic here

                               containers.ports:              ports:
                                 containerPort: 9696    ◄──    targetPort: 9696
                                                               port: 80 (users call this)
```

Three rules to always remember:
1. `hpa.yaml scaleTargetRef.name` must match `deployment.yaml metadata.name`
2. `deployment.yaml selector.matchLabels` must match `template.metadata.labels`
3. `service.yaml selector` must match `deployment.yaml template.metadata.labels`

A typo in any of these and the system breaks silently — pods run but no traffic reaches them,
or HPA targets the wrong Deployment.

---

## Useful kubectl Commands for Practice

```bash
# Apply all three files to the cluster
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f hpa.yaml

# Check if pods are running and ready
kubectl get pods

# Check the deployment status
kubectl get deployment recruitment-rank-app

# Check the service and its external IP
kubectl get service recruitment-rank-app

# Check HPA status — shows current vs target metrics and replica count
kubectl get hpa recruitment-rank-hpa

# Watch HPA scaling decisions in real time
kubectl describe hpa recruitment-rank-hpa

# See detailed events (useful for debugging probe failures)
kubectl describe pod <pod-name>

# Watch rolling update in real time
kubectl rollout status deployment/recruitment-rank-app

# Roll back to the previous model version
kubectl rollout undo deployment/recruitment-rank-app

# Enable metrics-server in Minikube (required for HPA to work)
minikube addons enable metrics-server

# Open the service in browser (Minikube only)
minikube service recruitment-rank-app
```
