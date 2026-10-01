# EML runtime evidence

Captured from the installed Enshrouded EML session logs. This document records
what the runtime proved; it does not authorize live mutation by EmberVault.

## Environment identity

- Enshrouded build: `1076226`
- Game branch: `/game38/branches/ea_update_08`
- Game build timestamp: `2026-06-29T10:27:39.052394Z`
- EML Lua API: `1.3`
- Type registry: `.cache/types.json`
- KFC source: `enshrouded.kfc`
- Evidence log: `H:\SteamLibrary\steamapps\common\Enshrouded\logs\2026-09-30.eml.log`

## Proven runtime behavior

The EML session log repeatedly records:

- successful type-registry loading;
- Lua API initialization at version `1.3`;
- execution of the `enshrouded_mod_hub` module;
- access to `keen::BalancingTable`;
- a resolved BalancingTable GUID:
  `82706b40-61b1-4b8f-8b23-dcec6971bda1`;
- successful application of the Mod Hub's progression-balancing patch;
- EML applying the patch set and attaching its runtime loader.

This proves that EML can execute a Lua mod and that the installed Mod Hub can
reach and mutate a BalancingTable resource in this build. It does not yet
prove that every individual field is accepted, that the change is visible in
gameplay, or that rollback has been verified.

## Adapter implication

The first EML adapter candidate should use the existing Mod Hub's declared
progression boundary as a research target, with one field changed at a time.
`player_level_cap` remains the proposed first candidate because it has a clear
input mapping and an observable in-game result.

The adapter must still provide its own ownership marker, verified backup,
closed-game gate, exact before/after record, post-launch observation, and
rollback test. The current log is runtime evidence, not a completed adapter
review packet.

## Current status

`experimental`: runtime registration and resource access evidenced.

Not yet verified: controlled single-field change, in-game behavior, clean
rollback, multiplayer scope, and compatibility after a fresh build change.
