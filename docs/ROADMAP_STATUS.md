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
  reporting, safe removal, conflict-free deployment, and ownership-protected
  undeploy, plus read-only inspection of existing external `mod.json` mods.
- Isolated research records/evidence, character projects, content projects, and
  versioned public catalog export.
- Guarded Trainer, Research, and Content Creator process workflows with UI
  launch controls, captured worker output, timeout termination, and audited
  results. Current workers are deliberately non-mutating; Research includes a
  bounded evidence probe, Trainer includes a readiness audit, and Content
  Creator includes a design-boundary audit.

## Guarded or incomplete

- Gameplay settings are validated, profile-scoped staged values and can be
  exported as a portable manifest; applying them to a live game is not
  implemented. The supported boundary and observed installation evidence are
  documented in `docs/GAME_SETTINGS_BOUNDARY.md`.
- Character projects can be exported as plan-only manifests; content projects
  can be exported as design-only manifests, while direct game mutation is not
  implemented.
- Website synchronization, community forums, moderation, and remote catalog
  hosting are outside the desktop repository and use the export contract.
- The seeded Trainer performs a bounded, read-only readiness audit; the Research
  worker performs a bounded filesystem observation probe; and Content Creator
  performs a bounded design-boundary audit. The tuning-audit worker performs a
  bounded review of staged settings without applying them to the game. Worker
  launch paths are covered by success, denial, and timeout tests.

## Release evidence

- Python unit suite currently covers the Core services, workflows, module gates,
  profile isolation, package contracts, packaging assets, and installed-process
  contracts (162 tests).
- QML is smoke-tested through an offscreen Qt application.
- Wheels have been built and installed into isolated temporary targets; the
  packaged launcher passes its offscreen smoke test and discovers five modules,
  one seed package, and three knowledge entries. The package-manifest schema is
  present in the installed wheel data.
- Save Manager remains inspection/backup/verification/restore-only.
