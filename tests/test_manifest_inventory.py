import unittest
from pathlib import Path

from core.modules import ModuleManifest


ROOT = Path(__file__).resolve().parents[1]


class ManifestInventoryTests(unittest.TestCase):
    def test_all_bundled_modules_parse_against_contract_v1(self):
        paths = sorted((ROOT / "modules").rglob("module.json"))
        self.assertGreaterEqual(len(paths), 1)
        manifests = [ModuleManifest.from_file(path) for path in paths]
        ids = [manifest.id for manifest in manifests]
        self.assertEqual(len(ids), len(set(ids)))
        for manifest in manifests:
            self.assertEqual(manifest.contract_version, 1)
            self.assertTrue(manifest.safety.get("allowed_profiles"))
            self.assertIn("rollback", manifest.recovery)
            self.assertIn("verification", manifest.recovery)

    def test_manifest_paths_stay_inside_module_inventory(self):
        for path in sorted((ROOT / "modules").rglob("module.json")):
            manifest = ModuleManifest.from_file(path)
            self.assertEqual(manifest.path, path.parent)
            self.assertTrue(path.parent.is_relative_to(ROOT / "modules"))

    def test_game_tuning_is_declared_staged_and_read_only(self):
        manifest = ModuleManifest.from_file(ROOT / "modules" / "game-tuning" / "module.json")
        self.assertTrue(manifest.safety["read_only"])


if __name__ == "__main__":
    unittest.main()
