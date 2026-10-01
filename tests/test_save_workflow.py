import json
import tempfile
import unittest
from pathlib import Path

from core.logging_service import StructuredLogService
from core.operations import OperationService
from core.save_manager import SaveManagerService
from core.save_workflow import SaveWorkflowService


class SaveWorkflowTests(unittest.TestCase):
    def test_backup_and_restore_are_audited(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "live"
            live.mkdir()
            (live / "world.dat").write_text("original")
            workflow = SaveWorkflowService(
                SaveManagerService(root / "state"),
                OperationService(root / "state" / "operations.jsonl"),
                StructuredLogService(root / "state" / "logs.jsonl"),
            )
            backup = workflow.backup(live, "before change", "default")
            (live / "world.dat").write_text("changed")
            restored = workflow.restore(backup.snapshot.id, live, "default")
            self.assertEqual((live / "world.dat").read_text(), "original")
            records = [json.loads(line) for line in (root / "state" / "operations.jsonl").read_text().splitlines()]
            self.assertEqual(records[-1]["operation_type"], "save-restore")
            self.assertEqual(records[-1]["status"], "succeeded")
            self.assertTrue(restored.operation.id.startswith("EV-OP-"))


if __name__ == "__main__":
    unittest.main()
