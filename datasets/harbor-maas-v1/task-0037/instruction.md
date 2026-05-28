# fix(test): use HTTPS endpoint for cleanup in e2e API key test

## Summary

- The `test_trigger_cleanup_preserves_active_keys` e2e test triggers the internal cleanup endpoint by exec'ing into the maas-api pod. The internal server listens on port 8443 with TLS, not plain HTTP on 8080.
- Updates both curl and wget commands to use `https://localhost:8443` instead of `http://localhost:8080`.
- Adds `-k` (curl) / `--no-check-certificate` (wget) to skip TLS certificate verification for the self-signed/cluster-internal certificate.

## Test plan
- [ ] Run `test_trigger_cleanup_preserves_active_keys` e2e test against a cluster with TLS-enabled maas-api
- [ ] Verify the cleanup endpoint is reachable and returns a valid response

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Tests**
  * Updated API key cleanup test to use HTTPS instead of HTTP for improved security in test infrastructure.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `test/e2e/tests/test_api_keys.py`
