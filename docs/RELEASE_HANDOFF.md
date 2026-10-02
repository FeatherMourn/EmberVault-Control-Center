# EmberVault release handoff

## Automated status

The current release candidate has passed the unified readiness gate:

- Full test suite
- Python compilation
- Wheel asset verification
- Windows and Linux bundle verification
- Bundle hash and safety audit
- Public catalog validation
- GitHub Pages deployment completed successfully.
- Deployed catalog: https://feathermourn.github.io/EmberVault-Web/

## Human release steps

1. Install the reviewed wheel or portable bundle on a clean machine or clean
   test workspace.
2. Complete [`USER_ACCEPTANCE.md`](USER_ACCEPTANCE.md), recording the build,
   platform, tester, and any failed or blocked action.
3. Open the deployed catalog and verify modules, packages, research, knowledge,
   and content records are visible without private workspace data.
4. Record the SHA-256 hashes of the reviewed artifacts:
   - `embervault_control_center-1.0.0rc1-py3-none-any.whl`: `81820D03CD8D65D8AFE1C97D26EEA9B81FC27468B57696D0E32BB0F4009F8EA6`
   - `embervault-control-center-1.0.0rc1-windows.zip`: `E362FCAE118DF7CF74CB7314C17F84F85195D83931951BEC87005285BF9CBBE4`
   - `embervault-control-center-1.0.0rc1-linux.zip`: `F052933186EFCBFF35186CA9B794672DF8A0E4E8CD831F606CBE4D07211BFC46`
5. Publish only after the acceptance checklist and deployment review are both
   complete.

## Release boundary

This release candidate does not claim unsupported live gameplay mutation.
Experimental, research-only, and backup-gated capabilities remain labeled and
must not be promoted solely because packaging or offline tests succeed.
