# chore: promote main to stable

## Promotion: main → stable

Automated promotion of **4 commit(s)** from `main` to `stable`.

| Detail | Value |
| --- | --- |
| Promotion | `main` → `stable` |
| Commits to merge | **4** |
| Conflict check | ✅ Passed |

### Commits included

````
a24c8c8 feat: add standalone setup-gateway.sh script for maas-default-gateway (#941)
bb18f4a fix: restore --dev flag in deploy script argument parser (#939)
0ee18b6 refactor: move Tenant reconciler away from params.env and maas-parameters (#864)
85d3311 feat: add access log middleware with sensitive header redaction (#871)
````

---
⚠️ **Merge this PR with a merge commit** (do not squash or rebase).


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
- `docs/content/configuration-and-management/gateway-patterns.md`
- `docs/content/configuration-and-management/tls-configuration.md`
- `docs/content/contributing/release-strategy.md`
- `docs/content/contributing/testing-guide.md`
- `docs/content/install/maas-setup.md`
- `docs/samples/gateway-patterns/clusterip-route-reencrypt/openshift-route.yaml`
- `maas-api/cmd/main.go`
- `maas-api/deploy/overlays/dev/kustomization.yaml`
- `maas-api/deploy/overlays/dev/params.env`
- `maas-api/deploy/overlays/odh/kustomization.yaml`
- `maas-api/deploy/overlays/odh/params.env`
- `maas-api/internal/logger/redaction.go`
- `maas-api/internal/logger/redaction_test.go`
- `maas-api/internal/middleware/access_log.go`
- `maas-api/internal/middleware/request_id_test.go`
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
- `scripts/README.md`
- `scripts/deploy.sh`
- `scripts/deployment-helpers.sh`
- `scripts/setup-gateway.sh`
- `test/e2e/scripts/local-deploy.sh`
