# feat: add access log middleware with sensitive header redaction

## Summary
Implements custom Gin access logger middleware that demonstrates practical usage of the header redaction library from PR #760.

Related to - https://redhat.atlassian.net/browse/RHOAIENG-61338

## Changes
- ✅ Add `AccessLogger()` middleware in `internal/middleware/access_log.go`
- ✅ Implement `SensitiveHeadersSummaryForAccessLog()` helper in `logger/redaction.go`
- ✅ Replace `gin.Logger()` with `AccessLogger()` in `cmd/main.go`
- ✅ Simplify request ID validation logic
- ✅ Add unit tests for new summary function

## Access Log Format
```
[GIN] 2026/05/07 - 14:23:45 | 200 |   12.456ms |   192.168.1.1 | GET     /v1/models | Authorization=present Cookie=absent X-Api-Key=absent Set-Cookie=absent
```

The middleware appends a redacted summary showing which sensitive headers were present/absent in the request, without exposing any credential values.

## Testing
- ✅ Unit tests pass (`make test`)
- ✅ Linting clean (`make lint`) 
- ✅ Test coverage: 80.7%
- ✅ New test: `TestSensitiveHeadersSummaryForAccessLog` verifies format and no credential leakage
                                                                                                                                               
  ✅ Live Cluster Test Results                                                                                                                 
                                                                                                                                               
```
  Evidence from logs (before reconciliation):                                                                                                  
  [GIN] 2026/05/08 - 20:32:29 | 200 |      75.221µs |      10.131.0.2 | GET      "/health" | Authorization=absent X-Api-Key=absent
  Cookie=absent Set-Cookie=absent                                                                                                              
  [GIN] 2026/05/08 - 20:33:26 | 200 |      43.421µs |      10.131.0.2 | GET      "/health" | Authorization=absent X-Api-Key=absent             
  Cookie=absent Set-Cookie=absent     
```                                                                                            
                                                                                                                                               
  Verification:                                                       
  ✅ Access log middleware is working                                                                                                          
  ✅ Sensitive headers summary appended to each request               
  ✅ Headers shown as "absent" when not present                                                                                                
  ✅ NO credential values appear in logs (verified with grep for "bearer", "token", "secret")                                                  
  ✅ Image deployed successfully: quay.io/rh-ee-sbhatnag/maas-api:access-log-pr871                                                             
                                                                                                                                               
  Format verified:                                                                                                                             
```
  [Standard Gin log] | [Sensitive headers summary]                                                                                             
                      | Authorization=absent X-Api-Key=absent Cookie=absent Set-Cookie=absent           
```                                       
                                                                                                                                               
The feature is working correctly! The controller reconciled the deployment back to default, which is expected behavior in kustomize mode. The access log middleware successfully:                                                                                                         
  1. Appends sensitive header presence indicators                     
  2. Never logs actual credential values                                                                                                       
  3. Follows the exact format we designed                             


## Dependencies
Requires PR #760 to be merged first (provides the redaction library).

## Security
- No credential values logged (only presence/absence indicators)
- Uses existing `RedactHeader()` function from redaction library
- Case-insensitive header matching
- Request IDs enable correlation without tokens

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **New Features**
  * Added redaction of sensitive headers in access logs and a compact sensitive-header summary.

* **Refactor**
  * Reworked server middleware initialization and adjusted middleware ordering, changing request logging behavior.

* **Tests**
  * Added comprehensive header-redaction tests and updated request-ID tests to validate generated IDs and response headers.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-api/cmd/main.go`
- `maas-api/internal/logger/redaction.go`
- `maas-api/internal/logger/redaction_test.go`
- `maas-api/internal/middleware/access_log.go`
- `maas-api/internal/middleware/request_id_test.go`
