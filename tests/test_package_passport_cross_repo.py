import importlib.util
import json
import unittest
from pathlib import Path

from core.mod_package_passport import review_package_passport


class PackagePassportCrossRepoTests(unittest.TestCase):
    def test_research_passport_flows_to_control_center_and_troubleshooter_shape(self):
        candidates = (Path(__file__).parents[2] / "EmberVault-Mod-Research",
                      Path(__file__).parents[1].parent / "EmberVault-Mod-Research")
        research = next((path for path in candidates if path.is_dir()), candidates[0])
        source = research / "src/mod_package_passport.py"
        spec = importlib.util.spec_from_file_location("research_passport", source)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        passport = json.loads((research / "research/external/SHROUDFORGE_PACKAGE_PASSPORT_FIXTURE_20261013.json").read_text(encoding="utf-8"))
        metadata = module.build_passport_metadata(passport)
        self.assertEqual(metadata["state"], "review-required")
        request = review_package_passport({**passport, "backup_required": True}, backup_id="save-backup-1")
        self.assertEqual(request["state"], "approval-required")
        troubleshooter_payload = {
            "passport_version": metadata["passport_version"],
            "id": passport["id"],
            "version": passport["version"],
            "builds": passport["builds"],
            "targets": passport["targets"],
            "files": passport["files"],
            "dependencies": passport["dependencies"],
            "evidence": passport["evidence"],
            "read_only": metadata["read_only"],
            "runtime_approval": metadata["runtime_approval"],
        }
        self.assertEqual(troubleshooter_payload["id"], request["package_id"])
        self.assertTrue(request["plan_only"])
        self.assertFalse(request["executes_installation"])
        self.assertFalse(request["mutates_workspace"])

    def test_cross_repo_flow_blocks_missing_hashes(self):
        passport = {"id": "sf.example", "version": "1.6.6", "builds": ["1076226"],
                    "targets": ["client"], "files": [{"path": "mod.json"}], "dependencies": [],
                    "evidence": [], "read_only": True, "runtime_approval": False, "backup_required": True}
        request = review_package_passport(passport, backup_id="save-backup-1")
        self.assertEqual(request["state"], "blocked")
        self.assertIn("hash", " ".join(request["issues"]))


if __name__ == "__main__":
    unittest.main()
