# LiteLLM Helm Chart Deployment

Deploy LiteLLM proxy gateway to Kubernetes using Helm charts.

## Prerequisites

- Kubernetes cluster (1.19+)
- Helm 3.x installed
- kubectl configured
- Access to your OpenWebUI instance

## Quick Start

### Step 1: Create Namespace

```bash
kubectl create namespace litellm
```

### Step 2: Create Secret

```bash
kubectl create secret generic litellm-secrets \
  --from-literal=openwebui-api-key=your-openwebui-api-token \
  -n litellm
```

### Step 3: Install Chart

```bash
helm install litellm-proxy ./chart -n litellm -f values.yaml
```

## Chart Structure

```
litellm-chart/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── NOTES.txt
│   ├── _helpers.tpl
│   ├── configmap.yaml
│   ├── deployment.yaml
│   ├── hpa.yaml
│   ├── ingress.yaml
│   ├── service.yaml
│   └── serviceaccount.yaml
└── README.md
```

## Chart Files

### Chart.yaml

```yaml
apiVersion: v2
name: litellm-proxy
description: LiteLLM Proxy Gateway for OpenAI-compatible APIs
type: application
version: 0.1.0
appVersion: "main-latest"
keywords:
  - litellm
  - llm
  - proxy
  - openai
home: https://github.com/BerriAI/litellm
sources:
  - https://github.com/BerriAI/litellm
maintainers:
  - name: Your Name
    email: your.email@example.com
```

### values.yaml

```yaml
# Default values for litellm-proxy
replicaCount: 1

image:
  repository: ghcr.io/berriai/litellm
  pullPolicy: IfNotPresent
  tag: "main-latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podAnnotations: {}

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
    - ALL

service:
  type: ClusterIP
  port: 4000
  targetPort: 4000
  annotations: {}

ingress:
  enabled: false
  className: "nginx"
  annotations: {}
    # kubernetes.io/tls-acme: "true"
    # cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: litellm.example.com
      paths:
        - path: /
          pathType: Prefix
  tls: []
  #  - secretName: litellm-tls
  #    hosts:
  #      - litellm.example.com

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 250m
    memory: 256Mi

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

affinity: {}

# LiteLLM specific configuration
config:
  model_list:
    - model_name: openwebui-default
      litellm_params:
        model: openai/openwebui-model
        api_base: http://myinstance.com/api
        api_key: ${OPENWEBUI_API_KEY}
    
    - model_name: openwebui-gpt4
      litellm_params:
        model: openai/gpt-4
        api_base: http://myinstance.com/api
        api_key: ${OPENWEBUI_API_KEY}
  
  litellm_settings:
    drop_params: true
    set_verbose: false
    request_timeout: 600
    telemetry: false

  general_settings:
    health_check_interval: 300

# Environment variables
env:
  - name: OPENWEBUI_API_KEY
    valueFrom:
      secretKeyRef:
        name: litellm-secrets
        key: openwebui-api-key

# Additional environment variables from ConfigMap
envFrom: []

# Liveness and readiness probes
livenessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: http
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

# Additional volumes
volumes: []

# Additional volume mounts
volumeMounts: []

# Pod disruption budget
podDisruptionBudget:
  enabled: false
  minAvailable: 1
  # maxUnavailable: 1

# Network policies
networkPolicy:
  enabled: false
  ingress: []
  egress: []
```

### templates/_helpers.tpl

```yaml
{{/*
Expand the name of the chart.
*/}}
{{- define "litellm-proxy.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "litellm-proxy.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "litellm-proxy.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "litellm-proxy.labels" -}}
helm.sh/chart: {{ include "litellm-proxy.chart" . }}
{{ include "litellm-proxy.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "litellm-proxy.selectorLabels" -}}
app.kubernetes.io/name: {{ include "litellm-proxy.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "litellm-proxy.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "litellm-proxy.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
```

### templates/configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ include "litellm-proxy.fullname" . }}
  labels:
    {{- include "litellm-proxy.labels" . | nindent 4 }}
