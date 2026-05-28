# fix: mandate spec for MaaS CRs

<!--- Provide a general summary of your changes in the Title above -->
https://redhat.atlassian.net/browse/RHOAIENG-59640

## Description
<!--- Describe your changes in detail -->
This PR:
1. mandates `spec` in MaaS CRs (MaaSAuthPolicy, MaaSSubscription, MaaSModelRef, Tenant); and
2. for the first three, considers backward compat and reports `Invalid` when `spec` doesn't exist.

## How Has This Been Tested?
<!--- Please describe in detail how you tested your changes. -->
<!--- Include details of your testing environment, and the tests you ran to -->
<!--- see how your change affects other areas of the code, etc. -->
1. Create no-spec CRs. Their phases remain empty.
2. Deploy the PR image.
3. Observe that no-spec CRs have `Invalid` phases.
4. Try creating new no-spec CRs and get blocked.

## Merge criteria:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Bug Fixes**
  * API validation now requires the top-level spec for MaaS resources; resources missing spec are rejected and show clear error messages.
  * Controllers now short-circuit on missing/empty spec: resources are marked Invalid (Ready=False, reason InvalidSpec), skip finalizer installation and further reconciliation.

* **Tests**
  * Added reconciliation tests for legacy/empty-spec resources to verify deterministic Invalid status and no finalizers.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_externalmodels.yaml`
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_maasauthpolicies.yaml`
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_maasmodelrefs.yaml`
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_maassubscriptions.yaml`
- `maas-controller/api/maas/v1alpha1/common_types.go`
- `maas-controller/api/maas/v1alpha1/externalmodel_types.go`
- `maas-controller/api/maas/v1alpha1/maasauthpolicy_types.go`
- `maas-controller/api/maas/v1alpha1/maasmodelref_types.go`
- `maas-controller/api/maas/v1alpha1/maassubscription_types.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller_test.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller_test.go`
- `maas-controller/pkg/controller/maas/maassubscription_controller.go`
- `maas-controller/pkg/controller/maas/maassubscription_controller_test.go`
