import base64
import json
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from core.distribution import DistributionService
from tools.package_signed_release import package_release


class SignedReleasePackageTests(unittest.TestCase):
    def test_package_release_emits_archive_and_publicly_verifiable_manifest(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); artifact = root / "EmberVaultControlCenter.exe"; artifact.write_bytes(b"exe")
            key = Ed25519PrivateKey.generate(); key_path = root / "release.pem"
            key_path.write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            manifest_path = package_release(artifact, "1.3.0", key_path, "release-test", root / "release")
            manifest = json.loads(manifest_path.read_text())
            public = base64.b64encode(key.public_key().public_bytes_raw()).decode()
            service = DistributionService(root, trusted_keys={"release-test": public})
            parsed = __import__('core.distribution', fromlist=['ReleaseManifest']).ReleaseManifest.from_dict(manifest)
            self.assertTrue(service.verify_signature(parsed))
            self.assertTrue((manifest_path.parent / manifest["package_name"]).is_file())


if __name__ == "__main__":
    unittest.main()
