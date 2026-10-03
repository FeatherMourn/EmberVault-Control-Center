import base64
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from core.distribution import DistributionService
from tools.sign_release import sign_manifest


class ReleaseSigningTests(unittest.TestCase):
    def test_signing_tool_emits_verifiable_manifest_without_private_key(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); unsigned = root / "unsigned.json"; signed = root / "signed.json"
            package = root / "update.zip"; package.write_bytes(b"release")
            unsigned.write_text(json.dumps({"version": "1.2.0", "channel": "stable", "platform": "windows",
                "package_name": package.name, "sha256": hashlib.sha256(package.read_bytes()).hexdigest()}), encoding="utf-8")
            private = Ed25519PrivateKey.generate(); private_path = root / "private.pem"
            private_path.write_bytes(private.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
            sign_manifest(unsigned, private_path, "test-key", signed)
            payload = json.loads(signed.read_text())
            self.assertTrue(payload["signature"].startswith("test-key:"))
            service = DistributionService(root, trusted_keys={"test-key": base64.b64encode(private.public_key().public_bytes_raw()).decode()})
            self.assertTrue(service.verify_signature(__import__('core.distribution', fromlist=['ReleaseManifest']).ReleaseManifest.from_dict(payload)))


if __name__ == "__main__":
    unittest.main()
