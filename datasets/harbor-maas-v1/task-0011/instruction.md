# refactor: reconcile gateway configuration sources [RHOAIENG-62286]

Thread the resolved gateway name and namespace from cmd/manager/main.go
flags through to all downstream consumers, establishing a single source
of truth. Previously, DefaultGatewayName and DefaultGatewayNamespace
constants in constants.go duplicated the flag defaults, and both the
bootstrap (EnsureTenantGatewayDefaults) and reconcile
(applyGatewayDefaults) paths consumed these constants instead of the
resolved flag values.

Changes:
- Remove DefaultGatewayName/DefaultGatewayNamespace from constants.go
- Add gatewayName/gatewayNamespace parameters to EnsureTenantGatewayDefaults
- Add GatewayName/GatewayNamespace fields to TenantReconciler and convert
  applyGatewayDefaults to a receiver method
- Thread gateway values from main.go to ensureClusterBootstrapRunnable
  and TenantReconciler
- Remove local constant aliases from MaaSModelRefReconciler and
  externalmodel.Reconciler, inlining the fallback strings
- Update tests to use inline string values

Closes [RHOAIENG-62286](https://redhat.atlassian.net/browse/RHOAIENG-62286)

Co-Authored-By: Claude <noreply@anthropic.com>
Signed-off-by: Ryan Qin <yqin@redhat.com>

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Refactor**
  * Controllers now accept gateway configuration from startup flags so gateway defaults come from configured values rather than package-level defaults.
  * Package-level gateway default constants were removed.

* **Bug Fixes**
  * Startup now validates gateway name and namespace and exits on missing values.
  * Controllers/reporting now use configured gateway values and fail if unset instead of deriving defaults.

* **Tests**
  * Tests updated to use explicit gateway settings (maas-default-gateway in openshift-ingress).
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-controller/cmd/manager/main.go`
- `maas-controller/pkg/controller/maas/cross_namespace_test.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller_test.go`
- `maas-controller/pkg/controller/maas/tenant_controller.go`
- `maas-controller/pkg/controller/maas/tenant_reconcile.go`
- `maas-controller/pkg/controller/maas/tenant_reconcile_test.go`
- `maas-controller/pkg/platform/tenantreconcile/constants.go`
- `maas-controller/pkg/platform/tenantreconcile/kustomize.go`
- `maas-controller/pkg/reconciler/externalmodel/reconciler.go`
