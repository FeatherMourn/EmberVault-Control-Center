import tempfile
import unittest
from pathlib import Path

from core.application import EmbervaultRuntime


class CommunitySyncTests(unittest.TestCase):
    def test_submission_is_staged_and_previewed_without_publishing(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            service = runtime.community_sync
            path = service.stage_record("research", "record-1", 1, {"title": "Safe study"})
            records = service.list_submissions()
            self.assertEqual(records[0]["state"], "website-review-required")
            preview = service.preview_submission(__import__('json').loads(path.read_text()))
            self.assertTrue(preview["review_required"])
            self.assertFalse(preview["automatic_publish"])

    def test_submission_preview_rejects_non_website_authority(self):
        with tempfile.TemporaryDirectory() as temp:
            service = EmbervaultRuntime.create(Path(temp)).community_sync
            with self.assertRaises(ValueError):
                service.preview_submission({"authority": "local", "payload": {}})


if __name__ == "__main__":
    unittest.main()
