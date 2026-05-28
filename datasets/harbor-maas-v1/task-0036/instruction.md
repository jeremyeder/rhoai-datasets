# chore: update llm-katan simulator endpoint to new AWS instance

## Summary
- Migrate llm-katan simulator endpoint from `3-13-21-181.sslip.io` to `3-147-232-199.sslip.io` (new AWS account)
- Same llm-katan version (0.15.3), same configuration, lifetime stats preserved

## Files changed
- `test/e2e/scripts/local-deploy.sh` — default `LLM_KATAN_FQDN`
- `test/e2e/scripts/LOCAL-DEPLOY.md` — documentation reference

## Test plan
- [x] New endpoint verified: health, all 5 providers, tool calling, streaming, auth, stats, dashboard
- [x] TLS cert valid (Let's Encrypt via sslip.io)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Updated external model endpoint configuration in deployment guide.

* **Tests**
  * Added new authentication enforcement tests for external models to verify proper authorization requirements are applied.

* **Chores**
  * Updated default endpoint configuration in deployment script.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `test/e2e/scripts/LOCAL-DEPLOY.md`
- `test/e2e/scripts/local-deploy.sh`
