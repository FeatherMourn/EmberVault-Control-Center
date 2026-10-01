# Game settings boundary

The Control Center keeps gameplay tuning staged and profile-scoped until a
supported application contract is available.

## Observed installation surfaces

The inspected Enshrouded installation exposes `enshrouded_local.json` with
client graphics, display, and audio preferences. It does not expose a native
gameplay-tuning document. Gameplay experiments in the reference mod workspace
are represented by mod-owned Lua/config content, for example the Enshrouded
Mod Hub configuration modules.

## Safety decision

Control Center does not write to `enshrouded_local.json`, binary game data, or
mod-owned source files as part of Game Settings. Staged values can be exported
as a portable tuning manifest and consumed later by an explicitly identified
mod or tuning module. Such a module must declare its input contract, backup
requirements, mutation scope, and verification procedure before live
application is enabled.

This preserves the first-release Save Manager boundary and prevents treating
client display settings as gameplay controls.
