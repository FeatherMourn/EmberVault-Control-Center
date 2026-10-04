from embervault_sdk import ModuleContext, ModuleResult

MODULE_ID = "embervault.mod-manager"


def describe() -> dict:
    return {"id": MODULE_ID, "execution": "embedded", "application_state": "profile-scoped", "mutates_saves": False}


def initialize(context: ModuleContext) -> ModuleResult:
    if context.module_id != MODULE_ID or not context.profile_id:
        return ModuleResult("blocked", "Mod Manager requires a profile-scoped context.")
    return ModuleResult("ready", "Mod Manager is ready for an explicitly approved profile operation.", {
        "application_state": "profile-scoped",
        "profile_id": context.profile_id,
        "backup_required": True,
        "evidence": [{"id": "mod-manager-initialization", "kind": "runtime", "state": "observed", "summary": "No profile mutation performed during initialization."}],
        "recovery": {"expectation": "Profile backup before mutation", "rollback": "Restore the prior profile package state", "verification": "Confirm managed deployment marker", "backup_required": True},
    })
