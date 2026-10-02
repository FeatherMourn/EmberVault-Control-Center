# EmberVault platform evolution roadmap

This roadmap describes the platform capabilities that can supersede the current
module-by-module design while preserving Control Center as the policy, safety,
state, and orchestration authority.

## Core platform engines

### 1. Unified operation engine

All modules use the same lifecycle:

`Draft → Review → Approve → Execute → Verify → Recover`

This applies to installs, backups, restores, tuning plans, research runs,
content exports, migrations, and updates.

### 2. Capability and permission engine

Modules declare individual capabilities such as reading saves, creating backups,
deploying packages, launching workers, exporting evidence, or applying adapters.
Each capability declares risk, permissions, profile restrictions, backup needs,
reversibility, and evidence requirements.

### 3. Dependency and compatibility graph

Connect modules, packages, contracts, game builds, loader versions, adapters,
research evidence, knowledge entries, and profiles. Use the graph to explain
compatibility, update impact, dependency chains, and evidence relationships.

### 4. Transactional change system

Every write operation must snapshot or back up state, stage changes, validate
ownership and compatibility, show a preview, apply changes, verify results, and
automatically roll back on failure.

### 5. Safe mode and recovery center

Provide a startup mode that disables third-party modules, loads a temporary
profile, preserves logs, repairs invalid manifests, and supports rollback.

## Evidence, trust, and knowledge

### 6. Provenance system

Records should identify their creator, source, timestamp, game build, tool version,
supporting evidence, verification state, and promotion history.

### 7. Evidence state vocabulary

Use explicit states: Observed, Reproduced, Inferred, Experimental, Verified,
Promoted, Unsupported, and Superseded.

### 8. Knowledge graph website

Connect game builds to research records, runtime evidence, packages,
compatibility results, knowledge entries, and Control Center capabilities.

### 9. Trust and privacy controls

Give users control over what leaves the machine, what is published, what is
shared, whether telemetry is enabled, and how private paths and evidence are
sanitized.

## Extensibility and release maturity

### 10. Community marketplace contract

Define publisher identity, signatures, version history, dependencies,
compatibility ranges, permissions, security review, community reports, trust
levels, and deprecation state for community packages.

### 11. Capability promotion lifecycle

Support Hidden, Experimental, Research-only, Preview, Community-tested, Stable,
Deprecated, and Blocked states.

### 12. Feature flags and automation policies

Allow advanced users to automate checks, backups, scans, and reports while
requiring explicit approval for changes unless a clearly defined policy permits
otherwise.

### 13. Test laboratory

Create disposable environments for clean profiles, broken manifests, conflicts,
interrupted deployments, corrupt backups, failed workers, failed updates, loader
changes, and migration failures. Link generated evidence to research and release
records.

### 14. Module governance

Every module should maintain a contract, threat model, compatibility policy,
recovery policy, test plan, release checklist, deprecation policy, and support
status.

## Target architecture

```text
Control Center Shell
├── Operation Engine
├── Capability and Permission Engine
├── Compatibility Engine
├── Dependency Graph
├── Backup and Recovery Engine
├── Update and Distribution Engine
├── Evidence and Provenance Engine
├── Module Registry
├── Profile Manager
└── UI and Workflow Layer
```

Modules provide specialized capabilities; Control Center owns policy, safety,
state, history, and orchestration.

## Recommended implementation order

1. Unified operation engine.
2. Capability and permission model.
3. Dependency and compatibility graph.
4. Safe mode and automatic rollback.
5. Provenance and evidence tracking.
6. Mod Manager expansion.
7. Test laboratory.
8. Update system.
9. Knowledge graph website.
10. Feature promotion lifecycle.

## Design principle

Make simple tasks effortless, advanced tasks inspectable, experimental tasks
isolated, and every change reversible.
