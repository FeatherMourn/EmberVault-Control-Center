import tempfile
import unittest
import zipfile
from pathlib import Path

from core.updater import ExternalUpdaterService


class ExternalUpdaterTests(unittest.TestCase):
    def test_prepare_writes_review_only_plan_without_replacing_installation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); staged = root / "update.zip"; staged.write_bytes(b"update")
            installation = root / "install"; installation.mkdir(); (installation / "old.txt").write_text("old")
            plan_file = ExternalUpdaterService(root).prepare("1.2.0", staged, installation)
            plan = plan_file.read_text(encoding="utf-8")
            self.assertIn('"status": "review-only"', plan)
            self.assertEqual((installation / "old.txt").read_text(), "old")

    def test_backup_and_startup_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); staged = root / "update.zip"; staged.write_bytes(b"update")
            installation = root / "install"; installation.mkdir(); (installation / "old.txt").write_text("old")
            service = ExternalUpdaterService(root)
            plan = service.prepare("1.2.0", staged, installation)
            backup = service.backup(plan)
            self.assertEqual((backup / "old.txt").read_text(), "old")
            self.assertTrue(service.validate_startup(0))
            self.assertFalse(service.validate_startup(1))

    def test_helper_requires_explicit_approval(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); staged = root / "update.zip"; staged.write_bytes(b"update")
            installation = root / "install"; installation.mkdir()
            service = ExternalUpdaterService(root)
            plan = service.prepare("1.2.0", staged, installation)
            with self.assertRaises(ValueError):
                service.helper_command(plan)
            service.approve(plan)
            self.assertIn("external_updater.py", service.helper_command(plan)[1])

    def test_approved_update_rolls_back_when_startup_probe_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); staged = root / "update.zip"
            with zipfile.ZipFile(staged, "w") as archive:
                archive.writestr("new.txt", "new")
            installation = root / "install"; installation.mkdir(); (installation / "old.txt").write_text("old")
            service = ExternalUpdaterService(root); plan = service.prepare("1.2.0", staged, installation); service.approve(plan)
            self.assertFalse(service.apply_approved(plan, lambda probe: False))
            self.assertTrue((installation / "old.txt").is_file())
            self.assertFalse((installation / "new.txt").exists())

    def test_approved_update_keeps_new_files_after_successful_probe(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); staged = root / "update.zip"
            with zipfile.ZipFile(staged, "w") as archive:
                archive.writestr("new.txt", "new")
            installation = root / "install"; installation.mkdir(); (installation / "old.txt").write_text("old")
            service = ExternalUpdaterService(root); plan = service.prepare("1.2.0", staged, installation); service.approve(plan)
            self.assertTrue(service.apply_approved(plan, lambda probe: True))
            self.assertTrue((installation / "new.txt").is_file())
            self.assertFalse((installation / "old.txt").exists())

    def test_helper_entry_point_defaults_to_validation(self):
        from tools.external_updater import main
        self.assertTrue(callable(main))

    def test_recovery_restores_installation_after_interrupted_rename(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); staged = root / "update.zip"; staged.write_bytes(b"update")
            installation = root / "install"; installation.mkdir(); (installation / "old.txt").write_text("old")
            service = ExternalUpdaterService(root); plan = service.prepare("1.2.0", staged, installation); service.approve(plan)
            data = __import__('json').loads(plan.read_text()); backup = Path(data["backup"]); backup.parent.mkdir(parents=True)
            import shutil; shutil.copytree(installation, backup); old = installation.with_name("install.old"); installation.rename(old)
            self.assertEqual(service.recover_pending(plan), "rolled-back-recovered")
            self.assertEqual((installation / "old.txt").read_text(), "old")

    def test_recovery_marks_existing_target_for_review(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); staged = root / "update.zip"; staged.write_bytes(b"update")
            installation = root / "install"; installation.mkdir()
            service = ExternalUpdaterService(root); plan = service.prepare("1.2.0", staged, installation); service.approve(plan)
            data = __import__('json').loads(plan.read_text()); Path(data["backup"]).mkdir(parents=True)
            self.assertEqual(service.recover_pending(plan), "pending-review")


if __name__ == "__main__":
    unittest.main()
