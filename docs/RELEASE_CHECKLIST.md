# Embervault Control Center release checklist

## Before packaging

- [ ] Run the complete Python test suite.
- [ ] Compile all Python packages with `py_compile`.
- [ ] Load `ui/Main.qml` through an offscreen Qt application.
- [ ] Confirm Save Manager never performs direct save editing.
- [ ] Confirm stable and research profiles remain separate.
- [ ] Confirm malformed manifests and corrupt local records fail safely.
- [ ] Review operation and structured-log output for a backup and restore preview.

## Packaging

- [x] Build a wheel from `pyproject.toml`.
- [ ] Verify the `embervault` entry point launches the desktop shell.
- [ ] Bundle the QML UI, contracts, seeded knowledge, and module manifests.
- [x] `pyproject.toml` declares the QML UI, contracts, knowledge, and sample manifests as wheel data files.
- [x] Test from a clean environment with an empty runtime-data directory. The
      installed wheel discovers four modules, one seed package, and three
      knowledge entries without source-tree assets.

## Release notes

- [ ] State which modules are embedded and which require a separate process.
- [ ] State the supported Enshrouded build range.
- [ ] State that Trainer, Research, and Content Creator capabilities are guarded
      and may require separate-process isolation.
- [ ] Include recovery instructions and the location of verified backups.
