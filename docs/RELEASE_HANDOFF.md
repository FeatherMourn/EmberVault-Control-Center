# EmberVault release handoff

## Automated status

The current stabilization revision has passed the repository-level readiness checks:

- Full test suite
- 300 automated tests passing, with two display-dependent GUI tests skipped when no Qt display is available
- Python compilation
- Wheel asset verification
- Windows and Linux bundle verification
- Bundle hash and safety audit
- Public catalog validation
- Signed Windows artifact generation and public-key verification
- Isolated Windows update replacement and rollback rehearsal
- Steam multi-library discovery and explicit selection coverage
- Save and package deployment recovery simulations

## Human release steps

1. Install the reviewed wheel or portable bundle on a clean machine or clean
   test workspace.
2. Complete [`USER_ACCEPTANCE.md`](USER_ACCEPTANCE.md), recording the build,
   platform, tester, and any failed or blocked action.
3. Open the deployed catalog, when the hosted website is available, and verify
   public records contain no private workspace data.
4. Run the manual signed-release workflow after configuring the production
   signing secrets, then record the generated artifact hashes in this handoff.
5. Publish only after the acceptance checklist and deployment review are both
   complete.

## Release boundary

This release candidate does not claim unsupported live gameplay mutation.
Experimental, research-only, and backup-gated capabilities remain labeled and
must not be promoted solely because packaging or offline tests succeed.
