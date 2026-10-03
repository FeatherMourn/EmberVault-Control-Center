import hashlib
import tempfile
import unittest
import base64
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from pathlib import Path

from core.distribution import DistributionService, ReleaseManifest


class DistributionUpdateTests(unittest.TestCase):
    def test_manifest_requires_valid_checksum_and_round_trips(self):
        digest = "a" * 64
        manifest = ReleaseManifest.from_dict({"version": "1.1.0", "channel": "stable",
            "platform": "windows", "package_name": "update.zip", "sha256": digest})
        self.assertEqual(manifest.to_dict()["sha256"], digest)
        with self.assertRaises(ValueError):
            ReleaseManifest.from_dict({"version": "1", "channel": "stable", "platform": "windows",
                "package_name": "update.zip", "sha256": "bad"})

    def test_update_is_review_only_and_verified_package_can_be_staged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "update.zip"
            package.write_bytes(b"signed later")
            digest = hashlib.sha256(package.read_bytes()).hexdigest()
            manifest = ReleaseManifest.from_dict({"version": "1.1.0", "channel": "stable",
                "platform": "windows", "package_name": package.name, "sha256": digest})
            manifest.signature = "test-signature"
            service = DistributionService(root, signature_verifier=lambda item: item.signature == "test-signature")
            result = service.check_update("1.0.0", manifest.to_dict())
            self.assertTrue(result["available"])
            self.assertEqual(result["application_state"], "review-only")
            staged = service.stage_package(package, manifest)
            self.assertTrue(staged.is_file())
            self.assertEqual(staged.read_bytes(), package.read_bytes())

    def test_corrupt_package_is_rejected_without_live_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            package = root / "update.zip"
            package.write_bytes(b"corrupt")
            manifest = ReleaseManifest(version="1.1.0", channel="stable", platform="windows",
                package_name=package.name, sha256="b" * 64, signature="test-signature")
            service = DistributionService(root, signature_verifier=lambda item: True)
            with self.assertRaises(ValueError):
                service.stage_package(package, manifest)
            self.assertFalse((root / "distribution" / "staged").exists())

    def test_unsigned_package_is_rejected_and_recorded(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); package = root / "update.zip"; package.write_bytes(b"data")
            manifest = ReleaseManifest(version="1.1.0", channel="stable", platform="windows",
                package_name=package.name, sha256=hashlib.sha256(package.read_bytes()).hexdigest())
            service = DistributionService(root, signature_verifier=lambda item: True)
            with self.assertRaises(ValueError):
                service.stage_package(package, manifest)
            self.assertIn('"status": "rejected"', service.history_path.read_text())

    def test_ed25519_signature_verifies_and_tampering_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); package = root / "update.zip"; package.write_bytes(b"data")
            private = Ed25519PrivateKey.generate()
            public = private.public_key().public_bytes_raw()
            manifest = ReleaseManifest(version="1.1.0", channel="stable", platform="windows",
                package_name=package.name, sha256=hashlib.sha256(package.read_bytes()).hexdigest())
            manifest.signature = "release-2026:" + base64.b64encode(private.sign(manifest.signing_bytes())).decode()
            service = DistributionService(root, trusted_keys={"release-2026": base64.b64encode(public).decode()})
            self.assertTrue(service.verify_signature(manifest))
            manifest.version = "1.2.0"
            self.assertFalse(service.verify_signature(manifest))

    def test_feed_discovery_reports_incompatible_release_without_installing(self):
        with tempfile.TemporaryDirectory() as temp:
            service = DistributionService(Path(temp))
            feed = {"release": {"version": "2.0.0", "channel": "stable", "platform": "windows",
                "package_name": "update.zip", "sha256": "a" * 64, "minimum_core_version": "9.0.0"}}
            result = service.discover_feed("1.0.0", feed, core_version="1.0.0")
            self.assertEqual(result["state"], "incompatible")
            self.assertFalse((Path(temp) / "distribution" / "staged").exists())


if __name__ == "__main__":
    unittest.main()
