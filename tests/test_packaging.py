import unittest
from pathlib import Path


class PackagingContractTests(unittest.TestCase):
    def test_release_assets_exist(self):
        root = Path(__file__).resolve().parents[1]
        for relative in (
            "ui/Main.qml",
            "contracts/module-manifest.schema.json",
            "contracts/package-manifest.schema.json",
            "contracts/catalog.schema.json",
            "contracts/worker-result.schema.json",
            "knowledge/entries.json",
            "modules/example/module.json",
            "packages/example-mod/package.json",
        ):
            self.assertTrue((root / relative).is_file(), relative)

    def test_data_file_layout_matches_setuptools_wheel_convention(self):
        root = Path(__file__).resolve().parents[1]
        metadata = (root / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('"ui" = ["ui/Main.qml"]', metadata)
        self.assertIn('dependencies = ["PySide6>=6.8"]', metadata)

    def test_seed_assets_have_installed_prefix_fallbacks(self):
        root = Path(__file__).resolve().parents[1]
        for relative in ("core/knowledge.py", "core/modules.py", "core/packages.py"):
            text = (root / relative).read_text(encoding="utf-8")
            self.assertIn("sys.prefix", text)

    def test_contracts_declare_strict_manifest_entries(self):
        root = Path(__file__).resolve().parents[1]
        module_schema = (root / "contracts/module-manifest.schema.json").read_text(encoding="utf-8")
        package_schema = (root / "contracts/package-manifest.schema.json").read_text(encoding="utf-8")
        self.assertIn('"uniqueItems": true', module_schema)
        self.assertIn('"minLength": 1', module_schema)
        self.assertIn('"minLength": 1', package_schema)


if __name__ == "__main__":
    unittest.main()
