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
- explicitly published, sanitized research summaries with evidence counts and
  publication timestamps (never local evidence text or profile identifiers)
  and can be explicitly unpublished without deleting the local record. Changes
  to published evidence or status automatically retract publication.
- explicitly published, sanitized Content project summaries for projects marked
  ready (never local descriptions, profiles, or design-workspace details). A
  project can be unpublished without deleting its local design record, and any
  status change automatically retracts publication.

Paths are deliberately removed from exported records. Runtime folders,
profiles, save backups, logs, and research-local evidence are not published by
this export. The canonical validation document is
`contracts/catalog.schema.json`; package and module entries use the contract
versions declared in the export. A future website synchronizer can validate
the catalog before attaching repository URLs, discussion links, and moderation
metadata on the web side.

The desktop exporter validates the handoff before writing it. Malformed public
records are rejected, and research or content records containing private
evidence, descriptions, profiles, or other local-only fields cannot be
exported as public catalog entries.

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
