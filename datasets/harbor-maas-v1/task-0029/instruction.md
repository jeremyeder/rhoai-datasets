# chore: add isManaged check for all resources managed by maas-controller

## Description

Audits all resource types reconciled by `maas-controller` to confirm the `opendatahub.io/managed=false` opt-out annotation is respected on both the write (create/update) and delete paths.

## How Has This Been Tested?

New unit tests in `pkg/reconciler/externalmodel/reconciler_test.go` cover the added behaviour:

- `TestManagedAnnotation_Service` — write-path opt-out: pre-existing Service with `managed=false` keeps its sentinel `ExternalName` after reconcile.
- `TestManagedAnnotation_ServiceEntry` — write-path opt-out: pre-existing ServiceEntry spec is untouched.
- `TestManagedAnnotation_HTTPRoute` — write-path opt-out: pre-existing HTTPRoute parent ref is untouched.
- `TestManagedAnnotation_DestinationRule_DeletePath` — delete-path opt-out: stale DestinationRule with `managed=false` survives the TLS→no-TLS transition that would otherwise call `deleteIfExists`.
- `TestIsManaged` — unit-tests the helper across all edge cases (nil annotations, absent key, `false`, `true`, other values, case-sensitivity).

Each test includes the three-way table `absent / managed=false / managed=true` to confirm the positive and negative cases.
https://redhat.atlassian.net/browse/RHOAIENG-60911

## Merge criteria:
- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [ ] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

## Release Notes

* **New Features**
  * Resources can now opt-out of automatic management by setting the `opendatahub.io/managed=false` annotation. When applied, the controller will skip updates and deletions for annotated resources.

* **Tests**
  * Added comprehensive test coverage for opt-out annotation behavior across service management, gateway routing, and resource lifecycle operations.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-controller/pkg/controller/maas/annotations.go`
- `maas-controller/pkg/platform/tenantreconcile/constants.go`
- `maas-controller/pkg/platform/tenantreconcile/postrender.go`
- `maas-controller/pkg/reconciler/externalmodel/reconciler.go`
- `maas-controller/pkg/reconciler/externalmodel/reconciler_test.go`
