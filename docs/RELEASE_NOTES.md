# Embervault Control Center 0.1.0

## Included

- PySide6 and Qt Quick/QML desktop shell.
- Core game detection, settings, profiles, compatibility, logs, operations,
  and recovery services.
- Save Manager inspection, verified backup, re-verification, restore preview,
  safe restore, and post-restore verification.
- Profile-scoped package discovery, folder/ZIP import, enablement, compatibility
  diagnostics, and safe removal.
- Staged Game Settings, Troubleshooter, Character projects, Research records
  with evidence lifecycle, Content projects, Knowledge search, and public
  catalog export.
- Guarded separate-process contracts for Trainer, Research, and Content Creator.

## Important limitations

- Save Manager does not edit save contents.
- Staged Game Settings are not applied directly to a live game.
- Character and Content projects are planning metadata, not live mutations.
- High-risk worker processes are non-mutating contract stubs in this release.
- Website synchronization, forums, moderation, and hosted databases consume the
  catalog export but are not implemented in this desktop repository.

## Verification

The release baseline includes the Python unit suite, Python compilation, an
offscreen QML load check, wheel construction, and isolated installed-prefix
smoke testing.
