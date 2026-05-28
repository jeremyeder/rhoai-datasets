# chore: promote main to stable

Automated promotion of **16 commit(s)** from `main` to `stable`.

```
02f86ce fix: use odh-stable image tags in odh overlay and add dev overlay (#896)
2bc0e66 test: add E2E tests for Tenant CR lifecycle (#869)
90ea64a chore: fix CI failures (#932)
7cebe73 chore: remove reviewers from OWNERS to disable prow auto-assignment (#931)
fb76894 chore: restrict /lgtm to approvers and add CODEOWNERS for review assignment (#928)
13a9ccd ci: harden promote-stable-to-rhoai merge step (#927)
41b2aed docs: add ModelsAsService to Tenant CR transition to upgrade guide (#923)
30744fa ci: replace PR-based stable→rhoai promotion with direct merge commit (#926)
47d0b3f chore: add isManaged check for all resources managed by maas-controller (#920)
43bd2ba docs: update API key endpoints sample requests and responses (#921)
9adb8b2 fix(maas-api): use ExternalModel name as model ID in GET /v1/models [RHOAIENG-63297] (#919)
b4f20ec feat: add subscription filter to POST /api-keys/search (#918)
6d40b19 refactor: reconcile gateway configuration sources [RHOAIENG-62286] (#909)
9bebd69 feat(maas-api): enrich model refs with displayName and description in GET /subscriptions (#913)
7f759eb feat(maas-api): enable TLS certificate validation for internal gateway calls (#707)
fd24b95 fix: update default RHOAI operator channel from fast-3.x to stable-3.x (#908)
```


## Files involved
- `.github/CODEOWNERS`
- `.github/workflows/openapi-validation.yml`
- `.github/workflows/promote-stable-to-rhoai.yml`
- `CONTRIBUTING.md`
- `OWNERS`
- `README.md`
- `deployment/base/maas-api/core/kustomization.yaml`
- `deployment/base/maas-controller/manager/kustomization.yaml`
- `deployment/overlays/dev/params.env`
- `deployment/overlays/odh/params.env`
- `docs/content/configuration-and-management/quota-and-access-configuration.md`
- `docs/content/contributing/release-strategy.md`
- `docs/content/contributing/testing-guide.md`
- `docs/content/install/platform-setup.md`
- `docs/content/migration/upgrade-to-3.4.md`
- `docs/content/user-guide/api-key-management.md`
- `docs/mkdocs.yml`
- `maas-api/cmd/main.go`
- `maas-api/deploy/overlays/dev/kustomization.yaml`
- `maas-api/deploy/overlays/dev/params.env`
- `maas-api/deploy/overlays/odh/params.env`
- `maas-api/internal/api_keys/handler_test.go`
- `maas-api/internal/api_keys/store_mock.go`
- `maas-api/internal/api_keys/store_postgres.go`
- `maas-api/internal/api_keys/types.go`
- `maas-api/internal/handlers/models_test.go`
- `maas-api/internal/models/discovery.go`
- `maas-api/internal/models/discovery_test.go`
- `maas-api/internal/models/maasmodelref.go`
- `maas-api/internal/subscription/handler_test.go`
- `maas-api/internal/subscription/selector.go`
- `maas-api/internal/subscription/selector_test.go`
- `maas-api/internal/subscription/types.go`
- `maas-api/openapi3.yaml`
- `maas-controller/cmd/manager/main.go`
- `maas-controller/pkg/controller/maas/annotations.go`
- `maas-controller/pkg/controller/maas/cross_namespace_test.go`
- `maas-controller/pkg/controller/maas/maasauthpolicy_controller.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller.go`
- `maas-controller/pkg/controller/maas/maasmodelref_controller_test.go`
- `maas-controller/pkg/controller/maas/tenant_controller.go`
- `maas-controller/pkg/controller/maas/tenant_reconcile.go`
- `maas-controller/pkg/controller/maas/tenant_reconcile_test.go`
- `maas-controller/pkg/platform/tenantreconcile/constants.go`
- `maas-controller/pkg/platform/tenantreconcile/kustomize.go`
- `maas-controller/pkg/platform/tenantreconcile/postrender.go`
- `maas-controller/pkg/reconciler/externalmodel/reconciler.go`
- `maas-controller/pkg/reconciler/externalmodel/reconciler_test.go`
- `scripts/README.md`
- `scripts/deploy.sh`
- `scripts/deployment-helpers.sh`
- `test/e2e/README.md`
- `test/e2e/fixtures/distinct/maas/maas-model.yaml`
- `test/e2e/scripts/prow_run_smoke_test.sh`
- `test/e2e/tests/test_api_keys.py`
- `test/e2e/tests/test_config_tenant.py`
- `test/e2e/tests/test_subscription_list_endpoints.py`
- `test/e2e/tests/test_tenant.py`
