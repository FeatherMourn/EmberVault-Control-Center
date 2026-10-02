# EmberVault user acceptance checklist

Run this checklist against a clean installed build and a disposable test
workspace before public release.

## First launch

- [ ] The shell opens without a configured game folder.
- [ ] Home explains the next steps and distinguishes the default and research
      profiles.
- [ ] Modules opens and shows feature state, process mode, capabilities, and
      safety/recovery status.
- [ ] The application does not claim that experimental features are stable.

## Safe everyday workflow

- [ ] A user can choose a game folder and create a verified save backup.
- [ ] A user can inspect and enable a package for one profile.
- [ ] A package enabled for Research is not enabled for Default automatically.
- [ ] Deployment requires reviewing the current deployment plan first.
- [ ] Existing or unmanaged destinations are not overwritten.

## Experimental workflow

- [ ] Trainer and Research are refused from the Default profile.
- [ ] Trainer is refused without a verified backup.
- [ ] Research launches as a separate process.
- [ ] Content Creator produces design-only records and does not touch live game
      files.
- [ ] Game Tuning remains staged-only until an explicit adapter workflow is
      reviewed.

## Recovery workflow

- [ ] Restore requires previewing the selected backup.
- [ ] Restore creates a current-state backup first.
- [ ] The Activity page shows profile, capability state, backup, and recovery
      expectation.
- [ ] A failed or blocked operation leaves the original data available.

## Public publishing

- [ ] Only explicitly published research, knowledge, and content records appear
      in the catalog.
- [ ] Public exports contain no profile IDs, private evidence text, save paths,
      credentials, or operation logs.
- [ ] Website catalog and submission validators pass before publication.

Record the date, build, tester, platform, and any failed step with a recovery
note before approving a public release.
