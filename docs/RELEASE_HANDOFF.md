# EmberVault release handoff

## Automated status

The current release candidate has passed the unified readiness gate:

- Full test suite
- Python compilation
- Wheel asset verification
- Windows and Linux bundle verification
- Bundle hash and safety audit
- Public catalog validation

## Human release steps

1. Install the reviewed wheel or portable bundle on a clean machine or clean
   test workspace.
2. Complete [`USER_ACCEPTANCE.md`](USER_ACCEPTANCE.md), recording the build,
   platform, tester, and any failed or blocked action.
3. In `EmberVault-Web`, open repository Settings → Pages and choose **GitHub
   Actions** as the source.
4. Confirm the Pages workflow completes after the next `main` push.
5. Open the deployed catalog and verify modules, packages, research, knowledge,
   and content records are visible without private workspace data.
6. Record the deployed URL and the SHA-256 hashes of the reviewed Windows and
   Linux bundles in the release notes.
7. Publish only after the acceptance checklist and deployment review are both
   complete.

## Release boundary

This release candidate does not claim unsupported live gameplay mutation.
Experimental, research-only, and backup-gated capabilities remain labeled and
must not be promoted solely because packaging or offline tests succeed.
