# EmberVault advanced capabilities roadmap

This roadmap extends the product and platform plans with capabilities that make
EmberVault more useful, explainable, accessible, collaborative, and resilient.

## User experience and workflows

1. **Command palette** — searchable actions for backups, packages, profiles,
   diagnostics, research, recovery, and updates.
2. **Guided workflow engine** — reusable `Review → Confirm → Execute → Verify →
   Recover` flows shared by every module.
3. **Simulation mode** — preview files, package changes, conflicts, backups, and
   rollback steps before applying an operation.
4. **Visual workflow builder** — let advanced users assemble safe workflows while
   Control Center enforces all capability gates.
5. **Accessibility** — keyboard navigation, screen-reader labels, high contrast,
   adjustable text, reduced motion, and non-color warning indicators.

## Data and workspace architecture

6. **Local-first database** — use a local database such as SQLite for indexed,
   versioned records while preserving JSON export/import.
7. **Workspace system** — isolate stable gameplay, research, content creation,
   multiplayer testing, and modpack development into separate workspaces.
8. **Visual comparison tools** — compare profiles, packages, backups, research,
   configuration plans, and compatibility records.
9. **Capability registry** — one authoritative registry for capability IDs,
   owning modules, schemas, risk, UI surfaces, recovery, and promotion state.
10. **Schema and deprecation management** — preserve old records, explain
    replacements, and provide safe migrations.

## Diagnostics, recovery, and reliability

11. **Sanitized support bundles** — export versions, module health, compatibility,
    operation summaries, and errors without private data.
12. **Environment detection** — inspect Steam paths, game build, loaders, mod
    folders, conflicting tools, permissions, and disk space read-only.
13. **Module health monitor** — track contracts, dependencies, workers, schemas,
    recovery paths, operations, and failures.
14. **Recovery rehearsal** — test backup restoration and repair in disposable
    workspaces without touching the real environment.
15. **Reliability engineering** — add lazy loading, cancellable operations,
    progress reporting, retries, resource limits, crash isolation, and large-
    library testing.

## Automation and integration

16. **CLI and automation API** — expose safe status, backup, module, package,
    research, and update commands for scripts and CI.
17. **Offline collaboration bundles** — exchange signed research, metadata,
    compatibility, and knowledge records without exposing private workspaces.
18. **Release channels** — support Nightly, Experimental, Preview, Stable, and
    Long-Term Support channels with module-specific compatibility rules.
19. **Optional local assistance** — explain errors, summarize research, suggest
    diagnostics, and draft documentation without silently changing files or
    promoting unsupported claims.

## Trust and quality

20. **Package trust system** — distinguish Official, Verified Publisher,
    Community-reviewed, Experimental, Unreviewed, Blocked, and Deprecated.
21. **Quality scoring** — score compatibility, evidence, maintenance,
    documentation, safety, reproducibility, and community review separately.
22. **Evidence-aware promotion** — connect quality and provenance to the
    capability promotion lifecycle.

## Priority order

1. Local-first database and workspace model.
2. Command palette and guided workflows.
3. Visual diff and simulation mode.
4. Environment detection.
5. Sanitized support bundles.
6. Module health monitoring.
7. CLI and automation API.
8. Recovery rehearsal.
9. Trust and release channels.
10. Offline collaboration bundles.

## Design objective

Make EmberVault a platform for safe, explainable operations rather than merely a
launcher with modules.
