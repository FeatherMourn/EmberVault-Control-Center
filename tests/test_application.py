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


if __name__ == "__main__":
    unittest.main()
