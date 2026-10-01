# Ember Vault catalog integration

The Control Center is the local authoring and safety surface. The Ember Vault
website can consume the exported catalog without importing desktop runtime
state.

`CatalogExportService` writes a JSON document with:

- `schema_version`
- `contract_versions` for module and package manifests
- package manifests
- module manifests
- knowledge entries
- sanitized research summaries with evidence counts (never local evidence text
  or profile identifiers)

Paths are deliberately removed from exported records. Runtime folders,
profiles, save backups, logs, and research-local evidence are not published by
this export. The canonical validation document is
`contracts/catalog.schema.json`; package and module entries use the contract
versions declared in the export. A future website synchronizer can validate
the catalog before attaching repository URLs, discussion links, and moderation
metadata on the web side.

Guarded workers must return JSON with `contract_version: 1` and
`read_only: true`. Control Center rejects successful processes that do not
provide that contract, preserving the first-release mutation boundary. The
canonical result schema is `contracts/worker-result.schema.json`. Research
workers may additionally return a bounded `evidence` string array containing
observations; these observations must be read-only and are captured in the
operation log rather than written into game or save data.
Trainer workers may additionally return a bounded `checks` string array for a
readiness audit. The backup identifier is passed as context only; the worker
cannot mutate or restore it.
Content Creator workers may also return bounded `checks` describing their
design-workspace boundary; they must not touch live game content.
