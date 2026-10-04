import json
import unittest
from pathlib import Path

from core.modules import ModuleManifest


ROOT = Path(__file__).resolve().parents[1]


class SharedManifestContractTests(unittest.TestCase):
    def test_shared_packaging_copies_use_canonical_sources(self):
        for name in ("worker-result.schema.json", "integration-context.schema.json", "promotion-evidence.schema.json", "evidence-reference.schema.json", "recovery-reference.schema.json"):
            local = json.loads((ROOT / "contracts" / name).read_text(encoding="utf-8"))
            self.assertTrue(local["$id"].startswith("https://embervault.dev/contracts/"), name)
            self.assertEqual(local["x-canonical-source"], f"EmberVault-Contracts/schemas/{name}")

    def test_seed_starter_module_matches_contract_v1_shape(self):
        manifest_path = ROOT / "modules" / "example" / "module.json"
        shared_schema = Path(__file__).resolve().parents[2] / "EmberVault-Contracts" / "schemas" / "module-manifest.schema.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        schema = json.loads(shared_schema.read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "https://embervault.dev/contracts/module-manifest.schema.json")
        local_schema = json.loads((ROOT / "contracts" / "module-manifest.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(local_schema["$id"], schema["$id"])
        self.assertEqual(local_schema["x-canonical-source"], "EmberVault-Contracts/schemas/module-manifest.schema.json")
        self.assertEqual(manifest["contract_version"], schema["properties"]["contract_version"]["const"])
        parsed = ModuleManifest.from_file(manifest_path)
        self.assertEqual(parsed.id, "embervault.example")
        self.assertEqual(parsed.process_mode, "embedded")
        self.assertTrue(parsed.safety["read_only"])
        self.assertIn("example-inspection", parsed.operation_types)


if __name__ == "__main__":
    unittest.main()
