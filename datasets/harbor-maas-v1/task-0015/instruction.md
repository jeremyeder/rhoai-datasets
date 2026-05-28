# chore: post-split RBAC audit, nil CR fixes, and lifecycle observability

Addresses https://redhat.atlassian.net/browse/RHOAIENG-60708

## Description
Post-split cleanup for `maas-controller` RBAC, CR lifecycle edge cases, and controller observability. Addresses the three ACs from the ticket:

**AC1 / AC3** — RBAC justification at source

Moved RBAC permission rationale from `clusterrole.yaml` (where `controller-gen` strips it on every regeneration) into the `+kubebuilder:rbac` marker blocks in Go source, where it is permanent and visible to developers changing permissions:

* `tenant_controller.go`: documents why secrets `get;list;watch` must remain unrestricted (`payload-processing-reader` escalation check + Kubernetes `list/watch` cannot use resourceNames); why `clusterroles/clusterrolebindings` CRUD is required (SSA-applies `maas-api` and `payload-processing-reader` ClusterRoles); and the escalation-check mirror pattern for maas-api verbs (`endpoints`, `pods`, `serviceaccounts/token`, `tokenreviews`, `subjectaccessreviews`).
* `self_deployment_controller.go`: documents the teardown-only `list;delete` verbs for ClusterRoles and CRDs used by LifecycleReconciler on ODH disable.

**AC2** — CR lifecycle nil/partial CR handling

Three targeted fixes with matching unit tests:
* `maasauthpolicy_controller.go`: `fetchOIDCConfig` moved after the MaaSAuthPolicy not-found guard — stale or deleted-race reconcile events no longer trigger an unnecessary Tenant Get.
* `self_deployment_controller.go`: log a visible Info message when a terminating Deployment has no CleanupFinalizer (previously a silent no-op with no observability).
* `self_deployment_controller.go`: log a visible Info message in deleteClusterScopedResources when no ClusterRoles, CRDs, or ClusterRoleBindings match the componentLabel — surfaces cases where the operator did not stamp the label.
* main.go: document the four-step startup ordering contract (namespace bootstrap → ensureDefaultTenantRunnable → TenantReconciler → ODH operator race window) as a code comment.


## How Has This Been Tested?
```
# Unit tests — all pass including three new tests
make -C maas-controller test

# Generated files still in sync with markers after comments moved to Go source
make -C maas-controller manifests verify-codegen
```
Also, added couple of new unit tests

## Merge criteria:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

## Release Notes

* **Bug Fixes**
  * Enhanced handling of stale events in authentication policy reconciliation to prevent unnecessary operations.

* **Documentation**
  * Clarified startup ordering contract and expanded RBAC permissions documentation for controller initialization.

* **Improvements**
  * Added explicit logging for deployment cleanup operations for better observability.

* **Tests**
  * Increased test coverage for edge cases including missing finalizers and stale event scenarios.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-controller/cmd/manager/main.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller_test.go`
- `maas-controller/pkg/controller/maas/self_deployment_controller.go`
- `maas-controller/pkg/controller/maas/self_deployment_controller_test.go`
- `maas-controller/pkg/controller/maas/tenant_controller.go`
