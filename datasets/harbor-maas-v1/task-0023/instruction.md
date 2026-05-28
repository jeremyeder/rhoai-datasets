# fix: route model access probes through gateway's internal service

## Summary
- On disconnected clusters, `FilterModelsByAccess` probes fail because they connect to the gateway via its external URL, which resolves to public ELB IPs unreachable from workload pods (blocked by `AdminNetworkPolicy` or VPC routing). Every probe hangs for 15 seconds (the `accessCheckTimeout`) and returns an empty model list.
- At startup, the maas-api now resolves the gateway's cluster-internal service address by looking up Services labeled with `gateway.networking.k8s.io/gateway-name` in the configured gateway namespace.
- A custom `DialContext` on the HTTP Transport routes all probe TCP connections to this internal address, while the original URL is preserved unchanged — keeping TLS SNI and the Host header correct so Envoy routing and Authorino ext-authz work identically.

## Details
- **Custom DialContext** — rather than rewriting probe URLs (which breaks TLS SNI matching on Envoy's filter chain), the Transport intercepts TCP connections and redirects them to the internal service. The probe URL, TLS ServerName, and Host header all remain the original external hostname.
- **Service resolution** is bounded by the configured `ACCESS_CHECK_TIMEOUT_SECONDS` to prevent stalling startup.
- **Service validation** requires the Service to have an `ownerReference` with `kind: Gateway` matching the configured gateway name, and exactly one matching candidate. This prevents a rogue Service with the same label from receiving probe traffic containing auth headers.
- HTTPS is maintained end-to-end; `InsecureSkipVerify: true` (already present) handles the cert mismatch between the external hostname and the internal service.

## Test plan
- [x] `go build ./...` and `go vet ./...` pass
- [x] Existing unit tests pass (they use httptest.Server URLs with empty `gatewayInternalHost`, so `DialContext` is not installed)
- [x] Deploy updated maas-api on a disconnected cluster and verify `GET /v1/models` returns non-empty model list
- [x] Verify Authorino ext-authz still enforces auth on probes (unauthorized users see empty list)
- [x] Re-run maas-tests Jenkins job to confirm the 22 disconnected-cluster failures are resolved

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

## Release Notes

* **New Features**
  * Added gateway internal host resolution during startup to enable access probes to route through the gateway's internal network, improving internal communication pathways.

* **Refactor**
  * Updated system initialization and underlying logic to support gateway internal host configuration and routing.

* **Tests**
  * Updated test cases to accommodate gateway internal host parameter changes.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-api/cmd/main.go`
- `maas-api/internal/config/cluster_config.go`
- `maas-api/internal/config/cluster_config_test.go`
- `maas-api/internal/handlers/models_test.go`
- `maas-api/internal/models/discovery.go`
