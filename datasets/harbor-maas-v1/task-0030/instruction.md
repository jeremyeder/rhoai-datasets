# feat: add subscription filter to POST /api-keys/search

## Summary

- Add optional `subscription` filter to POST /api-keys/search so users can scope results to a specific subscription

## Changes

- **`maas-api/internal/api_keys/types.go`**: Add `Subscription *string` to `SearchFilters`
- **`maas-api/internal/api_keys/store_postgres.go`**: Add `subscription = $N` WHERE clause when filter is provided
- **`maas-api/internal/api_keys/store_mock.go`**: Add subscription filtering to mock store's `Search()`
- **`maas-api/internal/api_keys/handler_test.go`**: Add `TestSearchAPIKeys_SubscriptionFilter` with two subtests: filter by subscription returns scoped results, no filter returns all keys

## Usage

```json
POST /v1/api-keys/search
{
  "filters": {
    "subscription": "my-subscription-name"
  }
}
```

## Test plan

- [x] Unit test: filter by subscription returns only matching keys
- [x] Unit test: no filter returns all keys (backward compatible)
- [ ] `go build ./...` passes
- [ ] `go test ./internal/api_keys/...` passes

Ref: [RHAISTRAT-1547](https://redhat.atlassian.net/browse/RHAISTRAT-1547)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Added subscription filtering to API key search, letting users narrow results to keys bound to a specific subscription.

* **Tests**
  * Added unit and end-to-end tests covering subscription-based search behavior to ensure correct filtering and overall search results.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-api/internal/api_keys/handler_test.go`
- `maas-api/internal/api_keys/store_mock.go`
- `maas-api/internal/api_keys/store_postgres.go`
- `maas-api/internal/api_keys/types.go`
- `test/e2e/tests/test_api_keys.py`
