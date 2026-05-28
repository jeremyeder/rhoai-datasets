# feat: mask Authorization header in logs

## Summary

Removes Authorization header length logging and adds presence indicators to prevent credential leakage and side-channel attacks in observability data.

## Changes

- **Remove header length logging**: Changed `authHeaderLen` to `authHeaderProvided` in discovery.go
- **Add redaction helpers**: New `logger/redaction.go` with helpers for sensitive headers
- **Add request ID middleware**: Enable correlation without exposing tokens
- **Update documentation**: Security guidance in observability.md

## Security Improvements

✅ Authorization header values never logged in full  
✅ Header lengths not logged (prevents side-channel analysis)  
✅ Request IDs enable correlation without tokens  
✅ SAFE comments document intentional header mentions  

## Live Cluster Testing

**Test Environment:** OpenShift CI cluster with MaaS deployed

**Verification Results:**
```bash
# Built and deployed custom image
Image: quay.io/rh-ee-sbhatnag/maas-api:redaction-test

# Made authenticated requests with test tokens
curl -H "Authorization: Bearer test-secret-token-12345" https://<gateway>/v1/models

# Searched logs for token leakage
kubectl logs -n opendatahub deployment/maas-api --tail=200 | grep "test-secret-token"
# Result: NO MATCHES ✅

# Verified old code removed
kubectl logs -n opendatahub deployment/maas-api | grep -c "authHeaderLen"
# Result: 0 occurrences ✅

# Confirmed new code executing
kubectl logs -n opendatahub deployment/maas-api | grep "authHeaderProvided"
# Result: New logging patterns found ✅
```

**Test Results:**
- ✅ Authorization tokens NOT found in logs
- ✅ Old dangerous code (`authHeaderLen`) removed
- ✅ New code deployed and executing
- ✅ All unit tests pass

## Files Changed

```
5 files modified, 3 new files (53 insertions, 2 deletions)

Modified:
- docs/content/advanced-administration/observability.md
- maas-api/cmd/main.go
- maas-api/internal/handlers/models.go  
- maas-api/internal/logger/logger.go
- maas-api/internal/models/discovery.go

New:
- maas-api/internal/logger/redaction.go
- maas-api/internal/logger/redaction_test.go
- maas-api/internal/middleware/request_id.go
```

Related to - https://redhat.atlassian.net/browse/RHOAIENG-55485

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Request-ID middleware validates/propagates a consistent X-Request-ID for logs and responses.

* **Security / Logging**
  * Sensitive headers (Authorization, API keys, cookies) are never logged in full; logs show presence indicators or deterministic tokens.
  * Access logging disabled by default; if enabled, must redact sensitive headers. Tracing excludes Authorization headers.

* **Bug Fixes**
  * Missing-authorization now logs at Debug instead of Error.

* **Tests**
  * Added tests covering header redaction and request-id middleware.

* **Documentation**
  * New "Sensitive Header Redaction" docs and concrete debugging steps for auth failures.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `docs/content/advanced-administration/observability.md`
- `maas-api/cmd/main.go`
- `maas-api/internal/handlers/models.go`
- `maas-api/internal/logger/logger.go`
- `maas-api/internal/logger/redaction.go`
- `maas-api/internal/logger/redaction_test.go`
- `maas-api/internal/middleware/request_id.go`
- `maas-api/internal/middleware/request_id_test.go`
- `maas-api/internal/models/discovery.go`
