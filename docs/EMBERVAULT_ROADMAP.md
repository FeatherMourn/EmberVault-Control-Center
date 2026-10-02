# EmberVault Control Center Roadmap

This document is the staged development roadmap for EmberVault Control Center.
It is intentionally version-controlled with the project so the plan remains
available alongside the implementation.

## Development rule

Build modules as complete vertical slices:

```text
Contract
→ Safety boundary
→ Core service
→ Backend wiring
→ QML interface
→ Operation tracking
→ Recovery behavior
→ Tests
→ Catalog integration
→ Packaging
→ Documentation
```

The shared foundation should receive changes only when a real module exposes a
missing shared capability.

## Stage 1 — Foundation and architecture

Status: complete.

- Freeze terminology and naming.
- Define module boundaries.
- Establish the safety model.
- Define profiles and isolation rules.
- Define embedded versus separate-process behavior.
- Preserve the legacy EnshroudedModHub repository as reference material only.
- Define the Core contracts.

Exit criteria:

- Architecture and safety boundaries are documented.
- Legacy UI architecture is not reused.
- Module ownership and process boundaries are explicit.

## Stage 2 — EmberVault Core

Status: complete.

- Game detection.
- Application settings.
- Profiles.
- Compatibility checks.
- Structured logging.
- Operation tracking.
- Risk gates.
- Backup and recovery services.
- Module discovery.

Exit criteria:

- Core services operate independently of the UI.
- Operations are traceable.
- Profiles are isolated.
- Recovery behavior is testable.

## Stage 3 — Control Center shell

Status: complete.

- PySide6 desktop application.
- Qt Quick/QML shell.
- Navigation and Home dashboard.
- Activity history.
- Module registration.
- Embedded module support.
- Separate worker support.

Exit criteria:

- The application launches.
- QML loads successfully.
- Modules can register and appear.
- Separate workers can return results and terminate safely.

## Stage 4 — Save Manager

Status: complete.

- Save inspection.
- Verified backup creation.
- Backup re-verification.
- Restore preview.
- Safe restore.
- Recovery verification.
- Corruption and ownership safeguards.

First-release boundary: Save Manager does not directly edit save contents.

Exit criteria:

- Restore requires explicit confirmation.
- Recovery can be verified.
- No direct save editing exists.

## Stage 5 — Module framework standardization

Status: complete; maintain through module work.

- Standard module manifest.
- Standard module lifecycle.
- Standard operation and result formats.
- Capability states: stable, verified, experimental, research-only, blocked.
- Standard testing template.
- Standard catalog fields.

Exit criteria:

- A new module can be created from a documented template.
- Every module has a contract, safety boundary, tests, and UI registration path.

## Stage 6 — EML runtime adapter

Status: in progress.

- EML manifest and build compatibility.
- Explicit EML API version compatibility (`1.3` for the reviewed evidence).
- Supported field declarations.
- Research-profile gate.
- Verified-backup gate.
- Game-closed gate.
- Payload staging.
- Owned deployment.
- Runtime readback.
- Operation-bound runtime context evidence for loader, API, and game build.
- Rollback.
- Restart recovery.
- Catalog integration.

Next work:

- Test additional valid values.
- Test repeated launches.
- Test build mismatches.
- Expand rollback and failure evidence.
- Keep the adapter separate from general Game Settings.

The current supported route is limited to the evidenced `baseCritChance`
field and remains experimental.

## Stage 7 — Mods Management

Status: initial implementation complete; continue hardening.

- Folder and ZIP import.
- Manifest validation.
- Dependencies.
- Compatibility checks.
- Profile enablement.
- Deployment planning.
- Conflict detection.
- Ownership markers.
- Safe undeployment.
- External unmanaged-mod inspection.

Exit criteria:

- Unowned content is never overwritten or removed.
- Deployments are reversible.
- Profile isolation works.
- Failed deployments roll back safely.

## Stage 8 — Research and Development

Status: initial implementation complete; expand evidence workflows.

- Experiment records.
- Hypotheses.
- Build and version context.
- Evidence and reproduction steps.
- Failure records.
- Research-only profiles.
- Promotion reviews.
- Sanitized research exports.

Exit criteria:

- Experiments are reproducible or clearly documented as failed.
- Evidence can link to adapters, mods, and knowledge articles.

## Stage 9 — Knowledge Base

Status: initial implementation complete; expand authoring and linking.

- Articles.
- Categories and tags.
- Search.
- Cross-links.
- Draft and published states.
- Version history.
- Evidence references.
- Public export.

Exit criteria:

- Private notes remain separate from published knowledge.
- Articles can reference research and mod records.
- Public records contain no private paths or sensitive data.

## Stage 10 — Content Creator

Status: design-only implementation.

- Furniture projects.
- Asset references.
- Materials and dimensions.
- Recipes and registration plans.
- Compatibility notes.
- Design validation.
- Design-only exports.

First-release boundary: no direct live game mutation or untracked asset
injection.

## Stage 11 — Character tools

Status: plan-only implementation.

- Character profiles.
- Build goals.
- Progression plans.
- Equipment and skill notes.
- Backup associations.
- Validation.
- Plan exports.

Direct save mutation requires a separate evidence and safety review.

## Stage 12 — Trainer

Status: guarded, plan-oriented implementation.

- Trainer targets.
- Backup-bound sessions.
- Readiness checks.
- Separate-process execution.
- Timeout and crash handling.
- Operation tracking.
- Recovery instructions.

The first release remains read-only or plan-only.

## Stage 13 — EmberVault website and community platform

Status: separate web-repository workstream.

- Public mod catalog.
- Mod detail pages.
- Research archive.
- Knowledge base.
- Shared project pages.
- Forums.
- User accounts and roles.
- Moderation.
- Submission and review workflows.
- Catalog synchronization.

The desktop Control Center publishes sanitized records; it does not become the
entire community platform.

## Stage 14 — Cross-module integration

Connect modules through contracts rather than private implementation details.

Required relationships:

- Mods ↔ Profiles.
- Mods ↔ Compatibility.
- Research ↔ Knowledge.
- Research ↔ Runtime Adapters.
- Content Creator ↔ Research.
- Character Tools ↔ Save Manager.
- Trainer ↔ Save Manager.
- All modules ↔ Operations.
- All modules ↔ Catalog Export.

Every cross-module action should preserve an operation ID, profile ID,
capability state, and recovery expectation.

## Stage 15 — Release hardening

- Windows testing.
- Linux testing.
- Clean installation testing.
- Installed-wheel testing.
- QML smoke tests.
- Contract validation.
- Corrupt-data tests.
- Interrupted-operation tests.
- Rollback tests.
- Upgrade and migration tests.
- User and recovery documentation.
- Release notes.

Exit criteria:

- Fresh installs work.
- Existing user data migrates safely.
- Packaging and CI are green.
- Release assets validate.

## Stage 16 — Capability promotion

Capabilities move through:

```text
Research-only
→ Experimental
→ Verified
→ Stable
```

Promotion requires current-build evidence, reproducibility, runtime
confirmation, recovery testing, compatibility documentation, clear ownership,
and rollback behavior.

## Recommended execution order from the current baseline

1. Finish and reuse the module-development template.
2. Continue EML adapter evidence and compatibility testing.
3. Harden Mods Management.
4. Expand Research and Evidence workflows.
5. Improve the Knowledge Base.
6. Build Content Creator design tools.
7. Expand Character planning.
8. Harden Trainer isolation.
9. Continue the EmberVault website/community platform.
10. Add cross-module integration.
11. Perform final release hardening.
12. Promote proven capabilities.
