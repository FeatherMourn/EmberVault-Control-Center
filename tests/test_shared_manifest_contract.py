import json
import unittest
from pathlib import Path

from core.modules import ModuleManifest


ROOT = Path(__file__).resolve().parents[1]


class SharedManifestContractTests(unittest.TestCase):
    def test_seed_starter_module_matches_contract_v1_shape(self):
        manifest_path = ROOT / "modules" / "example" / "module.json"
        shared_schema = Path(__file__).resolve().parents[2] / "EmberVault-Contracts" / "schemas" / "module-manifest.schema.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads(shared_schema.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "https://embervault.dev/contracts/module-manifest.schema.json")
        self.assertEqual(manifest["contract_version"], schema["properties"]["contract_version"]["const"])
        parsed = ModuleManifest.from_file(manifest_path)
        self.assertEqual(parsed.id, "embervault.example")
        self.assertEqual(parsed.process_mode, "embedded")
        self.assertTrue(parsed.safety["read_only"])
        self.assertIn("example-inspection", parsed.operation_types)


if __name__ == "__main__":
    unittest.main()
