import json
import tempfile
import unittest
from pathlib import Path

from core.modules import LaunchContext, ModuleRegistry
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

    def test_clean_registry_discovers_seed_example_module(self):
        with tempfile.TemporaryDirectory() as temp:
            registry = ModuleRegistry(Path(temp))
            self.assertEqual(list(registry.discover()), ["embervault.example", "embervault.trainer"])

    def test_python_module_process_uses_current_interpreter(self):
        with tempfile.TemporaryDirectory() as temp:
            module = Path(temp) / "demo"
            module.mkdir()
            (module / "module.json").write_text(json.dumps({
                "id": "demo.process", "name": "Demo", "version": "1.0.0",
                "publisher": "Test", "executable": "process.py",
            }))
            (module / "process.py").write_text("import sys; print(sys.argv[1])")
            registry = ModuleRegistry(Path(temp))
            registry.discover()
            process = registry.launch("demo.process", __import__("core.modules", fromlist=["LaunchContext"]).LaunchContext("default", "", None))
            process.wait(timeout=5)
            self.assertEqual(process.returncode, 0)

    def test_guarded_trainer_launch_succeeds_with_research_and_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            profile = next(item for item in runtime.profiles.list() if item.id == "research")
            process = runtime.launcher.launch(
                "embervault.trainer", "trainer", profile,
                LaunchContext(profile.id, None, "EV-OP-TEST"), "EV-BACKUP-TEST",
            )
            process.wait(timeout=5)
            self.assertEqual(process.returncode, 0)


if __name__ == "__main__":
    unittest.main()
