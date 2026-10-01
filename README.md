# Embervault Control Center

The new modular desktop platform for managing, testing, and safely operating
Enshrouded mods and Embervault packages.

This repository is being built from a clean architecture. The prior
`EnshroudedModHub` repository remains available as a reference source for
research, evidence, and selected proven service concepts.

## Current status

The first working vertical slice is in place. The Control Center currently
includes Home, Profiles, Save Manager safety workflows, profile-scoped package
management, staged Game Settings, read-only Troubleshooter diagnostics, a safe
Character Editor project layer, isolated Research records, and a local
Knowledge catalog.

Read:

- [Architecture](docs/ARCHITECTURE.md)
- [Stage 0 Contracts](docs/STAGE_0_CONTRACTS.md)
- [Legacy Migration Inventory](docs/MIGRATION_INVENTORY.md)
- [User Guide](docs/USER_GUIDE.md)
- [Release Checklist](docs/RELEASE_CHECKLIST.md)
- [Roadmap Status](docs/ROADMAP_STATUS.md)
- [Release Notes](docs/RELEASE_NOTES.md)

## Safety boundaries

Save Manager is inspection, backup, verification, restore preview, and safe
restore only. It does not directly edit save contents. Gameplay tuning and
higher-risk tools remain separate from normal embedded workflows and must use
explicit profiles, operation tracking, and recovery evidence.

## Development checks

Run the test suite with `python -m unittest discover -s tests -p "test*.py"`.
The QML shell can be smoke-tested with an offscreen Qt application after
installing the project dependencies.
