import tempfile
import unittest
from pathlib import Path

from core.application import EmbervaultRuntime


class ApplicationCompositionTests(unittest.TestCase):
    def test_runtime_composes_services_and_reports_health(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            health = runtime.health()
            self.assertEqual(health["core"], "ready")
            self.assertEqual(health["profiles"], 2)
            self.assertEqual(health["modules"], 2)
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

    def test_content_project_is_stored_outside_game_and_save_state(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Ashen Furniture", "research")
            self.assertEqual(project.profile_id, "research")
            self.assertEqual(runtime.saves.list_backups(), [])

    def test_research_evidence_can_be_appended_to_record(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Test", "Observe", "research")
            updated = runtime.research.add_evidence(record.id, "Observed result")
            self.assertEqual(updated.evidence, ["Observed result"])

    def test_character_project_can_stage_valid_level(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default")
            updated = runtime.characters.stage_level(record.id, 12)
            self.assertEqual(updated.planned_level, 12)

    def test_character_project_is_separate_from_save_manager(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default")
            self.assertEqual(record.profile_id, "default")
            self.assertEqual(runtime.saves.list_backups(), [])


if __name__ == "__main__":
    unittest.main()
