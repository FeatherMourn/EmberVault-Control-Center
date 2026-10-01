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

Paths are deliberately removed from exported records. Runtime folders,
profiles, save backups, logs, and research-local evidence are not published by
this export. The canonical validation document is
`contracts/catalog.schema.json`; package and module entries use the contract
versions declared in the export. A future website synchronizer can validate
the catalog before attaching repository URLs, discussion links, and moderation
metadata on the web side.
