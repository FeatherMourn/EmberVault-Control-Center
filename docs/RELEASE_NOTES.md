# Embervault Control Center 0.1.0

## Included

- PySide6 and Qt Quick/QML desktop shell.
- Core game detection, settings, profiles, compatibility, logs, operations,
  and recovery services.
- Save Manager inspection, verified backup, re-verification, restore preview,
  safe restore, and post-restore verification.
- Profile-scoped package discovery, folder/ZIP import, enablement, compatibility
  diagnostics, dependency-aware enablement, and safe removal.
- Staged Game Settings, Troubleshooter, Character projects, Research records
  with evidence lifecycle, Content projects, Knowledge search, and public
  catalog export.
- Guarded separate-process contracts for Trainer, Research, and Content Creator.

## Important limitations

- Save Manager does not edit save contents.
- Staged Game Settings are not applied directly to a live game.
- Character and Content projects are planning metadata, not live mutations.
- High-risk worker processes are non-mutating contract stubs in this release.
  They can be launched from eligible profiles, report captured output, and are
  terminated and audited if they exceed the worker timeout.
- Website synchronization, forums, moderation, and hosted databases consume the
  catalog export but are not implemented in this desktop repository.

## Compatibility and isolation

- There is no hard-coded supported Enshrouded build range in 0.1.0. Packages
  declare the builds they have tested; the Control Center reports unknown,
  compatible, or incompatible status and blocks known-incompatible enablement.
- Normal package and settings workflows are embedded. Trainer, Research, and
  Content Creator use guarded separate-process contracts; their included
  workers are non-mutating reference stubs.
- Verified backups are stored under the runtime data directory in the Save
  Manager backup area. Restore requires a current-state backup and performs
  post-restore verification.

## Verification

The release baseline includes the Python unit suite, Python compilation, an
offscreen QML load check, wheel construction, and isolated installed-prefix
smoke testing.
