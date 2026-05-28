# feat(metrics): add Prometheus metrics instrumentation to maas-api

Add basic HTTP request metrics instrumentation (count, latency, in-flight) to the maas-api server to comply with ODH-ADR-Operator-0010 observability requirements.

Ref: [RHOAIENG-56049](https://redhat.atlassian.net/browse/RHOAIENG-56049)

## Description
- MetricsRecorder interface decouples middleware from Prometheus, enabling future OTel migration
- Gin middleware records `maas_api_http_requests_total` (counter), `maas_api_http_request_duration_seconds` (histogram), and `maas_api_http_requests_in_flight` (gauge) with method/route/status labels
- Used Prometheus naming style
- Standalone metrics server on configurable port (`METRICS_PORT`, default 9090) serves `/metrics` endpoint separate from the gateway
- `PodMonitor` and `NetworkPolicy` for RHOAI monitoring stack scraping

## How Has This Been Tested?

- [x] Deployed to a fresh OCP 4.20 cluster using kustomize mode with a custom maas-api image built from this branch. Verified that `/metrics` endpoint works by port-forwarding to port 9090 and curling it.
- [x] Confirmed that the PodMonitor and NetworkPolicy are deployed in the namespace with the right labels (monitoring.opendatahub.io/scrape: "true"). The kustomize build picks them up through the default overlay without issues.

## Merge criteria:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Exposes a Prometheus-compatible metrics endpoint on port 9090 (configurable via METRICS_PORT) and runs a dedicated metrics server
  * Adds HTTP request metrics (count, latency, in-flight) per method, route, and status; middleware records requests

* **Infrastructure**
  * Kubernetes manifests updated to expose the metrics port, include monitoring resources, and restrict network access to metrics

* **Tests**
  * Added unit and integration tests validating metrics collection and scraping
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `deployment/base/maas-api/core/deployment.yaml`
- `deployment/base/maas-api/core/service.yaml`
- `deployment/base/maas-api/default/kustomization.yaml`
- `deployment/base/maas-api/monitoring/kustomization.yaml`
- `deployment/base/maas-api/monitoring/networkpolicy.yaml`
- `deployment/base/maas-api/monitoring/podmonitor.yaml`
- `maas-api/cmd/main.go`
- `maas-api/internal/config/cluster_config.go`
- `maas-api/internal/config/config.go`
- `maas-api/internal/config/config_test.go`
- `maas-api/internal/constant/const.go`
- `maas-api/internal/metrics/middleware.go`
- `maas-api/internal/metrics/prometheus.go`
- `maas-api/internal/metrics/prometheus_test.go`
- `maas-api/internal/metrics/recorder.go`
- `maas-api/internal/metrics/recorder_test.go`
- `maas-api/internal/metrics/server.go`
- `maas-api/internal/metrics/server_test.go`
