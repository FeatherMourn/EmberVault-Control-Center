# Security and recovery audit

This audit records the current controls at the boundaries where EmberVault can
touch external files or publish information.

## Module installation and execution

- Module manifests are parsed fail-closed.
- IDs and executable paths reject traversal and absolute paths.
- Module source directories reject symlinks.
- Minimum core versions are checked before loading.
- Missing or incompatible dependencies prevent loading and launching.
- Separate-process modules are constrained to executables inside their package.
- Embedded modules must expose the declared descriptor contract.

## Package installation and deployment

- Package folders and archives reject traversal, duplicate paths, and symlinks.
- Packages are copied through staging before becoming managed.
- Profile enablement checks dependencies and detected game-build compatibility.
- Deployment requires an inspected, unchanged deployment plan.
- Existing destinations and foreign deployment markers are protected.
- Removal requires packages to be disabled and dependents removed first.

## Save recovery

- Save inspection rejects symlinked roots and entries.
- Restore requires a preview and a verified source backup.
- Restore creates a current-state backup first.
- Save contents are never edited by the Save Manager module.
- Restore operations are recorded with profile, backup, and recovery context.

## Public publishing

- Research, knowledge, and content records require explicit publication.
- Public catalog exports omit private profiles, evidence text, and history.
- Website catalog and submission validators reject malformed records and common
  private-data markers.
- Public changes require schema validation and repository review.

## Evidence

The regression suite covers these controls across module, package, save,
catalog, workflow, and packaging tests. Release verification additionally
checks packaged safety and recovery metadata before distribution bundles are
created.
