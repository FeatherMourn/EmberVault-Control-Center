from embervault_sdk import ModuleContext, ModuleResult

MODULE_ID = "embervault.character-tools"


def describe() -> dict:
    return {"id": MODULE_ID, "execution": "embedded", "application_state": "plan-only", "mutates_saves": False}


def initialize(context: ModuleContext) -> ModuleResult:
    if context.module_id != MODULE_ID or not context.profile_id:
        return ModuleResult("blocked", "Character Tools requires a profile-scoped context.")
    return ModuleResult("ready", "Character Tools is ready for plan-only analysis.", {
        "application_state": "plan-only",
        "profile_id": context.profile_id,
        "mutates_saves": False,
        "evidence": [{"id": "character-tools-initialization", "kind": "runtime", "state": "observed", "summary": "No save contents read or changed during initialization."}],
        "recovery": {"expectation": "Discard plan revision", "rollback": "Discard the exported plan", "verification": "Confirm no save mutation", "backup_required": True},
    })
