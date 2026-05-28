# fix: fixing cleanup issue where not all objects were removed


### Description

This change introduces a **cluster-scoped `Config`** resource (`maas.opendatahub.io/v1alpha1`, singleton name `default`) as the **anchor for Models-as-a-Service platform lifecycle and garbage collection**. Workloads and related objects applied by the **Tenant** reconciler (server-side apply) receive **`metadata.ownerReferences`** to that `Config` where appropriate, so deleting the anchor drives cleanup of the rendered platform graph instead of relying on legacy Tenant finalizers alone.

**Highlights**

- **New CRD + default instance**: `Config` CRD and `deployment/base/maas-controller/default/config-default.yaml` for `default`.
- **Bootstrap** (`cmd/manager`): Ensures `Config/default` exists, then ensures `default-tenant` exists with a **controller** owner reference from `Config` → `Tenant` on create; patches an **additional owner reference** on existing Tenants when needed (upgrade path). Uses the **API reader** after `Config` create to avoid cache-stale reads.
- **Tenant reconcile** (`tenant_reconcile.go`): Gates platform work on a live, non-terminating `Config` with UID; surfaces **WaitingForConfigUID** when needed. **Deletion path** deletes the `Config` anchor when present, then strips the legacy finalizer. **Proactive** removal of **`maas.opendatahub.io/tenant-finalizer`** on non-deleting reconciles so upgraded clusters converge without manual patches.
- **Platform apply** (`tenantreconcile/apply.go`): `SetControllerReference` from `Config` for rendered objects; **extensible skip list** (`configOwnerRefSkips`) for resources that must not be controller-owned by `Config` (e.g. **`maas-controller` Deployment**, **`maas-parameters` ConfigMap** so it can remain aligned with operator ownership). Handles **`AlreadyOwnedError`** without failing the whole apply.
- **Lifecycle reconciler** (`self_deployment_controller.go`): Non-controller **owner reference** from `maas-controller` **Deployment** → `Config`, strips legacy cleanup finalizer on the Deployment; aligns with moving teardown off the Tenant object.
- **RBAC**: Split so **`maas-controller-role`** keeps **read-only** `configs` rules; **`maas-controller-cluster-config-role`** (+ binding) holds **mutating** `configs` rules scoped to **`resourceNames: ["default"]`** where RBAC allows (separate rule for `create`).
- **Install / scripts**: `deploy.sh` + `deployment-helpers` apply **CRDs first** and wait for **Established** before applying the full controller bundle (avoids races when not using the ODH operator’s ordering). **`cleanup-odh.sh`**: clear **finalizers** on cluster anchor CRs (`Config`, legacy `ClusterTenant`) before delete.
- **Container build**: `container.mk` builds with **repo root** context and `-f maas-controller/Dockerfile` so `COPY maas-controller/...` and embedded manifests resolve correctly.

**Coordination with Open Data Hub operator**

Validated together with **[opendatahub-io/opendatahub-operator#3535](https://github.com/opendatahub-io/opendatahub-operator/pull/3535)**:

- Operator side moves MaaS disable/cleanup to **`maas-controller` Deployment** lifecycle (instead of deleting the **Tenant** CR), provisions/watches the **cluster-scoped MaaS config** surface, and adds **RBAC for `configs`** so the operator manager can list/watch the new API.
- MaaS side avoids fighting the operator on **`maas-parameters`** by **not** setting a Config **controller** owner ref on that ConfigMap (skip list), while still applying labels and SSA.

Merge **both** PRs in a coordinated release (or ensure operator RBAC lands before / with the controller build that assumes operator watches `Config`).

### How Has This Been Tested?

- `make -C maas-controller test` (unit tests, including Tenant / lifecycle / apply paths).
- `go build` for `maas-controller` (including `cmd/manager`).
- CI: **Konflux / group-test** run referenced on the PR (see bot artifact links on the PR conversation).
- Manual / cluster (recommended before merge): install controller bundle after CRD wait; confirm `config default` exists; confirm `tenant default-tenant` owner refs; delete `config default` and confirm platform resources garbage-collect; confirm **`maas-parameters`** has no Config **controller** owner ref if the operator still owns it; disable MaaS via operator with **#3535** and confirm **`maas-controller` Deployment** deletion path and cleanup behavior.

### Risk analysis

- **Risk rating**: **4**
- **Why**: Touches **CRD install order**, **RBAC**, **bootstrap**, **GC semantics**, and **cross-repo operator** behavior. E2E smoke in CI may not cover every disable/cleanup and upgrade permutation; wrong ordering or missing operator RBAC can cause **forbidden** list/watch on `Config` or stuck anchors. Mitigations: two-phase CRD apply in `deploy.sh`, dedicated Config ClusterRole with `resourceNames`, skip list for `maas-parameters`, API reader after create, and explicit operator PR for `configs` RBAC.


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Added a cluster-scoped Config "default" to anchor controller behavior.
  * Controller startup now waits for CRDs and the Config anchor before proceeding.

* **Documentation**
  * Installation and deployment docs updated with two-phase install guidance and CRD readiness notes.

* **Refactor**
  * Simplified lifecycle and teardown behavior; removed legacy finalizer-driven cleanup flows.
  * RBAC rules reorganized to separate config permissions from other controller privileges.

* **Ops**
  * Shortened controller pod termination grace period for faster shutdowns.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

https://github.com/user-attachments/assets/a1388507-56a1-4748-9e59-79d42d59faaa



## Files involved
- `.github/hack/cleanup-odh.sh`
- `AGENTS.md`
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_configs.yaml`
- `deployment/base/maas-controller/crd/kustomization.yaml`
- `deployment/base/maas-controller/default/config-default.yaml`
- `deployment/base/maas-controller/manager/manager.yaml`
- `deployment/base/maas-controller/rbac/clusterrole.yaml`
- `deployment/base/maas-controller/rbac/clusterrole_maas_configs.yaml`
- `deployment/base/maas-controller/rbac/clusterrolebinding_maas_configs.yaml`
- `deployment/base/maas-controller/rbac/kustomization.yaml`
- `docs/content/install/maas-setup.md`
- `docs/content/migration/tier-to-subscription.md`
- `maas-controller/Makefile`
- `maas-controller/README.md`
- `maas-controller/api/maas/v1alpha1/config_types.go`
- `maas-controller/api/maas/v1alpha1/zz_generated.deepcopy.go`
- `maas-controller/cmd/manager/main.go`
- `maas-controller/container.mk`
- `maas-controller/docs/old-vs-new-flow.md`
- `maas-controller/pkg/controller/maas/self_deployment_controller.go`
- `maas-controller/pkg/controller/maas/self_deployment_controller_test.go`
- `maas-controller/pkg/controller/maas/tenant_controller.go`
- `maas-controller/pkg/controller/maas/tenant_finalize.go`
- `maas-controller/pkg/controller/maas/tenant_reconcile.go`
- `maas-controller/pkg/controller/maas/tenant_reconcile_test.go`
- `maas-controller/pkg/platform/tenantreconcile/apply.go`
- `maas-controller/pkg/platform/tenantreconcile/constants.go`
- `maas-controller/pkg/platform/tenantreconcile/pipeline.go`
- `scripts/deploy.sh`
- `scripts/deployment-helpers.sh`
- `test/e2e/scripts/auth_utils.sh`
- `test/e2e/scripts/local-deploy.sh`
