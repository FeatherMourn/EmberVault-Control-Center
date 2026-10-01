# Roadmap status

## Working

- Core composition, settings, game detection, profiles, structured logs, and
  operation tracking.
- Save Manager inspection, verified backup, re-verification, restore preview,
  safe restore, and post-restore verification.
- Contract-discovered embedded/separate module framework.
- PySide6/Qt Quick shell with Home, Profiles, Mods, Game Settings,
  Troubleshooter, Character Editor, Trainer, Content Studio, Research Lab,
  Knowledge, Modules, and Activity workspaces.
- Profile-scoped package discovery, folder/ZIP import, enablement, compatibility
  reporting, and safe removal.
- Isolated research records/evidence, character projects, content projects, and
  versioned public catalog export.
- Guarded Trainer, Research, and Content Creator process workflows with UI
  launch controls, captured worker output, timeout termination, and audited
  results. Current workers are deliberately non-mutating; Research includes a
  bounded evidence probe while Trainer and Content Creator remain stubs.

## Guarded or incomplete

- Gameplay settings are validated, profile-scoped staged values and can be
  exported as a portable manifest; applying them to a live game is not
  implemented.
- Character projects can be exported as plan-only manifests; content projects
  can be exported as design-only manifests, while direct game mutation is not
  implemented.
- Website synchronization, community forums, moderation, and remote catalog
  hosting are outside the desktop repository and use the export contract.
- The seeded Trainer and Content Creator workers prove process isolation and
  argument handoff. The Research worker additionally performs a bounded,
  read-only filesystem observation probe; production Trainer and Content Creator
  behavior is not implemented. Worker launch paths are covered by success,
  denial, and timeout tests.

## Release evidence

- Python unit suite currently covers the Core services, workflows, module gates,
  profile isolation, package contracts, packaging assets, and installed-process
  contracts (132 tests).
- QML is smoke-tested through an offscreen Qt application.
- Wheels have been built and installed into isolated temporary targets; the
  packaged launcher passes its offscreen smoke test and discovers four modules,
  one seed package, and three knowledge entries. The package-manifest schema is
  present in the installed wheel data.
- Save Manager remains inspection/backup/verification/restore-only.
