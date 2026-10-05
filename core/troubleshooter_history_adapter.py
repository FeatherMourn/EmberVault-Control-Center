"""Control Center boundary for approved Troubleshooter report-history actions."""

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any


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


def dispatch_history_action(request: HistoryActionRequest, runtime_handler: Callable[..., Any],
                            context: Any) -> Any:
    """Forward an approved request to the packaged Troubleshooter runtime."""
    if not isinstance(request, HistoryActionRequest) or request.approved is not True:
        raise PermissionError("Only approved history requests can be dispatched.")
    if not callable(runtime_handler):
        raise ValueError("A packaged Troubleshooter runtime handler is required.")
    return runtime_handler(context, {
        "contract_version": 1, "action": request.action, "approved": True,
        "store_path": request.store_path, "key_reference": request.key_reference,
    })
