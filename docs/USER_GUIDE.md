# Embervault Control Center user guide

## First launch

1. Open Home and choose the Enshrouded installation folder.
2. Confirm the Troubleshooter reports a readable installation.
3. Keep normal play in the Default profile.
4. Use Research or a custom profile for experiments.

## Mods

Open My Mods to import either a local package folder containing `package.json`
or an external mod folder containing `mod.json`, or a ZIP archive containing
either format. External `mod.json` metadata is adapted into EmberVault's
managed package contract without changing the source folder.
Packages are disabled by default and are enabled separately for each profile.
If a package declares `dependencies`, enable those packages first in the same
profile. Disable a package in every profile before removing it; packages that
other installed packages depend on must be removed last. A minimal manifest
looks like this:

```json
{
  "id": "embervault.example-mod",
  "name": "Example Mod",
  "version": "1.0.0",
  "package_type": "mod",
  "dependencies": []
}
```

Enabled packages can be checked with a deployment plan. The plan reports
missing packages and destination conflicts under the configured game `mods`
directory. Deployment is allowed only when every action is `ready`; existing
destinations block the operation, and partial failures remove newly created
destinations. Successful deployments carry an EmberVault ownership marker so
future removal can refuse unmarked or foreign destinations.
The Mods page exposes the same ownership-protected undeploy action.
Deployment also refuses package sources containing symlinks.
The configured game directory must already exist; deployment will not create a
new game tree.
Only packages with `package_type: "mod"` can deploy to the game `mods` folder;
other package types remain isolated for their own modules.
Troubleshooter also reports deployment conflicts and missing enabled-package
sources for each profile.

## Save safety

Save Manager can inspect a save folder, create a verified backup, re-verify a
backup, preview a restore, and restore after preserving the current state. It
does not edit save contents. Use Activity to review the recorded operation
history.

## Research and tools

Research records belong to a selected profile and can collect evidence notes.
Character and Content Creator pages store project plans separately from live
game data. Trainer, Research, and Content Creator execution remains guarded by
profile isolation and recovery requirements. Guarded workers are read-only in
this release and must return the versioned worker-result contract.

## Knowledge and integration

Knowledge contains the local safety and architecture guidance. Search it from
the Knowledge page or export the public catalog JSON for the Ember Vault
website. The export excludes paths, saves, logs, profiles, and private
research evidence.
