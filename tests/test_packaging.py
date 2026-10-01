import unittest
from pathlib import Path


class PackagingContractTests(unittest.TestCase):
    def test_release_assets_exist(self):
        root = Path(__file__).resolve().parents[1]
        for relative in (
            "ui/Main.qml",
            "contracts/module-manifest.schema.json",
            "knowledge/entries.json",
            "modules/example/module.json",
            "packages/example-mod/package.json",
        ):
            self.assertTrue((root / relative).is_file(), relative)

    def test_data_file_layout_matches_setuptools_wheel_convention(self):
        root = Path(__file__).resolve().parents[1]
        self.assertIn('"ui" = ["ui/Main.qml"]', (root / "pyproject.toml").read_text(encoding="utf-8"))

    def test_seed_assets_have_installed_prefix_fallbacks(self):
        root = Path(__file__).resolve().parents[1]
        for relative in ("core/knowledge.py", "core/modules.py", "core/packages.py"):
            text = (root / relative).read_text(encoding="utf-8")
            self.assertIn("sys.prefix", text)


if __name__ == "__main__":
    unittest.main()
