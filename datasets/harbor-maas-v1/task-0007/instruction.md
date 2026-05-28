# feat: detect rogue or conflicting AuthPolicies on MaaS auth surfaces

Add conflict detection to the MaaSAuthPolicy reconciler that identifies
non-MaaS Kuadrant AuthPolicies targeting the same HTTPRoutes used by
MaaS-governed models. When conflicts are detected (e.g., KServe
KserveAuthPolicyReconciler creating *-kserve-route-authn policies on
the same route), the controller:

- Sets a ConflictingAuthPolicy condition (True/False) on the
  MaaSAuthPolicy status, naming the conflicting policies
- Emits Kubernetes warning events for operator visibility
- Logs structured warnings with model, HTTPRoute, and policy details

Detection runs during each reconcile cycle. When conflicting policies
are removed, the condition automatically transitions back to False.

Includes 10 unit tests covering: no-conflict baseline, single/multiple
rogue detection, different-route exclusion, cross-namespace isolation,
conflict resolution lifecycle, missing model handling, and Gateway
target filtering.

Adds troubleshooting documentation with diagnosis commands and
remediation steps for KServe anonymous auth policies and custom
AuthPolicy conflicts.

Closes [RHOAIENG-61515](https://redhat.atlassian.net/browse/RHOAIENG-61515)

Co-Authored-By: Claude <noreply@anthropic.com>
Signed-off-by: Jamie Land <jland@redhat.com>

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Detects non-MaaS AuthPolicies that conflict with MaaS-managed HTTPRoutes, surfaces a status condition, and emits warning events when conflicts are found.

* **Documentation**
  * Added a troubleshooting guide for detecting and resolving conflicting AuthPolicies (symptoms, diagnosis steps, remediation).

* **Tests**
  * Added comprehensive unit tests covering conflict detection, condition setting, deduplication, and related scenarios.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `deployment/base/maas-controller/rbac/clusterrole.yaml`
- `docs/content/install/troubleshooting.md`
- `maas-controller/pkg/controller/maas/conflict_detection.go`
- `maas-controller/pkg/controller/maas/conflict_detection_test.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller.go`
