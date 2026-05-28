# feat(maas-api): enrich model refs with displayName and description in GET /subscriptions

## Summary

Add `display_name` and `description` fields to `ModelRefInfo` in `GET /v1/subscriptions`, populated from the `openshift.io/display-name` and `openshift.io/description` annotations on the corresponding `MaaSModelRef` CR.

Jira: https://issues.redhat.com/browse/RHOAIENG-62490

## Description

The `GET /subscriptions` response previously returned model refs with only `name`, `namespace`, `token_rate_limits`, and `billing_rate`. UI consumers had to make an additional `GET /v1/models` call to resolve human-readable model metadata.

Key changes:
- Add `DisplayName` and `Description` (`omitempty`) to `ModelRefInfo` in `types.go`
- Inject `MaaSModelRefLister` into `Selector`; `buildModelIndex()` builds a single `namespace/name → unstructured` map once per `loadSubscriptions()` call to avoid repeated `List()` calls per model ref
- Pass `MaaSModelRefLister` to `NewSelector` in `cmd/main.go` (already available in `ClusterConfig`)
- Update `openapi3.yaml` `ModelRefInfo` schema with the two new fields
- Enrichment is read-path only — no controller changes required; `MaaSModelRef` annotations are already written by the controller
- Fails gracefully (fields are empty) when the model lister is `nil`, `List()` errors, or the model ref is not yet in the informer cache — no impact on existing consumers

## How it was tested

- **Unit tests**: 3 new tests in `handler_test.go` covering the happy path, nil lister (graceful degradation), and model-not-found (graceful degradation). All 16 `maas-api` packages pass.
- **E2E test**: New `test_model_ref_display_name_and_description_enriched` in `test_subscription_list_endpoints.py` creates a `MaaSModelRef` with annotations on the cluster, creates a subscription pointing to it, calls `GET /v1/subscriptions`, and hard-asserts `display_name` and `description` match the annotations.
- **Schema validation**: Extended `_validate_subscription_info_schema` to type-check `display_name` and `description` on model refs when present, covering all existing e2e subscription list tests.
- **Build**: `go build ./...` passes cleanly.
- Also tested on the clusterbot cluster, here are the before and after test results - 

BEFORE — quay.io/opendatahub/maas-api:latest
```
"model_refs": [
  {
    "name": "facebook-opt-125m-simulated",
    "namespace": "llm",
    "token_rate_limits": [{"limit": 100, "window": "1m"}]
  }
]
```
AFTER — quay.io/chkulkar/maas-api:[RHOAIENG-62490](https://redhat.atlassian.net/browse/RHOAIENG-62490)
```
"model_refs": [
  {
    "name": "facebook-opt-125m-simulated",
    "namespace": "llm",
    "display_name": "Facebook OPT 125M (Simulated)",
    "description": "A simulated OPT-125M model for free-tier testing",
    "token_rate_limits": [{"limit": 100, "window": "1m"}]
  }
]
```

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **New Features**
  * Subscription list endpoints now enrich model references with display names and descriptions sourced from model resource metadata.

* **Documentation**
  * Updated API specification to document display name and description fields in subscription model reference responses.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `.github/workflows/openapi-validation.yml`
- `maas-api/cmd/main.go`
- `maas-api/internal/handlers/models_test.go`
- `maas-api/internal/subscription/handler_test.go`
- `maas-api/internal/subscription/selector.go`
- `maas-api/internal/subscription/selector_test.go`
- `maas-api/internal/subscription/types.go`
- `maas-api/openapi3.yaml`
- `test/e2e/fixtures/distinct/maas/maas-model.yaml`
- `test/e2e/tests/test_subscription_list_endpoints.py`
