# EmberVault Control Center release checklist

## Before packaging

- [x] Run the complete Python test suite (193 tests passing).
- [x] Run the same test, QML smoke, wheel, and asset-verification gates in
      GitHub Actions (`.github/workflows/ci.yml`).
- [x] Upload the verified wheel as a CI artifact for review.
- [x] Smoke-test the installed wheel outside the source tree in CI.
- [x] Run native Windows installation, compilation, tests, and QML smoke checks
      in CI.
- [x] Compile all Python packages with `py_compile`.
- [x] Load `ui/Main.qml` through an offscreen Qt application.
- [x] Confirm Save Manager never performs direct save editing.
- [x] Confirm stable and research profiles remain separate.
- [x] Confirm malformed manifests and corrupt local records fail safely.
- [x] Review operation and structured-log output for a backup and restore preview.
- [x] Confirm staged Game Settings schema is included in the wheel data.
- [x] Confirm gameplay tuning adapter schema is included in the wheel data.
- [x] Confirm character-plan and content-project schemas are included in the wheel data.
- [x] Confirm trainer-plan schema is included in the wheel data.
- [x] Review the frozen vocabulary in `docs/TERMINOLOGY.md`.
- [x] Review embedded and separate-process boundaries in
      `docs/MODULE_BOUNDARIES.md`.

## Packaging

- [x] Build a wheel from `pyproject.toml`.
- [x] Run `python tools/verify_release.py <wheel>` against the built wheel.
- [x] Verify the `embervault` entry point launches the desktop shell through
      the application entry point with the offscreen Qt platform.
- [x] Bundle the QML UI, contracts, seeded knowledge, and module manifests.
- [x] `pyproject.toml` declares the QML UI, contracts, knowledge, and sample manifests as wheel data files.
- [x] Test from a clean environment with an empty runtime-data directory. The
      installed wheel discovers five modules, one seed package, and eight
      knowledge entries without source-tree assets.

## Release notes

- [x] State which modules are embedded and which require a separate process.
- [x] State the compatibility policy: 0.1.0 has no hard-coded build range;
      packages declare tested builds and known incompatibilities are blocked.
- [x] State that Trainer, Research, and Content Creator capabilities are guarded
      and may require separate-process isolation.
- [x] Include recovery instructions and the location of verified backups.
