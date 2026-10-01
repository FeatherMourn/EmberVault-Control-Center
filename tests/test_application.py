import json
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock
from pathlib import Path

from core.application import EmbervaultRuntime
from control_center.backend import ControlCenterBackend


class ApplicationCompositionTests(unittest.TestCase):
    def test_runtime_composes_services_and_reports_health(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            health = runtime.health()
            self.assertEqual(health["core"], "ready")
            self.assertEqual(health["profiles"], 2)
            self.assertEqual(health["modules"], 5)
            self.assertEqual(health["backups"], 0)
            self.assertEqual(health["research"], 0)
            self.assertEqual(health["knowledge"], 8)
            self.assertEqual(health["content_projects"], 0)
            self.assertEqual(health["trainer_plans"], 0)

    def test_backend_exposes_workspace_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            self.assertIn("Research · 0 records", backend.workspaceSummary)
            self.assertIn("Knowledge · 8 entries", backend.workspaceSummary)
            self.assertIn("Content · 0 projects", backend.workspaceSummary)
            self.assertIn("Trainer · 0 plans", backend.workspaceSummary)

    def test_backend_exposes_selected_profile_index(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            self.assertEqual(backend.selectedProfileIndex, 0)
            backend.selectProfile(1)
            self.assertEqual(backend.selectedProfileIndex, 1)

    def test_backend_imports_staged_settings_for_selected_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            backend = ControlCenterBackend(root, runtime=runtime)
            profile = runtime.profiles.list()[0]
            manifest = root / "settings.json"
            manifest.write_text(json.dumps({
                "schema_version": 1,
                "profile_id": profile.id,
                "application_state": "staged-only",
                "settings": {
                    "enemy_damage_multiplier": 1.25,
                    "resource_yield_multiplier": 1.0,
                    "experimental_rules": False,
                    "base_crit_chance": 0.1,
                },
            }), encoding="utf-8")
            backend.importGameSettings(str(manifest))
            self.assertIn("Imported staged settings", backend.lastSaveMessage)
            selected = next(item for item in backend.profiles if item.id == profile.id)
            self.assertEqual(selected.settings["enemy_damage_multiplier"], 1.25)
            self.assertEqual(backend.operations.list_recent(1)[0].operation_type, "game-settings-import")

    def test_backend_requires_restore_preview_before_restore(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend._selected_backup_id = "unpreviewed"
            backend._save_directory = temp
            backend.restoreSelected()
            self.assertIn("Preview the selected restore", backend.lastSaveMessage)
            self.assertFalse(backend.canRestore)

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

    def test_research_summary_export_excludes_profile_and_evidence_text(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Yield test", "Test staged yield", "research")
            runtime.research.add_evidence(record.id, "Private observation")
            destination = runtime.research.export_summary(runtime.research.list()[0])
            payload = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(payload["application_state"], "research-summary")
            self.assertEqual(payload["record"]["evidence_count"], 1)
            self.assertNotIn("profile_id", payload["record"])
            self.assertNotIn("Private observation", destination.read_text(encoding="utf-8"))

    def test_knowledge_catalog_searches_seeded_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            entries = runtime.knowledge.search("restore")
            self.assertEqual([entry.id for entry in entries], ["save-safety"])

    def test_knowledge_entry_creation_preserves_seeded_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            seeded_count = len(runtime.knowledge.entries())
            entry = runtime.knowledge.create("Local Finding", "Research", "A local summary", "Observed during a safe probe.")
            self.assertEqual(len(runtime.knowledge.entries()), seeded_count + 1)
            self.assertEqual(runtime.knowledge.search("safe probe")[0].id, entry.id)

    def test_local_knowledge_requires_explicit_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            entry = runtime.knowledge.create("Private Finding", "Research", "Private summary", "Private observation")
            self.assertNotIn(entry.id, [item["id"] for item in runtime.catalog.build()["knowledge"]])
            runtime.knowledge.publish(entry.id)
            self.assertIn(entry.id, [item["id"] for item in runtime.catalog.build()["knowledge"]])
            runtime.knowledge.unpublish(entry.id)
            self.assertNotIn(entry.id, [item["id"] for item in runtime.catalog.build()["knowledge"]])

    def test_troubleshooter_flags_package_with_unsupported_build(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            package = root / "packages" / "tested"
            package.mkdir(parents=True)
            (package / "package.json").write_text(
                '{"id":"tested.mod","name":"Tested Mod","version":"1.0.0","required_builds":["old-build"]}'
            )
            game = root / "game" / "steamapps"
            game.mkdir(parents=True)
            (game.parent / "Enshrouded.exe").write_bytes(b"")
            (game / "appmanifest_1203620.acf").write_text('"buildid" "123"')
            runtime.settings.save(type(runtime.settings.load())(game_path=str(game.parent)))
            findings = runtime.troubleshooter.scan()
            self.assertTrue(any(item.key == "package-tested.mod" for item in findings))

    def test_troubleshooter_flags_deployment_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            source = root / "incoming"
            source.mkdir()
            (source / "package.json").write_text(json.dumps({"id": "conflict.mod", "name": "Conflict", "version": "1.0"}))
            package = runtime.packages.install_from_directory(source)
            profile = runtime.profiles.list()[0]
            runtime.packages.set_enabled(profile, package.id, True)
            game = root / "game"
            (game / "mods" / package.id).mkdir(parents=True)
            runtime.settings.save(type(runtime.settings.load())(game_path=str(game)))
            findings = runtime.troubleshooter.scan()
            self.assertTrue(any(item.key == "deployment-default-conflict.mod" for item in findings))

    def test_game_detection_treats_malformed_manifest_as_unknown_build(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            steamapps = root / "steamapps"
            steamapps.mkdir()
            (steamapps / "appmanifest_1203620.acf").write_text('"buildid" "not-a-number"')
            installation = EmbervaultRuntime.create(Path(temp)).game.detect(root)
            self.assertIsNone(installation.build_id)

    def test_game_detection_reports_missing_build_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Enshrouded.exe").write_bytes(b"")
            runtime = EmbervaultRuntime.create(Path(temp))
            installation = runtime.game.detect(root)
            self.assertIn("build evidence", " ".join(runtime.game.validate(installation)).lower())

    def test_troubleshooter_flags_missing_package_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            package = root / "packages" / "addon.mod"
            package.mkdir(parents=True)
            (package / "package.json").write_text(json.dumps({
                "id": "addon.mod", "name": "Addon", "version": "1.0", "dependencies": ["missing.mod"],
            }))
            findings = runtime.troubleshooter.scan()
            self.assertTrue(any(item.key == "package-dependency-addon.mod" for item in findings))

    def test_troubleshooter_flags_package_dependency_cycle(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            for package_id, dependency in (("alpha.mod", "beta.mod"), ("beta.mod", "alpha.mod")):
                package = root / "packages" / package_id
                package.mkdir(parents=True)
                (package / "package.json").write_text(json.dumps({
                    "id": package_id, "name": package_id, "version": "1.0", "dependencies": [dependency],
                }))
            findings = runtime.troubleshooter.scan()
            self.assertTrue(any(item.key == "package-dependency-cycle" for item in findings))

    def test_catalog_export_excludes_local_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            export = runtime.catalog.build()
            self.assertEqual(export["schema_version"], 1)
            self.assertEqual(export["contract_versions"]["package_manifest"], 1)
            self.assertIn("knowledge", export)
            self.assertTrue(all(item["path"] is None for item in export["modules"]))

    def test_catalog_export_includes_sanitized_research_summary(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Yield study", "Observe yield", "research")
            runtime.research.add_evidence(record.id, "private local observation")
            self.assertEqual(runtime.catalog.build()["research"], [])
            runtime.research.set_status(record.id, "completed")
            runtime.research.publish(record.id)
            research = runtime.catalog.build()["research"]
            self.assertEqual(research[0]["evidence_count"], 1)
            self.assertNotIn("private local observation", json.dumps(research))
            self.assertNotIn("profile_id", research[0])
            self.assertEqual(set(research[0]), {"id", "title", "hypothesis", "status", "evidence_count", "created_at", "published_at"})
            self.assertTrue(research[0]["published_at"])

    def test_research_publish_requires_completion_and_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Private", "Do not publish yet", "research")
            with self.assertRaises(ValueError):
                runtime.research.publish(record.id)

    def test_research_can_be_unpublished_without_losing_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Public", "Documented", "research")
            runtime.research.add_evidence(record.id, "Observed")
            runtime.research.set_status(record.id, "completed")
            published = runtime.research.publish(record.id)
            unpublished = runtime.research.unpublish(record.id)
            self.assertTrue(published.published)
            self.assertFalse(unpublished.published)
            self.assertEqual(unpublished.published_at, "")
            self.assertEqual(unpublished.evidence, ["Observed"])
            self.assertEqual(runtime.catalog.build()["research"], [])

    def test_research_options_show_private_or_published_state(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            record = runtime.research.create("Visible", "Documented", "research")
            runtime.research.add_evidence(record.id, "Observed")
            runtime.research.set_status(record.id, "completed")
            backend = ControlCenterBackend(root, runtime=runtime)
            backend.selectProfile(1)
            self.assertIn("PRIVATE", backend.researchOptions[0])
            runtime.research.publish(record.id)
            self.assertIn("PUBLISHED", backend.researchOptions[0])

    def test_published_research_retracts_when_evidence_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Mutable", "Documented", "research")
            runtime.research.add_evidence(record.id, "Initial")
            runtime.research.set_status(record.id, "completed")
            runtime.research.publish(record.id)
            updated = runtime.research.add_evidence(record.id, "Correction")
            self.assertFalse(updated.published)
            self.assertEqual(updated.published_at, "")
            self.assertEqual(runtime.catalog.build()["research"], [])

    def test_catalog_export_writes_json_document(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            destination = runtime.catalog.export(Path(temp) / "out" / "catalog.json")
            self.assertTrue(destination.is_file())
            self.assertIn('"schema_version": 1', destination.read_text(encoding="utf-8"))
            self.assertIn('"generated_at":', destination.read_text(encoding="utf-8"))

    def test_catalog_declares_tuning_adapter_contract_version(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            self.assertEqual(runtime.catalog.build()["contract_versions"]["tuning_adapter"], 1)

    def test_eml_tuning_adapter_loads_existing_reversible_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            adapter_dir = root / "adapters"
            adapter_dir.mkdir()
            source = Path(__file__).parents[1] / "adapters" / "eml-balancing-table.json"
            (adapter_dir / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            from core.tuning_adapter import TuningAdapterService
            manifest = TuningAdapterService(root).manifest()
            self.assertEqual(manifest["supported_setting_keys"], ["baseCritChance"])

    def test_catalog_sync_writes_repository_ready_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            destination = runtime.catalog.sync_to_directory(Path(temp) / "website" / "public")
            self.assertEqual(destination.name, "embervault-catalog.json")
            self.assertTrue(destination.is_file())
            self.assertEqual(json.loads(destination.read_text(encoding="utf-8"))["schema_version"], 1)

    def test_standalone_catalog_verifier_accepts_and_rejects_snapshots(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            catalog = runtime.catalog.export(root / "catalog.json")
            verifier = Path(__file__).resolve().parents[1] / "tools" / "verify_catalog.py"
            valid = subprocess.run([sys.executable, str(verifier), str(catalog)], capture_output=True, text=True)
            self.assertEqual(valid.returncode, 0, valid.stdout + valid.stderr)
            payload = json.loads(catalog.read_text(encoding="utf-8"))
            payload["contract_versions"]["tuning_adapter"] = 0
            invalid = root / "invalid-catalog.json"
            invalid.write_text(json.dumps(payload), encoding="utf-8")
            rejected = subprocess.run([sys.executable, str(verifier), str(invalid)], capture_output=True, text=True)
            self.assertNotEqual(rejected.returncode, 0)

    def test_sync_catalog_command_writes_validated_snapshot(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            tool = Path(__file__).resolve().parents[1] / "tools" / "sync_catalog.py"
            destination = root / "website"
            result = subprocess.run(
                [sys.executable, str(tool), str(destination), "--data-root", str(root / "runtime")],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((destination / "embervault-catalog.json").is_file())

    def test_catalog_validation_rejects_private_research_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            payload = runtime.catalog.build()
            payload["research"].append({"id": "private", "evidence": ["secret"]})
            with self.assertRaises(ValueError):
                runtime.catalog.validate(payload)

    def test_catalog_validation_rejects_unsanitized_knowledge_records(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            payload = runtime.catalog.build()
            payload["knowledge"].append({"id": "private", "content": "secret", "profile_id": "research"})
            with self.assertRaises(ValueError):
                runtime.catalog.validate(payload)

    def test_catalog_validation_requires_all_contract_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            payload = runtime.catalog.build()
            del payload["contract_versions"]["content_project"]
            with self.assertRaisesRegex(ValueError, "content_project"):
                runtime.catalog.validate(payload)

    def test_catalog_validation_rejects_zero_contract_versions(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            payload = runtime.catalog.build()
            payload["contract_versions"]["research_record"] = 0
            with self.assertRaisesRegex(ValueError, "research_record"):
                runtime.catalog.validate(payload)

    def test_catalog_validation_rejects_identitiless_module_records(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            payload = runtime.catalog.build()
            payload["modules"].append({"name": "Missing identity"})
            with self.assertRaises(ValueError):
                runtime.catalog.validate(payload)

    def test_catalog_validation_rejects_invalid_module_process_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            payload = runtime.catalog.build()
            payload["modules"][0]["process_mode"] = "unknown"
            with self.assertRaises(ValueError):
                runtime.catalog.validate(payload)

    def test_catalog_export_orders_public_records_by_id(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            export = runtime.catalog.build()
            self.assertEqual([item["id"] for item in export["modules"]], sorted(item["id"] for item in export["modules"]))
            self.assertEqual([item["id"] for item in export["knowledge"]], sorted(item["id"] for item in export["knowledge"]))

    def test_knowledge_search_filters_catalog(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            self.assertEqual([item.id for item in runtime.knowledge.search("profiles")], ["profiles"])

    def test_troubleshooter_scan_is_read_only_and_repeatable(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            first = runtime.troubleshooter.scan()
            second = runtime.troubleshooter.scan()
            self.assertEqual(first, second)

    def test_module_catalog_exposes_capabilities(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            self.assertTrue(any("trainer" in item for item in runtime.modules.discover()["embervault.trainer"].capabilities))

    def test_backend_inspects_embedded_modules_with_operation_tracking(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.inspectEmbeddedModules()
            self.assertIn("Inspected 1 embedded module", backend.lastSaveMessage)
            self.assertTrue(any(item.operation_type == "embedded-module-inspection"
                                and item.status == "succeeded"
                                for item in backend.operations.list_recent()))

    def test_package_options_show_package_type(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            self.assertTrue(any("mod" in item for item in backend.packageOptions))

    def test_backend_exposes_read_only_deployment_plan(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.settings.game_path = temp
            self.assertTrue(any("enabled" in item.lower() or "ready" in item.lower()
                                for item in backend.deploymentOptions))
            backend.inspectDeploymentPlan()
            self.assertIn("Deployment plan", backend.lastSaveMessage)
            self.assertTrue(any("package-deployment-plan" in item for item in backend.recentOperations))

    def test_backend_exposes_external_mods_from_configured_game_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            runtime = EmbervaultRuntime.create(root)
            mods = root / "game" / "mods" / "outside"
            mods.mkdir(parents=True)
            (mods / "mod.json").write_text(json.dumps({
                "id": "outside.mod", "name": "Outside", "version": "1.0",
            }))
            backend = ControlCenterBackend(root, runtime=runtime)
            backend.settings.game_path = str(root / "game")
            self.assertTrue(any("Outside" in item for item in backend.externalPackageOptions))

    def test_backend_deploys_ready_packages_to_configured_game_folder(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.settings.game_path = temp
            self.assertFalse(backend.canDeploy)
            backend.inspectDeploymentPlan()
            self.assertTrue(backend.canDeploy)
            backend.deployReadyPackages()
            self.assertIn("Deployed 0 package", backend.lastSaveMessage)

    def test_backend_requires_current_deployment_plan_before_deploy(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.settings.game_path = temp
            backend.deployReadyPackages()
            self.assertIn("Inspect the current deployment plan", backend.lastSaveMessage)
            self.assertFalse(backend.canDeploy)

    def test_backend_undeploy_refuses_unowned_destination(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.settings.game_path = temp
            backend.undeployPackage(0)
            self.assertIn("does not exist", backend.lastSaveMessage)

    def test_module_options_show_version_and_publisher(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            self.assertTrue(any("v0.1.0" in item and "EmberVault" in item and "embedded" in item for item in backend.moduleOptions))
            self.assertTrue(any("v0.1.0" in item and "EmberVault" in item and "separate" in item for item in backend.moduleOptions))

    def test_backend_guarded_research_launch_tracks_success(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.selectProfile(1)
            backend.launchResearchWorker()
            self.assertIn("Completed guarded research worker", backend.lastSaveMessage)

    def test_backend_research_probe_persists_evidence_on_latest_record(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Probe", "Observe environment", "research")
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.selectProfile(1)
            backend.launchResearchWorker()
            updated = next(item for item in runtime.research.list() if item.id == record.id)
            self.assertTrue(any(item.startswith("worker observation:") for item in updated.evidence))

    def test_backend_guarded_worker_receives_configured_game_path(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.settings.game_path = "C:/Configured/Enshrouded"
            backend.selectProfile(1)
            backend.launchResearchWorker()
            self.assertIn("C:/Configured/Enshrouded", backend.lastSaveMessage)

    def test_backend_guarded_launch_reports_stable_profile_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.launchResearchWorker()
            self.assertIn("Research profile", backend.lastSaveMessage)

    def test_backend_guarded_launch_terminates_timeout(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            process = Mock()
            process.communicate.side_effect = [subprocess.TimeoutExpired("worker", 15), ("", None)]
            backend.launcher = Mock()
            backend.launcher.launch.return_value = process
            backend.selectProfile(1)
            backend.launchResearchWorker()
            process.kill.assert_called_once_with()
            self.assertIn("timed out and was terminated", backend.lastSaveMessage)
            self.assertIn("Guarded module timed out", (Path(temp) / "logs" / "events.jsonl").read_text(encoding="utf-8"))

    def test_backend_rejects_invalid_worker_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            process = Mock(returncode=0)
            process.communicate.return_value = ('{"status":"ready"}', None)
            backend.launcher = Mock()
            backend.launcher.launch.return_value = process
            backend.selectProfile(1)
            backend.launchResearchWorker()
            self.assertIn("invalid", backend.lastSaveMessage.lower())

    def test_backend_rejects_worker_context_mismatch(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            process = Mock(returncode=0)
            process.communicate.return_value = ('{"contract_version":1,"status":"ready","read_only":true,"profile":"wrong","operation":"wrong"}', None)
            backend.launcher = Mock()
            backend.launcher.launch.return_value = process
            backend.selectProfile(1)
            backend.launchResearchWorker()
            self.assertIn("invalid", backend.lastSaveMessage.lower())

    def test_backend_rejects_oversized_worker_output(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            process = Mock(returncode=0)
            process.communicate.return_value = ("x" * (1024 * 1024 + 1), None)
            backend.launcher = Mock()
            backend.launcher.launch.return_value = process
            backend.selectProfile(1)
            backend.launchResearchWorker()
            self.assertIn("too much output", backend.lastSaveMessage)

    def test_backend_rejects_worker_missing_schema_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            process = Mock(returncode=0)
            process.communicate.return_value = ('{"contract_version":1,"status":"ready","read_only":true,"profile":"research","operation":"x"}', None)
            backend.launcher = Mock()
            backend.launcher.launch.return_value = process
            backend.selectProfile(1)
            backend.launchResearchWorker()
            self.assertIn("invalid", backend.lastSaveMessage.lower())

    def test_backend_workspace_lists_are_profile_scoped(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.research.create("Stable note", "Stable hypothesis", "default")
            runtime.research.create("Research note", "Research hypothesis", "research")
            runtime.content.create("Stable project", "default", "Stable brief")
            runtime.content.create("Research project", "research", "Research brief")
            runtime.characters.create("Stable character", "default")
            runtime.characters.create("Research character", "research")
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            self.assertEqual(len(backend.researchOptions), 1)
            self.assertEqual(len(backend.contentOptions), 1)
            self.assertEqual(len(backend.characterOptions), 1)
            backend.selectProfile(1)
            self.assertIn("Research note", backend.researchOptions[0])
            self.assertIn("Research project", backend.contentOptions[0])
            self.assertIn("Research character", backend.characterOptions[0])

    def test_backend_profile_deletion_protects_owned_records(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            profile = runtime.profiles.create_custom("Scratch")
            runtime.research.create("Owned", "Keep it", profile.id)
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.selectProfile(2)
            backend.deleteActiveProfile()
            self.assertIn("owns project records", backend.lastSaveMessage)
            self.assertTrue(any(item.id == profile.id for item in backend.profile_service.list()))

    def test_backend_diagnostics_runs_and_audits_scan(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            backend = ControlCenterBackend(Path(temp), runtime=runtime)
            backend.runDiagnostics()
            self.assertIn("attention finding(s)", backend.lastSaveMessage)
            self.assertTrue(any(item.operation_type == "troubleshooter-scan" for item in runtime.operations.list_recent()))
            log_text = (Path(temp) / "logs" / "events.jsonl").read_text(encoding="utf-8")
            self.assertIn("Troubleshooter scan completed", log_text)

    def test_fallback_backend_can_delete_custom_profile(self):
        with tempfile.TemporaryDirectory() as temp:
            backend = ControlCenterBackend(Path(temp))
            backend.profile_service.create_custom("Scratch")
            backend.profiles = backend.profile_service.list()
            backend.selectProfile(2)
            backend.deleteActiveProfile()
            self.assertIn("Deleted profile", backend.lastSaveMessage)

    def test_content_project_is_stored_outside_game_and_save_state(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Ashen Furniture", "research", "A modular furniture experiment", "furniture", "Oak frame; modular corner joint")
            self.assertEqual(project.profile_id, "research")
            self.assertEqual(project.description, "A modular furniture experiment")
            self.assertEqual(project.design_type, "furniture")
            self.assertIn("Oak frame", project.design_notes)
            self.assertEqual(runtime.saves.list_backups(), [])

    def test_content_project_export_is_design_only(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Ashen Furniture", "research", "A modular furniture experiment", "furniture", "Oak frame")
            destination = runtime.content.export(project)
            payload = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(payload["application_state"], "design-only")
            self.assertIn("published", payload["project"])
            self.assertIn("published_at", payload["project"])
            self.assertEqual(payload["project"]["id"], project.id)
            self.assertNotIn("game", destination.parts)

    def test_content_asset_references_are_relative_and_persisted(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Furniture", "research", "Brief", "furniture", "Oak", ["assets/chair.png"])
            self.assertEqual(project.asset_references, ["assets/chair.png"])
            with self.assertRaises(ValueError):
                runtime.content.update_design(project.id, "furniture", "Oak", ["..\\outside.png"])

    def test_content_project_publication_is_explicit_and_catalog_sanitized(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Furniture", "research", "A public design brief")
            self.assertEqual(runtime.catalog.build()["content_projects"], [])
            runtime.content.set_status(project.id, "ready")
            runtime.content.publish(project.id)
            public = runtime.catalog.build()["content_projects"]
            self.assertEqual(public[0]["id"], project.id)
            self.assertNotIn("description", public[0])
            runtime.content.unpublish(project.id)
            self.assertEqual(runtime.catalog.build()["content_projects"], [])

    def test_content_design_update_retracts_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Furniture", "research", "A public design brief", "furniture", "Oak frame")
            runtime.content.set_status(project.id, "ready")
            runtime.content.publish(project.id)
            updated = runtime.content.update_design(project.id, "building", "Stone arch variation")
            self.assertEqual(updated.design_type, "building")
            self.assertFalse(updated.published)
            self.assertEqual(runtime.catalog.build()["content_projects"], [])

    def test_content_project_cannot_be_ready_without_brief(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Unspecified", "research")
            with self.assertRaises(ValueError):
                runtime.content.set_status(project.id, "ready")

    def test_character_plan_export_is_save_safe(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "research", "Build plan")
            destination = runtime.characters.export(record)
            payload = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(payload["application_state"], "plan-only")
            self.assertEqual(payload["character"]["id"], record.id)
            self.assertNotIn("saves", destination.parts)

    def test_research_evidence_can_be_appended_to_record(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Test", "Observe", "research")
            updated = runtime.research.add_evidence(record.id, "Observed result")
            self.assertEqual(updated.evidence, ["Observed result"])

    def test_research_cannot_complete_without_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.research.create("Test", "Observe", "research")
            with self.assertRaises(ValueError):
                runtime.research.set_status(record.id, "completed")
            runtime.research.add_evidence(record.id, "Observed")
            self.assertEqual(runtime.research.set_status(record.id, "completed").status, "completed")

    def test_character_project_can_stage_valid_level(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default")
            updated = runtime.characters.stage_level(record.id, 12)
            self.assertEqual(updated.planned_level, 12)

    def test_content_project_supports_guarded_status(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            project = runtime.content.create("Furniture", "research", "Test furniture brief")
            self.assertEqual(runtime.content.set_status(project.id, "ready").status, "ready")

    def test_character_project_is_separate_from_save_manager(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default")
            self.assertEqual(record.profile_id, "default")
            self.assertEqual(runtime.saves.list_backups(), [])

    def test_character_level_rejects_boolean(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default")
            with self.assertRaises(ValueError):
                runtime.characters.stage_level(record.id, True)

    def test_character_project_preserves_planning_notes(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default", "Prioritize fire resistance")
            self.assertEqual(record.notes, "Prioritize fire resistance")

    def test_character_plan_notes_can_be_revised_without_save_mutation(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            record = runtime.characters.create("Ash", "default", "Initial plan")
            updated = runtime.characters.update_notes(record.id, "Revised progression plan")
            self.assertEqual(updated.notes, "Revised progression plan")
            self.assertEqual(runtime.saves.list_backups(), [])

    def test_trainer_plan_is_backup_bound_and_plan_only(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            profile = next(item for item in runtime.profiles.list() if item.id == "research")
            save_dir = Path(temp) / "save-source"
            save_dir.mkdir()
            (save_dir / "world.dat").write_text("safe", encoding="utf-8")
            backup = runtime.saves.backup(save_dir)
            plan = runtime.trainer.create(profile, "damage multiplier", "Read-only rehearsal", backup.id)
            destination = runtime.trainer.export(plan)
            payload = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(payload["application_state"], "trainer-plan-only")
            self.assertEqual(payload["plan"]["backup_id"], backup.id)

    def test_character_records_normalize_invalid_planned_level(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.characters.path.write_text(json.dumps([{
                "id": "EV-CHAR-BAD", "name": "Ash", "profile_id": "default", "planned_level": 999,
            }]))
            self.assertEqual(runtime.characters.list()[0].planned_level, 1)

    def test_character_records_skip_malformed_records(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.characters.path.write_text(json.dumps([
                {"id": "good", "name": "Ash", "profile_id": "default"},
                {"id": "bad", "profile_id": "default"},
            ]), encoding="utf-8")
            self.assertEqual([item.id for item in runtime.characters.list()], ["good"])

    def test_research_and_content_records_normalize_invalid_status(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.research.path.write_text(json.dumps([{
                "id": "EV-RES-BAD", "title": "Test", "hypothesis": "Test", "profile_id": "default",
                "status": "unknown", "evidence": "not-a-list",
            }]))
            runtime.content.path.write_text(json.dumps([{
                "id": "EV-CONTENT-BAD", "name": "Test", "profile_id": "default", "status": "unknown",
            }]))
            self.assertEqual(runtime.research.list()[0].status, "planned")
            self.assertEqual(runtime.research.list()[0].evidence, [])
            self.assertEqual(runtime.content.list()[0].status, "draft")

    def test_research_records_normalize_malformed_evidence_items(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.research.path.write_text(json.dumps([{
                "id": "EV-RES-EVIDENCE", "title": "Test", "hypothesis": "Test", "profile_id": "default",
                "status": "planned", "evidence": ["  observed  ", 12, "", "second"],
            }]))
            self.assertEqual(runtime.research.list()[0].evidence, ["observed", "second"])

    def test_research_and_content_skip_malformed_records(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.research.path.write_text(json.dumps([
                {"id": "good", "title": "Good", "hypothesis": "Test", "profile_id": "research"},
                {"id": "bad", "title": "Missing required fields"},
            ]), encoding="utf-8")
            runtime.content.path.write_text(json.dumps([
                {"id": "good", "name": "Good", "profile_id": "research"},
                {"id": "bad", "profile_id": "research"},
            ]), encoding="utf-8")
            self.assertEqual([item.id for item in runtime.research.list()], ["good"])
            self.assertEqual([item.id for item in runtime.content.list()], ["good"])

    def test_knowledge_skips_malformed_and_duplicate_entries(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = EmbervaultRuntime.create(Path(temp))
            runtime.knowledge.path.write_text(json.dumps([
                {"id": "valid", "title": " Valid ", "category": "Guide", "summary": "Summary", "content": "Content"},
                {"id": "broken", "title": "Missing content", "category": "Guide"},
                {"id": "valid", "title": "Duplicate", "category": "Guide", "summary": "Other", "content": "Other"},
                "not-an-entry",
            ]), encoding="utf-8")
            entries = runtime.knowledge.entries()
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].id, "valid")
            self.assertEqual(entries[0].title, "Valid")
            self.assertEqual(runtime.knowledge.path.parent.parent, Path(temp))


if __name__ == "__main__":
    unittest.main()
