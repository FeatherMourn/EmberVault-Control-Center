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

    def test_custom_profile_creation_generates_safe_id(self):
        with tempfile.TemporaryDirectory() as temp:
            service = ProfileService(Path(temp))
            service.ensure_defaults()
            profile = service.create_custom("My Test World")
            self.assertEqual(profile.id, "my-test-world")
            self.assertEqual(profile.profile_type, "custom")

    def test_built_in_profiles_cannot_be_deleted(self):
        with tempfile.TemporaryDirectory() as temp:
            service = ProfileService(Path(temp))
            service.ensure_defaults()
            with self.assertRaises(ValueError):
                service.delete_custom("default")

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

    def test_recent_operations_skips_corrupt_history_lines(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "operations.jsonl"
            service = OperationService(path)
            operation = service.start("valid")
            path.write_text(path.read_text(encoding="utf-8") + "not-json\n", encoding="utf-8")
            self.assertEqual([item.operation_type for item in service.list_recent()], ["valid"])

    def test_settings_preserve_game_folder_for_detection(self):
        with tempfile.TemporaryDirectory() as temp:
            service = SettingsService(Path(temp))
            service.save(Settings(game_path="C:/Games/Enshrouded"))
            self.assertEqual(service.load().game_path, "C:/Games/Enshrouded")

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

    def test_game_settings_reset_restores_documented_defaults(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            service = GameSettingsService(profiles)
            profile = profiles.list()[0]
            changed = service.stage(profile, "enemy_damage_multiplier", 2.0)
            reset = service.reset(changed)
            self.assertEqual(service.values(reset)["enemy_damage_multiplier"], 1.0)

    def test_high_risk_capabilities_require_research_and_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            profiles = ProfileService(Path(temp))
            profiles.ensure_defaults()
            stable, research = profiles.list()
            gate = RiskGateService()
            self.assertFalse(gate.evaluate("trainer", stable).allowed)
            self.assertFalse(gate.evaluate("trainer", research).allowed)
            self.assertTrue(gate.evaluate("trainer", research, verified_backup_id="EV-BACKUP-1").allowed)

    def test_package_import_requires_manifest_and_copies_valid_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            source = root / "incoming"
            source.mkdir()
            (source / "package.json").write_text(json.dumps({"id": "imported.mod", "name": "Imported", "version": "1.0.0"}))
            service = PackageService(root, profiles)
            package = service.install_from_directory(source)
            self.assertEqual(package.id, "imported.mod")
            self.assertTrue((root / "packages" / "imported.mod" / "package.json").exists())
            self.assertEqual(list(root.glob("embervault-package-stage-*")), [])

    def test_clean_package_service_can_discover_seed_example(self):
        with tempfile.TemporaryDirectory() as temp:
            profiles = ProfileService(Path(temp))
            profiles.ensure_defaults()
            packages = PackageService(Path(temp), profiles)
            self.assertEqual([item.id for item in packages.list()], ["embervault.example-mod"])

    def test_managed_package_cannot_be_removed_while_enabled(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            incoming = root / "incoming"
            incoming.mkdir()
            (incoming / "package.json").write_text(json.dumps({"id": "managed.mod", "name": "Managed", "version": "1.0.0"}))
            packages = PackageService(root, profiles)
            packages.install_from_directory(incoming)
            default = profiles.list()[0]
            packages.set_enabled(default, "managed.mod", True)
            with self.assertRaises(ValueError):
                packages.remove("managed.mod")
            packages.set_enabled(default, "managed.mod", False)
            packages.remove("managed.mod")
            self.assertIsNone(packages.get("managed.mod"))

    def test_package_removal_protects_dependents(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            incoming = root / "incoming"
            incoming.mkdir()
            (incoming / "package.json").write_text(json.dumps({
                "id": "base.mod", "name": "Base", "version": "1.0",
            }))
            packages = PackageService(root, profiles)
            packages.install_from_directory(incoming)
            dependent = root / "dependent"
            dependent.mkdir()
            (dependent / "package.json").write_text(json.dumps({
                "id": "addon.mod", "name": "Addon", "version": "1.0", "dependencies": ["base.mod"],
            }))
            packages.install_from_directory(dependent)
            with self.assertRaisesRegex(ValueError, "dependent"):
                packages.remove("base.mod")

    def test_package_archive_import_rejects_unsafe_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            archive = root / "unsafe.zip"
            import zipfile
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("../escape.txt", "no")
            with self.assertRaises(ValueError):
                PackageService(root, profiles).install_from_archive(archive)

    def test_package_archive_imports_nested_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            archive = root / "package.zip"
            import zipfile
            with zipfile.ZipFile(archive, "w") as bundle:
                bundle.writestr("demo/package.json", json.dumps({"id": "archive.mod", "name": "Archive", "version": "1.0.0"}))
            package = PackageService(root, profiles).install_from_archive(archive)
            self.assertEqual(package.id, "archive.mod")

    def test_package_manifest_rejects_path_like_id(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            incoming = root / "incoming"
            incoming.mkdir()
            (incoming / "package.json").write_text(json.dumps({"id": "../escape", "name": "Unsafe", "version": "1.0.0"}))
            with self.assertRaises(ValueError):
                PackageService(root, profiles).install_from_directory(incoming)

    def test_package_manifest_rejects_path_like_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            incoming = root / "incoming"
            incoming.mkdir()
            (incoming / "package.json").write_text(json.dumps({
                "id": "unsafe.mod", "name": "Unsafe", "version": "1.0", "dependencies": ["../escape"],
            }))
            with self.assertRaises(ValueError):
                PackageService(root, profiles).install_from_directory(incoming)

    def test_package_manifest_rejects_duplicate_or_self_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            for dependencies in (["base.mod", "base.mod"], ["self.mod"]):
                incoming = root / ("incoming-" + str(len(dependencies)))
                incoming.mkdir()
                package_id = "self.mod" if dependencies == ["self.mod"] else "duplicate.mod"
                (incoming / "package.json").write_text(json.dumps({
                    "id": package_id, "name": "Invalid", "version": "1.0", "dependencies": dependencies,
                }))
                with self.assertRaises(ValueError):
                    PackageService(root, profiles).install_from_directory(incoming)

    def test_package_enablement_blocks_known_incompatible_build(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            incoming = root / "incoming"
            incoming.mkdir()
            (incoming / "package.json").write_text(json.dumps({
                "id": "build.mod", "name": "Build Mod", "version": "1.0.0", "required_builds": ["old"]
            }))
            packages = PackageService(root, profiles)
            packages.install_from_directory(incoming)
            with self.assertRaises(ValueError):
                packages.set_enabled(profiles.list()[0], "build.mod", True, "new")

    def test_package_enablement_requires_profile_dependencies(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            profiles = ProfileService(root)
            profiles.ensure_defaults()
            for package_id, dependencies in (("base.mod", []), ("addon.mod", ["base.mod"])):
                package = root / "packages" / package_id
                package.mkdir(parents=True)
                (package / "package.json").write_text(json.dumps({
                    "id": package_id, "name": package_id, "version": "1.0", "dependencies": dependencies,
                }))
            packages = PackageService(root, profiles)
            packages.discover()
            profile = profiles.list()[0]
            with self.assertRaisesRegex(ValueError, "dependencies"):
                packages.set_enabled(profile, "addon.mod", True)
            profile = packages.set_enabled(profile, "base.mod", True)
            packages.set_enabled(profile, "addon.mod", True)


if __name__ == "__main__":
    unittest.main()
