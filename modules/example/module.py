"""Minimal embedded-module contract example."""

from embervault_sdk import ModuleContext, ModuleResult


def describe() -> dict[str, str]:
    return {
        "id": "embervault.example",
        "execution": "embedded",
        "mutation": "read-only",
    }


def initialize(context: ModuleContext) -> ModuleResult:
    return ModuleResult("ready", "Example module initialized.", {
        "application_state": "plan-only",
        "evidence": [],
        "recovery": {"expectation": "No live mutation", "rollback": "Discard the plan", "verification": "Confirm no live files changed", "backup_required": False},
    })


def shutdown(context: ModuleContext) -> ModuleResult:
    return ModuleResult("stopped", "Example module stopped.")
