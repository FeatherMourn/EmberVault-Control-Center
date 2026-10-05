from embervault_sdk import ModuleContext, ModuleResult

MODULE_ID = "embervault.troubleshooter"


def describe() -> dict:
    return {"id": MODULE_ID, "execution": "embedded", "application_state": "read-only", "mutates_workspace": False}


def scan_evidence(context: ModuleContext, evidence: dict) -> ModuleResult:
    if context.module_id != MODULE_ID or not isinstance(evidence, dict) or evidence.get("contract_version") != 1:
        return ModuleResult("blocked", "Diagnostic evidence requires the Troubleshooter version-one contract.")
    producer = evidence.get("producer")
    findings = evidence.get("findings")
    if not isinstance(producer, str) or not producer.strip() or not isinstance(findings, list):
        return ModuleResult("blocked", "Diagnostic evidence requires a producer and findings list.")
    result = scan(context, findings)
    if result.status != "ready":
        return result
    data = dict(result.data)
    data["evidence_contract"] = {"contract_version": 1, "producer": producer.strip()}
    data["source_operation"] = str(evidence.get("operation", "unspecified"))
    return ModuleResult("ready", "Version-one diagnostic evidence summarized.", data)


def plan_history_action(context: ModuleContext, action: str, approved: bool) -> ModuleResult:
    """Return an explicit plan for report-history lifecycle work; never executes it."""
    if context.module_id != MODULE_ID:
        return ModuleResult("blocked", "Troubleshooter received an invalid module context.")
    if action not in {"save", "clear", "delete"}:
        return ModuleResult("blocked", "Unsupported report-history action.")
    if approved is not True:
        return ModuleResult("blocked", "Report-history lifecycle actions require explicit approval.")
    return ModuleResult("ready", "Report-history action approved for external execution.", {
        "action": action, "approved": True, "plan_only": True,
        "read_only": True, "mutates_workspace": False,
        "authority": "Control Center",
    })


def scan(context: ModuleContext, findings: list[dict]) -> ModuleResult:
    if context.module_id != MODULE_ID:
        return ModuleResult("blocked", "Troubleshooter received an invalid module context.")
    normalized = []
    for finding in findings:
        if not isinstance(finding, dict) or not finding.get("title") or not finding.get("severity"):
            return ModuleResult("blocked", "Diagnostic findings must include a title and severity.")
        normalized.append({"title": str(finding["title"]), "severity": str(finding["severity"]), "message": str(finding.get("message", ""))})
    return ModuleResult("ready", "Read-only diagnostic scan completed.", {
        "findings": normalized, "attention_count": sum(item["severity"] == "attention" for item in normalized),
        "application_state": "read-only", "mutates_workspace": False,
        "evidence": [{"id": "diagnostic-scan", "kind": "test", "state": "observed", "summary": "Read-only diagnostic findings collected."}],
        "recovery": {"expectation": "No repair or mutation", "rollback": "Discard diagnostic output", "verification": "Confirm workspace is unchanged", "backup_required": False},
    })