data:
  config.yaml: |
{{- toYaml .Values.config | nindent 4 }}
```

### templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "litellm-proxy.fullname" . }}
  labels:
    {{- include "litellm-proxy.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "litellm-proxy.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "litellm-proxy.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "litellm-proxy.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
        - name: {{ .Chart.Name }}
          securityContext:
            {{- toYaml .Values.securityContext | nindent 12 }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          command:
            - "litellm"
            - "--config"
            - "/app/config.yaml"
            - "--port"
            - "4000"
          ports:
            - name: http
              containerPort: {{ .Values.service.targetPort }}
              protocol: TCP
          livenessProbe:
            {{- toYaml .Values.livenessProbe | nindent 12 }}
          readinessProbe:
            {{- toYaml .Values.readinessProbe | nindent 12 }}
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
          env:
            {{- toYaml .Values.env | nindent 12 }}
          {{- with .Values.envFrom }}
          envFrom:
            {{- toYaml . | nindent 12 }}
          {{- end }}
          volumeMounts:
            - name: config
              mountPath: /app/config.yaml
              subPath: config.yaml
              readOnly: true
            - name: tmp
              mountPath: /tmp
            {{- with .Values.volumeMounts }}
            {{- toYaml . | nindent 12 }}
            {{- end }}
      volumes:
        - name: config
          configMap:
            name: {{ include "litellm-proxy.fullname" . }}
        - name: tmp
          emptyDir: {}
        {{- with .Values.volumes }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### templates/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ include "litellm-proxy.fullname" . }}
  labels:
    {{- include "litellm-proxy.labels" . | nindent 4 }}
  {{- with .Values.service.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "litellm-proxy.selectorLabels" . | nindent 4 }}
```

### templates/ingress.yaml

```yaml
{{- if .Values.ingress.enabled -}}
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: {{ include "litellm-proxy.fullname" . }}
  labels:
    {{- include "litellm-proxy.labels" . | nindent 4 }}
  {{- with .Values.ingress.annotations }}
  annotations:
    {{- toYaml . | nindent 4 }}
  {{- end }}
spec:
  {{- if .Values.ingress.className }}
  ingressClassName: {{ .Values.ingress.className }}
  {{- end }}
  {{- if .Values.ingress.tls }}
  tls:
    {{- range .Values.ingress.tls }}
    - hosts:
        {{- range .hosts }}
        - {{ . | quote }}
        {{- end }}
      secretName: {{ .secretName }}
    {{- end }}
  {{- end }}
  rules:
    {{- range .Values.ingress.hosts }}
    - host: {{ .host | quote }}
      http:
        paths:
          {{- range .paths }}
          - path: {{ .path }}
            pathType: {{ .pathType }}
            backend:
              service:
                name: {{ include "litellm-proxy.fullname" $ }}
                port:
                  number: {{ $.Values.service.port }}
          {{- end }}
    {{- end }}
{{- end }}
```

### templates/hpa.yaml

```yaml
{{- if .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "litellm-proxy.fullname" . }}
  labels:
    {{- include "litellm-proxy.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "litellm-proxy.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}
```

### templates/NOTES.txt

```
1. Get the application URL by running these commands:
{{- if .Values.ingress.enabled }}
{{- range $host := .Values.ingress.hosts }}
  {{- range .paths }}
  http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}{{ .path }}
  {{- end }}
{{- end }}
{{- else if contains "NodePort" .Values.service.type }}
  export NODE_PORT=$(kubectl get --namespace {{ .Release.Namespace }} -o jsonpath="{.spec.ports[0].nodePort}" services {{ include "litellm-proxy.fullname" . }})
  export NODE_IP=$(kubectl get nodes --namespace {{ .Release.Namespace }} -o jsonpath="{.items[0].status.addresses[0].address}")
  echo http://$NODE_IP:$NODE_PORT
{{- else if contains "LoadBalancer" .Values.service.type }}
     NOTE: It may take a few minutes for the LoadBalancer IP to be available.
           You can watch the status of by running 'kubectl get --namespace {{ .Release.Namespace }} svc -w {{ include "litellm-proxy.fullname" . }}'
  export SERVICE_IP=$(kubectl get svc --namespace {{ .Release.Namespace }} {{ include "litellm-proxy.fullname" . }} --template "{{"{{ range (index .status.loadBalancer.ingress 0) }}{{.}}{{ end }}"}}")
  echo http://$SERVICE_IP:{{ .Values.service.port }}
{{- else if contains "ClusterIP" .Values.service.type }}
  export POD_NAME=$(kubectl get pods --namespace {{ .Release.Namespace }} -l "app.kubernetes.io/name={{ include "litellm-proxy.name" . }},app.kubernetes.io/instance={{ .Release.Name }}" -o jsonpath="{.items[0].metadata.name}")
  export CONTAINER_PORT=$(kubectl get pod --namespace {{ .Release.Namespace }} $POD_NAME -o jsonpath="{.spec.containers[0].ports[0].containerPort}")
  echo "Visit http://127.0.0.1:8080 to use your application"
  kubectl --namespace {{ .Release.Namespace }} port-forward $POD_NAME 8080:$CONTAINER_PORT
{{- end }}

2. Test the deployment:
  curl http://localhost:8080/health

3. Check logs:
  kubectl logs -n {{ .Release.Namespace }} -l app.kubernetes.io/instance={{ .Release.Name }}
```

