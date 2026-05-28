# chore: promote stable to rhoai

Automated promotion of **7 commit(s)** from `stable` to `rhoai`.

```
b9211b4 fix: fixing cleanup issue where not all objects were removed (#894)
3b1e5dd docs: add telemetry defaults and cardinality guidance (#768)
d98eeb5 feat: detect rogue or conflicting AuthPolicies on MaaS auth surfaces (#882)
eef74cf chore: update llm-katan simulator endpoint to new AWS instance (#890)
962ba70 fix: resolve postgresql image from operator CSV in setup-database (#778)
d19959f chore: updating to a smaller subset of owners (#891)
```


## Files involved
- `.github/hack/cleanup-odh.sh`
- `AGENTS.md`
- `OWNERS`
- `deployment/base/maas-controller/crd/bases/maas.opendatahub.io_configs.yaml`
- `deployment/base/maas-controller/crd/kustomization.yaml`
- `deployment/base/maas-controller/default/config-default.yaml`
- `deployment/base/maas-controller/manager/manager.yaml`
- `deployment/base/maas-controller/rbac/clusterrole.yaml`
- `deployment/base/maas-controller/rbac/clusterrole_maas_configs.yaml`
- `deployment/base/maas-controller/rbac/clusterrolebinding_maas_configs.yaml`
- `deployment/base/maas-controller/rbac/kustomization.yaml`
- `docs/content/advanced-administration/telemetry-defaults-and-cardinality.md`
- `docs/content/install/maas-setup.md`
- `docs/content/install/troubleshooting.md`
- `docs/content/migration/tier-to-subscription.md`
- `maas-controller/Makefile`
- `maas-controller/README.md`
- `maas-controller/api/maas/v1alpha1/config_types.go`
- `maas-controller/api/maas/v1alpha1/zz_generated.deepcopy.go`
- `maas-controller/cmd/manager/main.go`
- `maas-controller/container.mk`
- `maas-controller/docs/old-vs-new-flow.md`
- `maas-controller/pkg/controller/maas/conflict_detection.go`
- `maas-controller/pkg/controller/maas/conflict_detection_test.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller.go`
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
- `scripts/setup-database.sh`
- `test/e2e/scripts/LOCAL-DEPLOY.md`
- `test/e2e/scripts/auth_utils.sh`
- `test/e2e/scripts/local-deploy.sh`
