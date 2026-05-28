# chore: add SAR Admin cache

https://redhat.atlassian.net/browse/RHOAIENG-54975

## Description
This PR introduces new files:
- `maas-api/internal/auth/cached_admin_checker.go` — CachedAdminChecker wrapping SARAdminChecker with TTL-based cache (30s), sync.RWMutex+map for thread safety, lazy eviction of expired entries, and Prometheus counters (`sar_cache_hits_total`, `sar_cache_misses_total`)
  -  additionally, used `negative TTL` which is the cache duration for "not admin" results, as opposed to the regular ttl which applies to "is admin" (true) results. This utilizes `asymmetric caching`:
```
**true (admin)** - long TTL (30s): Admin status is stable and slow to change. Caching it longer reduces K8s API server load.
**false (not admin)** - short TTL (2s): A user who was just granted admin RBAC shouldn't have to wait 30s for the cache to expire. A short negative TTL means they get re-checked quickly.
```
- `maas-api/internal/auth/cached_admin_checker_test.go` — 15 tests covering cache hits/misses, TTL expiry, group-order invariance, fail-closed guards, metrics, concurrent access, eviction, and constructor panics

As well as, I modified files:
- `maas-api/internal/config/cluster_config.go` — AdminChecker field changed to *auth.CachedAdminChecker, wraps SARAdminChecker with 30s TTL
- `maas-api/cmd/main.go` — added /metrics endpoint via promhttp.Handler()
- `maas-api/go.mod / go.sum` — prometheus/client_golang promoted to direct dependency

## How Has This Been Tested?
The existing `E2E test suite` already covers the **admin auth** path end-to-end:
Admin authorization tests (`test/e2e/tests/test_api_keys.py`):
- test_admin_manage_other_users_keys — admin can list/filter/revoke other users' keys
- test_non_admin_cannot_access_other_users_keys — non-admin gets 404 (IDOR protection)
- test_bulk_revoke_admin_can_revoke_any_user — admin-only bulk revoke

SAR path exercised via smoke tests (`test/e2e/scripts/prow_run_smoke_test.sh`, `test/e2e/smoke.sh`):
- Sets up RBAC granting create `maasauthpolicies` permission
- Admin token goes through the full path: `user` - `maas-api` - `Kubernetes SubjectAccessReview` - `RBAC check`

The SAR admin check is already exercised E2E — requests from the admin user hits `CachedAdminChecker`, which delegates to `SARAdminChecker`, which calls the real Kubernetes API. The cache works as intended as part of the E2E tests since it doesn't change observable behaviuor.

As for **TTL expiry, eviction, metrics, asymmetric TTL**, those are implementation details best validated by the unit tests that we introdued. Adding `E2E` tests for cache would slow-down the smoke test by a lot for a minimual gain, while units tests serve as a proof the code works. 

## Merge criteria:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Prometheus metrics endpoint added (GET /metrics) for observing runtime metrics.

* **Performance**
  * Admin authorization checks now cached with a 30s TTL to reduce repeated lookups.

* **Tests**
  * Comprehensive tests added covering caching behavior, TTL expiry, concurrency, and metrics counters.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-api/cmd/main.go`
- `maas-api/go.mod`
- `maas-api/internal/api_keys/handler.go`
- `maas-api/internal/api_keys/handler_test.go`
- `maas-api/internal/auth/cached_admin_checker.go`
- `maas-api/internal/auth/cached_admin_checker_test.go`
- `maas-api/internal/auth/sar_admin_checker.go`
- `maas-api/internal/auth/sar_admin_checker_test.go`
- `maas-api/internal/config/cluster_config.go`
- `maas-api/internal/config/config.go`
- `maas-api/internal/constant/const.go`
