# fix: scale down kserve-controller-manager to prevent crash-loop on Kind

## Summary
- The opendatahub fork `kserve-controller` image watches `Route.route.openshift.io` for `InferenceGraph`, which crash-loops on non-OpenShift clusters (Kind) even with stub CRDs installed.
- Scale `kserve-controller-manager` to 0 replicas instead of swapping its image to the ODH fork. The vanilla KServe install still provides CRDs, RBAC, and webhook configs.
- `LLMInferenceService` reconciliation is handled by the separate `llmisvc-controller-manager`, which runs fine on Kind.

## Test plan
- [ ] Run `local-deploy.sh` on a fresh Kind cluster and verify no pods are in CrashLoopBackOff
- [ ] Verify `llmisvc-controller-manager` is 1/1 Ready and handles LLMInferenceService resources
- [ ] Verify smoke test passes end-to-end

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Chores**
  * Updated test deployment script to simplify KServe controller initialization. The deployment process no longer uses a custom controller image and instead delegates inference service handling to a separate manager component.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `test/e2e/scripts/local-deploy.sh`
