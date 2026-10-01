"""Launch gates for higher-risk or separate-process capabilities."""
from __future__ import annotations

from dataclasses import dataclass

from .profiles import Profile


@dataclass(frozen=True)
class RiskDecision:
    capability: str
    allowed: bool
    reasons: tuple[str, ...] = ()


class RiskGateService:
    def evaluate(self, capability: str, profile: Profile, *, verified_backup_id: str | None = None) -> RiskDecision:
        reasons: list[str] = []
        if capability in {"trainer", "research", "content-creator"} and profile.profile_type != "research":
            reasons.append("Select the isolated Research profile.")
        if capability in {"trainer", "content-creator"} and not verified_backup_id:
            reasons.append("Create or select a verified backup first.")
        return RiskDecision(capability, not reasons, tuple(reasons))
