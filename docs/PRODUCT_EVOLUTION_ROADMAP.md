# EmberVault product evolution roadmap

This roadmap turns the existing technical foundation into a safer, easier, and
more advanced product without weakening Control Center authority or module
isolation.

## Experience modes

### Beginner mode

- Guided first launch and game-folder detection.
- Plain-language explanations and safe defaults.
- Recommended actions and no unnecessary experimental controls.

### Standard mode

- Profiles, packages, backups, diagnostics, tuning plans, and deployment review.
- Full everyday workflows without exposing internal research complexity.

### Advanced mode

- Runtime evidence, adapter workflows, experimental modules, package manifests,
  logs, schemas, compatibility details, and research tools.

## Home command center

The Home screen should show the active profile, game-installation status, backup
health, installed and outdated modules, pending package changes, compatibility
warnings, recovery state, experimental warnings, and the recommended next action.

Primary workflows should use the same sequence:

`Review → Confirm → Execute → Verify → Recover if needed`

Initial guided workflows are install a mod, create a backup, enable a package,
diagnose a problem, restore a save, create a research experiment, and prepare a
content project.

## Shared advanced platform services

- Unified operation history and structured notifications.
- Universal preview-before-change system.
- Compatibility engine and dependency graph.
- Package ownership tracking.
- Versioned schemas and migration handlers.
- Update manager, rollback engine, and repair center.
- Capability and permission system.
- Evidence and provenance tracking.
- Module health monitoring.

## Capability and permission model

Every module action must declare whether it is read-only or a write operation,
which files it affects, its required profile, backup requirement, process mode,
reversibility, evidence requirement, and compatibility range. Control Center
then classifies the action as allowed, backup-gated, research-only, review-required,
or blocked.

## Mod Manager priority

Mod Manager is the next major everyday module. Its advanced scope includes package
discovery, install/update/disable/remove, dependency resolution, conflict
detection, load-order planning, profile-specific state, deployment previews,
ownership tracking, rollback, broken-install repair, compatibility reports, and
update notifications.

## Shared module event system

Modules should emit structured events such as `backup.created`, `package.staged`,
`package.enabled`, `deployment.previewed`, `deployment.blocked`, `research.started`,
`module.updated`, and `recovery.restored`. Control Center uses these events for
notifications, activity history, diagnostics, and audit trails.

## Module maturity model

1. Read-only inspection.
2. Planning and preview.
3. Verified backup and staged change.
4. Explicit user-approved deployment.
5. Automated recovery and rollback.
6. Experimental adapter support.
7. Evidence-backed stable promotion.

Features must not jump directly from research to live mutation.

## Development order

1. Finish Windows packaging repair.
2. Define the unified capability and operation model.
3. Improve onboarding and the Home dashboard.
4. Expand Mod Manager.
5. Add universal preview and deployment workflows.
6. Add update discovery and staged updates.
7. Improve recovery and repair workflows.
8. Add Advanced mode and research tooling.
9. Add module health, diagnostics, and dependency visualization.
10. Conduct structured user testing.
11. Promote only verified capabilities to Stable.
