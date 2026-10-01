"""Conservative compatibility states and evaluations."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CompatibilityState(StrEnum):
    COMPATIBLE = "compatible"
    WARNINGS = "compatible-with-warnings"
    UNKNOWN = "unknown"
    INCOMPATIBLE = "incompatible"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class Compatibility:
    state: CompatibilityState
    reasons: tuple[str, ...] = ()


def evaluate(*, required_builds: list[str] | None, detected_build: str | None,
             blocked: bool = False, warnings: list[str] | None = None) -> Compatibility:
    if blocked:
        return Compatibility(CompatibilityState.BLOCKED, ("Capability is blocked by policy.",))
    if not detected_build or not required_builds:
        return Compatibility(CompatibilityState.UNKNOWN, ("Build evidence is incomplete.",))
    if detected_build not in required_builds:
        return Compatibility(CompatibilityState.INCOMPATIBLE, (f"Build {detected_build} is not in the tested set.",))
    if warnings:
        return Compatibility(CompatibilityState.WARNINGS, tuple(warnings))
    return Compatibility(CompatibilityState.COMPATIBLE)
