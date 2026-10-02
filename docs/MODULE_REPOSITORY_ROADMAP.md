# EmberVault repository-module roadmap

This document maps the repositories that make up the EmberVault Control Center
ecosystem. The Control Center remains the central authority; modules remain
independently packaged, contract-based, and replaceable.

## Foundation repositories

1. **EmberVault-Control-Center** — desktop shell, registry, navigation, profiles,
   safety gates, operations, notifications, and orchestration.
2. **EmberVault-Contracts** — shared manifests, schemas, capability definitions,
   package contracts, and integration records.
3. **EmberVault-Module-SDK** — lifecycle interfaces, module context, result
   contracts, worker communication, and module templates.

## Core modules

4. **EmberVault-Character-Tools** — character planning, progression, equipment,
   builds, and skills.
5. **EmberVault-Mod-Manager** — external mod installation, packages, profiles,
   dependencies, compatibility, load-order planning, and updates.
6. **EmberVault-Save-Manager** — inspection, verified backups, restore previews,
   recovery, migration, and rollback.
7. **EmberVault-Game-Tuning** — staged gameplay-setting plans and adapter records.
8. **EmberVault-TroubleShooter** — diagnostics, compatibility scans, recovery
   guidance, and evidence collection.

## Experimental and research modules

9. **EmberVault-Mod-Research** — experiments, runtime evidence, comparisons,
   build tracking, and reproducibility.
10. **EmberVault-Trainer** — isolated research plans, verified-backup gates, and
    recovery simulation.
11. **EmberVault-Content-Creator** — furniture, building, recipe, asset, material,
    and design projects; design-only until explicitly promoted.

## Public and integration repositories

12. **EmberVault-Web** — public catalog, research archive, knowledge base,
    submissions, and community-facing records.
13. **Runtime Evidence Adapter** — loader/runtime evidence collection boundary.
14. **EML adapter** — initial loader and tuning integration support.
15. **Shroudtopia adapter** — future loader support behind the adapter contract.

## Development order

1. Stabilize Contracts and Module SDK.
2. Expand the Control Center registry and lifecycle.
3. Expand Mod Manager.
4. Complete Save Manager recovery workflows.
5. Expand Character Tools.
6. Expand Troubleshooter diagnostics.
7. Expand Game Tuning staged workflows.
8. Expand Research evidence workflows.
9. Expand Content Creator design workflows.
10. Expand Trainer isolation and recovery simulation.
11. Synchronize the website and knowledge base.
12. Implement runtime adapters.
13. Repair Windows desktop packaging.
14. Implement distribution and update services.
15. Complete stable public release.

## Boundary rules

- Lower-risk tools may render inside Control Center.
- Higher-risk or independent features use separate processes.
- Modules must not bypass Control Center safety, profile, backup, or compatibility gates.
- Experimental modules remain isolated from stable release channels.
- Public exports must exclude profiles, save paths, private evidence, credentials,
  and operation logs.
