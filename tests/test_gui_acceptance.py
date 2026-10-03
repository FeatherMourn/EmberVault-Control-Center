import os
import subprocess
import sys
import unittest
from pathlib import Path


class GuiAcceptanceTests(unittest.TestCase):
    def test_source_declares_all_primary_pages_and_dashboard_bindings(self):
        qml = (Path(__file__).parents[1] / "ui" / "Main.qml").read_text(encoding="utf-8")
        for page in ("HomePage", "PackagesPage", "ActivityPage", "ModulesPage"):
            self.assertIn(f"component {page}", qml)
        for binding in ("dashboardHealth", "activitySummary", "updateTrustStatus", "operationDetails"):
            self.assertIn(f"controlCenter.{binding}", qml)

    @unittest.skipUnless(os.environ.get("CI") or os.environ.get("QT_QPA_PLATFORM") == "offscreen", "requires an offscreen Qt display")
    def test_windowed_smoke_startup_exits_cleanly(self):
        env = os.environ.copy()
        env["QT_QPA_PLATFORM"] = "offscreen"
        result = subprocess.run([sys.executable, "-m", "control_center.app", "--smoke-test"],
                                cwd=Path(__file__).parents[1], env=env, timeout=30,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(os.environ.get("QT_QPA_PLATFORM") == "offscreen", "requires an offscreen Qt display")
    def test_qml_shell_supports_home_to_activity_navigation(self):
        from PySide6.QtCore import QUrl
        from PySide6.QtQml import QQmlApplicationEngine
        from PySide6.QtWidgets import QApplication
        from core.application import EmbervaultRuntime
        from control_center.backend import ControlCenterBackend
        app = QApplication.instance() or QApplication([])
        root = Path(__file__).parents[1]
        runtime = EmbervaultRuntime.create(Path(self.id().replace(".", "_") + "-data"))
        backend = ControlCenterBackend(runtime.root, runtime=runtime)
        backend.refresh()
        engine = QQmlApplicationEngine()
        engine.rootContext().setContextProperty("controlCenter", backend)
        engine.load(QUrl.fromLocalFile(str(root / "ui" / "Main.qml")))
        self.assertTrue(engine.rootObjects())
        window = engine.rootObjects()[0]
        self.assertEqual(window.property("page"), 0)
        window.setProperty("page", 11)
        app.processEvents()
        self.assertEqual(window.property("page"), 11)
        self.assertTrue(backend.activitySummary)


if __name__ == "__main__":
    unittest.main()
