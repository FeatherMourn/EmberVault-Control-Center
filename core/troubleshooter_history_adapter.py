"""Control Center boundary for approved Troubleshooter report-history actions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HistoryActionRequest:
    action: str
    store_path: str
    approved: bool
    key_reference: str


def create_history_action_request(action: str, store_path: str, key_reference: str,
                                  approved: bool) -> HistoryActionRequest:
    if action not in {"save", "clear", "delete"}:
        raise ValueError("Unsupported report-history action.")
    if not approved:
        raise PermissionError("Report-history actions require explicit approval.")
    if not isinstance(store_path, str) or not store_path.strip():
        raise ValueError("An encrypted report-store path is required.")
    if not isinstance(key_reference, str) or not key_reference.strip():
        raise ValueError("A key reference is required; raw keys are not accepted.")
    return HistoryActionRequest(action, store_path, True, key_reference)
