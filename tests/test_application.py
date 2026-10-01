import subprocess
import tempfile
import unittest
from unittest.mock import Mock
from pathlib import Path

from core.application import EmbervaultRuntime
from control_center.backend import ControlCenterBackend


class ApplicationCompositionTests(unittest.TestCase):
    def test_runtime_composes_services_and_reports_health(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            health = runtime.health()
            self.assertEqual(health["core"], "ready")
            self.assertEqual(health["profiles"], 2)
            self.assertEqual(health["modules"], 4)
            self.assertEqual(health["backups"], 0)

    def test_troubleshooter_reports_unconfigured_game_without_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            findings = runtime.troubleshooter.scan()
            self.assertEqual(findings[0].key, "game-path")
            self.assertEqual(findings[0].severity, "attention")

    def test_research_record_keeps_evidence_with_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Yield test", "Yield changes under staged setting", "research")
            updated = runtime.research.add_evidence(record.id, "Observed baseline behavior")
            self.assertEqual(updated.profile_id, "research")
            self.assertEqual(updated.evidence, ["Observed baseline behavior"])

    def test_knowledge_catalog_searches_seeded_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            entries = runtime.knowledge.search("restore")
            self.assertEqual([entry.id for entry in entries], ["save-safety"])

    def test_troubleshooter_flags_package_with_unsupported_build(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            package = root / "packages" / "tested"
            package.mkdir(parents=True)
            (package / "package.json").write_text(
                '{"id":"tested.mod","name":"Tested Mod","version":"1.0.0","required_builds":["old-build"]}'
            )
            game = root / "game" / "steamapps"
            game.mkdir(parents=True)
            (game.parent / "Enshrouded.exe").write_bytes(b"")
            (game / "appmanifest_1203620.acf").write_text('"buildid" "123"')
            runtime.settings.save(type(runtime.settings.load())(game_path=str(game.parent)))
            findings = runtime.troubleshooter.scan()
            self.assertTrue(any(item.key == "package-tested.mod" for item in findings))

    def test_catalog_export_excludes_local_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            export = runtime.catalog.build()
            self.assertEqual(export["schema_version"], 1)
            self.assertIn("knowledge", export)
            self.assertTrue(all(item["path"] is None for item in export["modules"]))

    def test_catalog_export_writes_json_document(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            destination = runtime.catalog.export(Path(temp) / "out" / "catalog.json")
            self.assertTrue(destination.is_file())
            self.assertIn('"schema_version": 1', destination.read_text(encoding="utf-8"))

    def test_knowledge_search_filters_catalog(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            self.assertEqual([item.id for item in runtime.knowledge.search("profiles")], ["profiles"])

    def test_troubleshooter_scan_is_read_only_and_repeatable(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            first = runtime.troubleshooter.scan()
            second = runtime.troubleshooter.scan()
            self.assertEqual(first, second)

    def test_module_catalog_exposes_capabilities(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            self.assertTrue(any("trainer" in item for item in runtime.modules.discover()["embervault.trainer"].capabilities))

    def test_backend_guarded_research_launch_tracks_success(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.selectProfile(1)
            backend.launchResearchWorker()
            self.assertIn("Completed guarded research worker", backend.lastSaveMessage)

    def test_backend_guarded_launch_reports_stable_profile_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.launchResearchWorker()
            self.assertIn("Research profile", backend.lastSaveMessage)

    def test_backend_guarded_launch_terminates_timeout(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            process = Mock()
            process.communicate.side_effect = [subprocess.TimeoutExpired("worker", 15), ("", None)]
            backend.launcher = Mock()
            backend.launcher.launch.return_value = process
            backend.selectProfile(1)
            backend.launchResearchWorker()
            process.kill.assert_called_once_with()
            self.assertIn("timed out and was terminated", backend.lastSaveMessage)

    def test_backend_workspace_lists_are_profile_scoped(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.research.create("Stable note", "Stable hypothesis", "default")
            runtime.research.create("Research note", "Research hypothesis", "research")
            runtime.content.create("Stable project", "default", "Stable brief")
            runtime.content.create("Research project", "research", "Research brief")
            runtime.characters.create("Stable character", "default")
            runtime.characters.create("Research character", "research")
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            self.assertEqual(len(backend.researchOptions), 1)
            self.assertEqual(len(backend.contentOptions), 1)
            self.assertEqual(len(backend.characterOptions), 1)
            backend.selectProfile(1)
            self.assertIn("Research note", backend.researchOptions[0])
            self.assertIn("Research project", backend.contentOptions[0])
            self.assertIn("Research character", backend.characterOptions[0])

    def test_content_project_is_stored_outside_game_and_save_state(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Ashen Furniture", "research", "A modular furniture experiment")
            self.assertEqual(project.profile_id, "research")
            self.assertEqual(project.description, "A modular furniture experiment")
            self.assertEqual(runtime.saves.list_backups(), [])

    def test_content_project_cannot_be_ready_without_brief(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Unspecified", "research")
            with self.assertRaises(ValueError):
                runtime.content.set_status(project.id, "ready")

    def test_research_evidence_can_be_appended_to_record(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Test", "Observe", "research")
            updated = runtime.research.add_evidence(record.id, "Observed result")
            self.assertEqual(updated.evidence, ["Observed result"])

    def test_research_cannot_complete_without_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Test", "Observe", "research")
            with self.assertRaises(ValueError):
                runtime.research.set_status(record.id, "completed")
            runtime.research.add_evidence(record.id, "Observed")
            self.assertEqual(runtime.research.set_status(record.id, "completed").status, "completed")

    def test_character_project_can_stage_valid_level(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default")
            updated = runtime.characters.stage_level(record.id, 12)
            self.assertEqual(updated.planned_level, 12)

    def test_content_project_supports_guarded_status(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Furniture", "research", "Test furniture brief")
            self.assertEqual(runtime.content.set_status(project.id, "ready").status, "ready")

    def test_character_project_is_separate_from_save_manager(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default")
            self.assertEqual(record.profile_id, "default")
            self.assertEqual(runtime.saves.list_backups(), [])


if __name__ == "__main__":
    unittest.main()
