import json
import tempfile
import unittest
from pathlib import Path

from core.compatibility import CompatibilityState, evaluate
from core.logging_service import StructuredLogService
from core.operations import OperationService, OperationStatus
from core.profiles import ProfileService
from core.packages import PackageService
from core.game_settings import GameSettingsService
from core.risk import RiskGateService
from core.settings import Settings, SettingsService


class CoreServiceTests(unittest.TestCase):
    def test_settings_round_trip_is_atomic_and_typed(self):
        with tempfile.TemporaryDirectory() as temp:
            service = SettingsService(Path(temp))
            service.save(Settings(game_path="C:/Enshrouded", advanced_mode=True))
            loaded = service.load()
            self.assertEqual(loaded.game_path, "C:/Enshrouded")
            self.assertTrue(loaded.advanced_mode)

    def test_profiles_create_safe_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            profiles = ProfileService(Path(temp)).ensure_defaults()
            self.assertEqual({p.id for p in profiles}, {"default", "research"})

    def test_profile_defaults_have_distinct_safety_purposes(self):
        with tempfile.TemporaryDirectory() as temp:
            profiles = ProfileService(Path(temp)).ensure_defaults()
            by_id = {profile.id: profile for profile in profiles}
            self.assertEqual(by_id["default"].profile_type, "stable")
            self.assertEqual(by_id["research"].profile_type, "research")

    def test_structured_log_contains_contract_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "logs" / "events.jsonl"
            StructuredLogService(path).info("Started", operation_id="EV-OP-1", profile_id="default")
            record = json.loads(path.read_text().splitlines()[0])
            self.assertEqual(record["operation_id"], "EV-OP-1")
            self.assertEqual(record["profile_id"], "default")

    def test_operation_lifecycle_records_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            service = OperationService(Path(temp) / "operations.jsonl")
            operation = service.start("backup", profile_id="default")
            service.finish(operation, OperationStatus.SUCCEEDED, "Verified", "EV-BACKUP-1")
            records = [json.loads(line) for line in service.path.read_text().splitlines()]
            self.assertEqual(records[-1]["status"], "succeeded")
            self.assertEqual(records[-1]["backup_id"], "EV-BACKUP-1")

    def test_recent_operations_returns_latest_records_first(self):
        with tempfile.TemporaryDirectory() as temp:
            service = OperationService(Path(temp) / "operations.jsonl")
            first = service.start("first")
            service.finish(first, OperationStatus.SUCCEEDED, "done")
            second = service.start("second")
            service.finish(second, OperationStatus.FAILED, "broken")
            recent = service.list_recent(2)
            self.assertEqual([item.operation_type for item in recent], ["second", "first"])

    def test_unknown_compatibility_is_not_compatible(self):
        result = evaluate(required_builds=["1076226"], detected_build=None)
        self.assertEqual(result.state, CompatibilityState.UNKNOWN)

    def test_package_enablement_is_profile_scoped(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package_dir = root / "packages" / "demo"
            package_dir.mkdir(parents=True)
            (package_dir / "package.json").write_text(json.dumps({
                "id": "demo.mod", "name": "Demo Mod", "version": "1.0.0"
            }))
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            packages = PackageService(root, profiles)
            packages.discover()
            default = profiles.list()[0]
            updated = packages.set_enabled(default, "demo.mod", True)
            self.assertEqual(updated.enabled_packages, ["demo.mod"])
            research = next(profile for profile in profiles.list() if profile.id == "research")
            self.assertFalse(packages.is_enabled(research, "demo.mod"))

    def test_game_settings_are_stored_on_selected_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            service = GameSettingsService(profiles)
            profile = profiles.list()[0]
            updated = service.stage(profile, "enemy_damage_multiplier", 1.5)
            self.assertEqual(service.values(updated)["enemy_damage_multiplier"], 1.5)

    def test_high_risk_capabilities_require_research_and_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            profiles = ProfileService(Path(temp))
            profiles.ensure_defaults()
            stable, research = profiles.list()
            gate = RiskGateService()
            self.assertFalse(gate.evaluate("trainer", stable).allowed)
            self.assertFalse(gate.evaluate("trainer", research).allowed)
            self.assertTrue(gate.evaluate("trainer", research, verified_backup_id="EV-BACKUP-1").allowed)


if __name__ == "__main__":
    unittest.main()
