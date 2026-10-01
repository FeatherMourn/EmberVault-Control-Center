"""Profile-scoped gameplay settings with explicit staged application state."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .profiles import Profile, ProfileService


@dataclass(frozen=True)
class SettingDefinition:
    key: str
    name: str
    description: str
    default: Any
    value_type: str


DEFINITIONS = (
    SettingDefinition("enemy_damage_multiplier", "Enemy damage", "Research value for incoming damage.", 1.0, "number"),
    SettingDefinition("resource_yield_multiplier", "Resource yield", "Research value for gathered resources.", 1.0, "number"),
    SettingDefinition("experimental_rules", "Experimental rules", "Marks this profile as a tuning test surface.", False, "boolean"),
)


class GameSettingsService:
    def __init__(self, profiles: ProfileService):
        self.profiles = profiles

    def definitions(self) -> tuple[SettingDefinition, ...]:
        return DEFINITIONS

    def values(self, profile: Profile) -> dict[str, Any]:
        return {definition.key: profile.settings.get(definition.key, definition.default) for definition in DEFINITIONS}

    def stage(self, profile: Profile, key: str, value: Any) -> Profile:
        definition = next((item for item in DEFINITIONS if item.key == key), None)
        if not definition:
            raise ValueError(f"Unknown game setting: {key}")
        if definition.value_type == "number" and (not isinstance(value, (int, float)) or value < 0):
            raise ValueError(f"Invalid value for {key}")
        if definition.value_type == "boolean" and not isinstance(value, bool):
            raise ValueError(f"Invalid value for {key}")
        settings = dict(profile.settings)
        settings[key] = value
        updated = Profile(**{**profile.__dict__, "settings": settings})
        self.profiles.save(updated)
        return updated
