import json
import tempfile
import unittest
from pathlib import Path

from core.modules import ModuleRegistry
from core.application import EmbervaultRuntime


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

    def test_high_risk_launch_is_denied_before_process_start(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            profile = next(item for item in runtime.profiles.list() if item.id == "default")
            decision = runtime.launcher.check("trainer", "trainer", profile)
            self.assertFalse(decision.allowed)
            self.assertIn("Research profile", decision.reasons[0])


if __name__ == "__main__":
    unittest.main()
