# chore: fix CI failures

<!--- Provide a general summary of your changes in the Title above -->

## Description
With recent merges, the CI seems to have started failing. Somehow, the issues were not detected before merging the changes.

## How Has This Been Tested?
* `make build` for both maas-api and maas-controller

## Merge criteria:
<!--- This PR will be merged by any repository approver when it meets all the points in the checklist -->
<!--- Go over all the following points, and put an `x` in all the boxes that apply. -->

- [x] The commits are squashed in a cohesive manner and have meaningful messages.
- [x] Testing instructions have been added in the PR body (for PRs involving changes that are not immediately obvious).
- [x] The developer has manually tested the changes and verified that the changes work


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Bug Fixes**
  * Fixed an issue preventing proper recognition of managed external models.

* **Tests**
  * Updated test validation to ensure accurate data handling.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Files involved
- `maas-api/internal/handlers/models_test.go`
- `maas-controller/pkg/reconciler/externalmodel/reconciler.go`
