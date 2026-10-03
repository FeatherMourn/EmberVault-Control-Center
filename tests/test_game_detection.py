import tempfile
import unittest
from pathlib import Path

from core.game_detection import GameDetector


class SteamDiscoveryTests(unittest.TestCase):
    def test_reads_custom_steam_libraries_and_discovers_multiple_installs(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); steam = root / "Steam"; steam_apps = steam / "steamapps"
            steam_apps.mkdir(parents=True)
            library = root / "Library Two"; (library / "steamapps" / "common" / "Enshrouded").mkdir(parents=True)
            (library / "steamapps" / "common" / "Enshrouded" / "Enshrouded.exe").write_bytes(b"")
            primary = steam / "steamapps" / "common" / "Enshrouded"; primary.mkdir(parents=True)
            (primary / "Enshrouded.exe").write_bytes(b"")
            steam_apps.joinpath("libraryfolders.vdf").write_text(
                '"libraryfolders" { "0" { "path" "' + str(library).replace("\\", "\\\\") + '" } }', encoding="utf-8")
            found = GameDetector().discover_steam([steam])
            self.assertEqual(len(found), 2)
            self.assertEqual({item.path for item in found}, {primary.resolve(), (library / "steamapps" / "common" / "Enshrouded").resolve()})

    def test_missing_library_configuration_is_read_only_and_empty(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(GameDetector.steam_library_roots(Path(temp)), [])


if __name__ == "__main__":
    unittest.main()
