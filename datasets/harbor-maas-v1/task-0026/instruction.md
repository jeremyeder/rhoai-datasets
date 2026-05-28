# refactor: move Tenant reconciler away from params.env and maas-parameters

<!--- Provide a general summary of your changes in the Title above -->
https://redhat.atlassian.net/browse/RHOAIENG-59864

## Description
<!--- Describe your changes in detail -->
**Major**

This PR consolidates the ownership of `params.env` and ConfigMap `maas-parameters`. After the change, only ODH reads from `params.env` and writes to `maas-parameters`, MaaS doesn't any more. Instead, Tenant reconciler gathers required params from MaaS controller args/env vars, Tenant CR and auto-detection, and patches them to the manifests with code instead of kustomize.

**Minor**

This PR also includes some other chores:
- starts to move `params.env` from outdated `/overlays/odh` to `base/maas-controller/default`, and includes only the necessary params there (the image ones).
- cleans up useless `shared-patches` and MaaS-side `params.env`.
- updates a whole bunch of stale or dead docs, scripts and comments.

## How Has This Been Tested?
<!--- Please describe in detail how you tested your changes. -->
<!--- Include details of your testing environment, and the tests you ran to -->
<!--- see how your change affects other areas of the code, etc. -->
Deployed on a cluster and verified all resources work as before and pass all E2E tests.

## Merge criteria:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Chores**
  * Platform values (images, gateway, namespace, audience, API key expiry) are now injected during post-render, eliminating previous file-based parameterization.
  * Image defaults for maas-api, maas-controller, payload-processing, and maas-api-key-cleanup are explicitly configurable.
  * Deployment/installer now manages a ConfigMap for image overrides instead of env-var patching.
  * Reduced unnecessary reconciliations previously triggered by deleted ConfigMaps.

* **Improvements**
  * Better handling and readiness processing for additional resource types (HTTPRoute, CronJob).
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `.github/hack/cleanup-odh.sh`
- `.github/scripts/update-kustomize-tag.sh`
- `.github/workflows/create-release.yml`
- `AGENTS.md`
- `README.md`
- `deployment/base/maas-api/policies/auth-policy.yaml`
- `deployment/base/maas-controller/default/params.env`
- `deployment/base/maas-controller/manager/manager.yaml`
- `deployment/components/shared-patches/kustomization.yaml`
- `deployment/overlays/dev/params.env`
- `docs/content/configuration-and-management/authorino-caching.md`
- `docs/content/configuration-and-management/tls-configuration.md`
- `docs/content/contributing/release-strategy.md`
- `docs/content/contributing/testing-guide.md`
- `maas-api/deploy/overlays/dev/kustomization.yaml`
- `maas-api/deploy/overlays/dev/params.env`
- `maas-api/deploy/overlays/odh/kustomization.yaml`
- `maas-api/deploy/overlays/odh/params.env`
- `maas-controller/README.md`
- `maas-controller/cmd/manager/main.go`
- `maas-controller/pkg/controller/maas/tenant_controller.go`
- `maas-controller/pkg/controller/maas/tenant_reconcile.go`
- `maas-controller/pkg/platform/tenantreconcile/apply.go`
- `maas-controller/pkg/platform/tenantreconcile/constants.go`
- `maas-controller/pkg/platform/tenantreconcile/params.go`
- `maas-controller/pkg/platform/tenantreconcile/params_test.go`
- `maas-controller/pkg/platform/tenantreconcile/pipeline.go`
- `maas-controller/pkg/platform/tenantreconcile/postrender.go`
- `maas-controller/pkg/platform/tenantreconcile/prerequisites.go`
- `scripts/deploy.sh`
- `scripts/deployment-helpers.sh`
- `test/e2e/scripts/local-deploy.sh`