## Deployment Examples

### Basic Installation

```bash
# Install with default values
helm install litellm-proxy ./litellm-chart -n litellm

# Install with custom values
helm install litellm-proxy ./litellm-chart -n litellm -f custom-values.yaml

# Dry run
helm install litellm-proxy ./litellm-chart -n litellm --dry-run --debug
```

### Production Values

Create `values.prod.yaml`:

```yaml
replicaCount: 3

image:
  tag: "main-stable"  # Use stable version

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: litellm.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: litellm-tls
      hosts:
        - litellm.yourdomain.com

resources:
  limits:
    cpu: 2000m
    memory: 2Gi
  requests:
    cpu: 500m
    memory: 512Mi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

podDisruptionBudget:
  enabled: true
  minAvailable: 2

config:
  litellm_settings:
    set_verbose: true
    telemetry: false
```

### Install for Production

```bash
helm install litellm-proxy ./litellm-chart \
  -n litellm \
  -f values.prod.yaml \
  --wait
```

## Managing Secrets

### Using Kubernetes Secrets

```bash
# Create secret from file
kubectl create secret generic litellm-config \
  --from-file=config.yaml=./litellm_config.yaml \
  -n litellm

# Create secret from literals
kubectl create secret generic litellm-api-keys \
  --from-literal=openai-key=sk-... \
  --from-literal=anthropic-key=sk-ant-... \
  -n litellm
```

### Using Sealed Secrets

```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

# Create sealed secret
echo -n 'your-api-key' | kubectl create secret generic litellm-secrets \
  --dry-run=client \
  --from-file=openwebui-api-key=/dev/stdin \
  -o yaml | kubeseal -o yaml > sealed-secret.yaml

# Apply sealed secret
kubectl apply -f sealed-secret.yaml -n litellm
```

## Monitoring

### Prometheus Metrics

Add to `values.yaml`:

```yaml
metrics:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

### Grafana Dashboard

Import dashboard JSON for LiteLLM metrics visualization.

## Upgrades

### Upgrade Chart

```bash
# Update values
helm upgrade litellm-proxy ./litellm-chart -n litellm -f values.yaml

# Rollback if needed
helm rollback litellm-proxy 1 -n litellm
```

### Blue-Green Deployment

```bash
# Deploy green version
helm install litellm-proxy-green ./litellm-chart \
  -n litellm \
  -f values.yaml \
  --set nameOverride=litellm-proxy-green

# Switch traffic
kubectl patch service litellm-proxy \
  -n litellm \
  -p '{"spec":{"selector":{"app.kubernetes.io/instance":"litellm-proxy-green"}}}'

# Remove blue version
helm uninstall litellm-proxy-blue -n litellm
```

## Troubleshooting

### Check Pod Status

```bash
kubectl get pods -n litellm
kubectl describe pod <pod-name> -n litellm
kubectl logs <pod-name> -n litellm
```

### Check Configuration

```bash
# View current config
kubectl get configmap litellm-proxy -n litellm -o yaml

# Edit config
kubectl edit configmap litellm-proxy -n litellm

# Restart pods after config change
kubectl rollout restart deployment litellm-proxy -n litellm
```

### Debug Mode

```bash
# Enable debug in values
helm upgrade litellm-proxy ./litellm-chart -n litellm \
  --set config.litellm_settings.set_verbose=true \
  --set config.litellm_settings.detailed_debug=true
```

## Best Practices

1. **Use Namespaces**: Isolate LiteLLM in its own namespace
2. **Resource Limits**: Always set resource requests and limits
3. **Secrets Management**: Use Kubernetes secrets or external secret managers
4. **High Availability**: Run multiple replicas with pod disruption budgets
5. **Monitoring**: Enable metrics and set up alerts
6. **Security**: Use network policies and pod security policies
7. **Backup**: Regularly backup your configuration