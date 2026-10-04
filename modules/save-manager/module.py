from embervault_sdk import ModuleContext, ModuleResult

MODULE_ID = "embervault.save-manager"


def describe() -> dict:
    return {"id": MODULE_ID, "execution": "embedded", "application_state": "backup-gated", "mutates_saves": True}


def initialize(context: ModuleContext) -> ModuleResult:
    if context.module_id != MODULE_ID or not context.profile_id:
        return ModuleResult("blocked", "Save Manager requires a profile-scoped context.")
    return ModuleResult("ready", "Save Manager is ready for an explicitly approved, backup-gated operation.", {
        "application_state": "backup-gated",
        "profile_id": context.profile_id,
        "backup_required": True,
        "evidence": [{"id": "save-manager-initialization", "kind": "runtime", "state": "observed", "summary": "No save mutation performed during initialization."}],
        "recovery": {"expectation": "Current-state backup before restore", "rollback": "Restore the current-state backup", "verification": "Verify source and current-state backups", "backup_required": True},
    })
