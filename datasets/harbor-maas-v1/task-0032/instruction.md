# fix(e2e): avoid creating service accounts in default namespace

## Summary
Some clusters (eg. ROSA) restrict deletion of service accounts in the `default` namespace, causing test cleanup failures.

- Replace `namespace="default"` with `namespace=MODEL_NAMESPACE` for all e2e test service account operations (`_create_sa_token`, `_sa_to_user`, `_delete_sa`)
- Replace hardcoded `f"system:serviceaccount:default:{sa_name}"` strings with `_sa_to_user(sa_name, namespace=MODEL_NAMESPACE)` for consistency

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Tests**
  * Updated end-to-end tests to use model-scoped namespace configuration for service account operations, improving test environment consistency and cleanup procedures.

**Note:** This release contains no user-facing changes. Updates are internal to testing infrastructure.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `test/e2e/tests/test_api_keys.py`
- `test/e2e/tests/test_subscription.py`
