# feat(maas-api): enable TLS certificate validation for internal gateway calls

<!--- Provide a general summary of your changes in the Title above -->

## Description
This PR fixes the TLS certificate validation issue in the maas-api service where InsecureSkipVerify: true was used for internal gateway calls, bypassing FIPS-certified certificate validation.

**Issue:** The HTTP client used for model discovery/access validation (probing model endpoints to check user access) had TLS certificate verification disabled. This was flagged as [FIPS-001](https://redhat.atlassian.net/browse/FIPS-001) violation during security scanning.

**Before:**
```
TLSClientConfig: &tls.Config{InsecureSkipVerify: true}, //nolint:gosec // cluster-internal only
```
**After:**
```
TLSClientConfig: tlsConfig, // Uses K8s service account CA or system root CAs
```

https://redhat.atlassian.net/browse/RHOAIENG-47769

## How Has This Been Tested?
* Unit Tests 
* Manual Cluster Testing:
  * Built and pushed test image: quay.io/isequeir/maas-api:tls-fix-amd64
  * Deployed to OpenShift cluster in opendatahub namespace
  * Verified pod starts successfully with debug logging enabled
  * Made authenticated requests to /v1/models endpoint
  * Verified HTTPS connections to model endpoints complete successfully (received HTTP 403 auth response, not TLS errors)

  * Confirmed TLS CA loading via log message:
```
  Using Kubernetes service account CA for TLS validation {"path": "/var/run/secrets/kubernetes.io/serviceaccount/ca.crt"}
```
<!--- Please describe in detail how you tested your changes. -->
<!--- Include details of your testing environment, and the tests you ran to -->
<!--- see how your change affects other areas of the code, etc. -->

## Merge criteria:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Bug Fixes**
  * Enforced secure TLS for cluster probes: removed insecure defaults, require TLS 1.2+, prefer the in-cluster service account CA when available, fall back to system roots, and fail initialization if a present cluster CA cannot be parsed. Added debug logging indicating which CA pool was used.

* **Tests**
  * Added tests covering manager initialization and TLS configuration behaviors.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-api/internal/models/discovery.go`
- `maas-api/internal/models/discovery_test.go`
