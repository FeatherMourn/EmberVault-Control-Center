import json
import tempfile
import unittest
from pathlib import Path

from core.compatibility import CompatibilityState, evaluate
from core.logging_service import StructuredLogService
from core.operations import OperationService, OperationStatus
from core.profiles import ProfileService
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


if __name__ == "__main__":
    unittest.main()
