# fix(RHOAIENG-61344): clean up maas-controller bundle on disable via LifecycleReconciler

## Description

Fixes [RHOAIENG-61344](https://redhat.atlassian.net/browse/RHOAIENG-61344).

### **Background**

The ODH operator deploys `maas-controller` via `AppendOperatorInstallManifests`, SSA-applying the full bundle (Deployment, CRDs, ClusterRole, ClusterRoleBinding, ServiceAccount) labeled `app.opendatahub.io/modelsasservice=true`.

When MaaS was disabled, `removeTenantIfModelsAsServiceDisabled` in the ODH operator deleted only the `Tenant` CR. The Tenant finalizer correctly cleaned up maas-api, gateway policies, and Perses dashboards — but nothing deleted the `maas-controller` bundle itself. The Deployment, CRDs, ClusterRoles, ClusterRoleBindings, and ServiceAccount remained on the cluster indefinitely.

Root cause: unlike other ODH components, MaaS has `NewCRObject` returning `(nil, nil)`, which means there is no intermediate component CR and no ownerReference chain. The ODH GC machinery has nothing to cascade-delete the
controller bundle from.

Additionally, the orphaned `maas-controller` was not passive — it actively fought cleanup by re-creating `default-tenant` and logging conflict errors on every reconcile cycle.

### **Fix (this PR)**

Adds a `LifecycleReconciler` that manages a `maas.opendatahub.io/cleanup` finalizer on the `maas-controller` Deployment. The companion ODH operator PR ([RHOAIENG-61344](https://redhat.atlassian.net/browse/RHOAIENG-61344)) deletes the Deployment when MaaS is set to `Removed`. The finalizer keeps the Deployment object alive while `LifecycleReconciler` runs
teardown in the correct order:

1. Deletes all `Tenant` CRs and waits for their finalizers to complete (cascades to maas-api, auth policies, Perses dashboards).
2. Deletes `ClusterRole`s and CRDs — while the `ClusterRoleBinding` still grants the SA the permissions to do so.
3. Deletes `ClusterRoleBinding`s last — removing them revokes all cluster-scoped permissions for this SA.

**Companion PR in `opendatahub-operator`**: replaces `removeTenantIfModelsAsServiceDisabled` with `deleteMaaSDeploymentIfDisabled`, which triggers this cleanup by deleting the Deployment when MaaS is set to `Removed`. (To be created)

<img width="833" height="492" alt="image" src="https://github.com/user-attachments/assets/13806a44-be03-4858-a2b2-2865907f295f" />


## How Has This Been Tested?

**Unit tests** (`go test ./maas-controller/pkg/controller/maas/...`):
- `TestLifecycleReconciler` covers: finalizer added on healthy Deployment,
  no-op when finalizer already present, Tenants deleted and requeued while
  terminating, ClusterRoles/ClusterRoleBindings/CRDs deleted and finalizer
  removed once all Tenants are gone.

**Live cluster**:
- Enabled MaaS via DSC, confirmed `maas-controller` Deployment running with
  finalizer present.
- Patched DSC to `managementState: Removed`. Observed in pod logs: Tenants
  deleted → ClusterRoles and CRDs deleted → ClusterRoleBindings deleted →
  finalizer removed → Deployment object fully deleted.
- Verified: `kubectl get all,clusterrole,clusterrolebinding,crd -l app.opendatahub.io/modelsasservice=true`
  returned empty after one reconcile cycle.

## Merge criteria:

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **New Features**
  * Added deployment lifecycle management with automatic resource cleanup and orderly shutdown sequence.

* **Documentation**
  * Enhanced database setup documentation with clarity on data persistence and initialization requirements.

* **Tests**
  * Added unit tests for lifecycle management functionality.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `deployment/base/maas-controller/rbac/clusterrole.yaml`
- `docs/content/install/maas-setup.md`
- `maas-controller/cmd/manager/main.go`
- `maas-controller/pkg/controller/maas/self_deployment_controller.go`
- `maas-controller/pkg/controller/maas/self_deployment_controller_test.go`
