# chore: promote stable to rhoai

Automated promotion of **3 commit(s)** from `stable` to `rhoai`.

```
f644b8f fix(kustomize): restore cleanup CronJob image replacement dropped by Tenant refactor (#792)
047eb06 feat: local Kind deployment for MaaS + BBR development (#775)
```


## Files involved
- `deployment/components/shared-patches/kustomization.yaml`
- `maas-controller/pkg/platform/tenantreconcile/constants.go`
- `test/e2e/scripts/LOCAL-DEPLOY.md`
- `test/e2e/scripts/local-demo.sh`
- `test/e2e/scripts/local-deploy.sh`
- `test/e2e/scripts/local-test.sh`
