import json
import tempfile
import unittest
from pathlib import Path

from core.modules import ModuleRegistry


class ModuleRegistryTests(unittest.TestCase):
    def test_discovers_manifest_and_capability(self):
        with tempfile.TemporaryDirectory() as temp:
            module = Path(temp) / "demo"
            module.mkdir()
            (module / "module.json").write_text(json.dumps({
                "id": "embervault.demo", "name": "Demo", "version": "1.0.0",
                "publisher": "Test", "capabilities": ["demo.read"],
            }))
            registry = ModuleRegistry(Path(temp))
            modules = registry.discover()
            self.assertEqual(modules["embervault.demo"].name, "Demo")
            self.assertEqual([m.id for m in registry.by_capability("demo.read")], ["embervault.demo"])

    def test_discovery_ignores_malformed_manifests(self):
        with tempfile.TemporaryDirectory() as temp:
            module = Path(temp) / "broken"
            module.mkdir()
            (module / "module.json").write_text("not json")
            self.assertEqual(ModuleRegistry(Path(temp)).discover(), {})


if __name__ == "__main__":
    unittest.main()
