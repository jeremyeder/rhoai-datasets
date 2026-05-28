# feat(RHOAIENG-60867): controller: reconcile governance attachment into MaaSModelRef status

Add GovernanceAttached and RuntimeReady conditions to MaaSModelRef
status so that phase and conditions reflect whether a model is covered
by an active MaaSSubscription + MaaSAuthPolicy pairing.

Phase semantics:
- Pending: no governance pairing or backend not ready
- Ready: governed and runtime-healthy
- Unhealthy: governed but backend has a runtime failure
- Failed/Invalid: reconciliation error or bad spec

The controller now watches MaaSSubscription and MaaSAuthPolicy for
changes and re-reconciles affected MaaSModelRef resources. No admin
CR names, namespaces, or UIDs appear in any status field.

Includes unit tests for all governance scenarios: no pairing, active
pairing, pairing removed (GovernanceGap), runtime failure with
governance, both failures, privacy checks, and mapper functions.

Closes [RHOAIENG-60867](https://redhat.atlassian.net/browse/RHOAIENG-60867)
Co-Authored-By: Claude <noreply@anthropic.com>
Signed-off-by: Ishita Sequeira <isequeir@redhat.com>

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Richer model status with explicit governance attachment and runtime health conditions; expanded Phase semantics and new condition types (GovernanceAttached, RuntimeReady) and reason values for clearer status reporting.

* **Tests**
  * Expanded unit and e2e tests covering governance interactions, pairing states, runtime failures, race conditions, and subscription/auth policy mappings.

* **Chores**
  * Updated monitoring and RBAC to manage pod monitors; lint/test config tweaks to support new checks and tests.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_maasauthpolicies.yaml`
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_maasmodelrefs.yaml`
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_maassubscriptions.yaml`
- `maas-controller/.golangci.yml`
- `maas-controller/api/maas/v1alpha1/common_types.go`
- `maas-controller/api/maas/v1alpha1/maasmodelref_types.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller_test.go`
- `test/e2e/scripts/prow_run_smoke_test.sh`
- `test/e2e/tests/test_subscription.py`
