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
            self.assertEqual(health["modules"], 0)
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


if __name__ == "__main__":
    unittest.main()
