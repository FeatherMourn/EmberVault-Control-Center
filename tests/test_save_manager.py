import tempfile
import unittest
import os
from pathlib import Path

from core.save_manager import SaveManagerError, SaveManagerService


class SaveManagerTests(unittest.TestCase):
    def test_backup_verify_preview_and_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "live"
            live.mkdir()
            (live / "characters-index").write_text("one")
            (live / "world.dat").write_text("first")
            service = SaveManagerService(root / "state")
            snapshot = service.backup(live, "before test")
            self.assertTrue(service.verify_backup(snapshot.id))
            (live / "world.dat").write_text("changed")
            preview = service.preview_restore(snapshot.id, live)
            self.assertTrue(preview["requires_current_backup"])
            current = service.backup(live, "before restore")
            service.restore(snapshot.id, live, current_backup=current)
            self.assertEqual((live / "world.dat").read_text(), "first")

    def test_restore_requires_current_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "live"
            live.mkdir()
            (live / "save.dat").write_text("data")
            service = SaveManagerService(root / "state")
            snapshot = service.backup(live)
            with self.assertRaises(SaveManagerError):
                service.restore(snapshot.id, live)

    def test_inspection_rejects_symlinked_save_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            live = root / "live"
            live.mkdir()
            outside = root / "outside.dat"
            outside.write_text("outside")
            link = live / "linked.dat"
            try:
                os.symlink(outside, link)
            except (OSError, NotImplementedError):
                self.skipTest("Symlink creation is unavailable")
            with self.assertRaises(SaveManagerError):
                SaveManagerService.inspect(live)


if __name__ == "__main__":
    unittest.main()
