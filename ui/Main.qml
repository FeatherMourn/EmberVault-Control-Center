import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Dialogs

ApplicationWindow {
    visible: true
    width: 1200
    height: 760
    minimumWidth: 900
    minimumHeight: 600
    title: "EmberVault Control Center"
    color: "#0d0c14"
    property color ink: "#edeaf4"
    property color muted: "#918da4"
    property color panel: "#15141e"
    property color line: "#2b2739"
    property color ember: "#ef8b4d"
    property int page: 0
    property var pageTitles: ["Home", "My Mods", "Game Settings", "Save Manager", "Troubleshooter", "Content Creator", "Research Lab", "Knowledge", "Profiles", "Characters", "Trainer", "Activity", "Modules", "Governance"]

    RowLayout {
        anchors.fill: parent
        spacing: 0
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 230
            color: "#100f18"
            ScrollView {
                anchors.fill: parent
                clip: true
                contentWidth: width
                ColumnLayout {
                    width: parent.width
                    anchors.margins: 20
                    spacing: 9
                    Text { text: "✦  EMBERVAULT"; color: ember; font.bold: true; font.pixelSize: 15 }
                    Text { text: "CONTROL CENTER"; color: muted; font.pixelSize: 10 }
                    Rectangle { Layout.fillWidth: true; height: 1; color: line; Layout.topMargin: 16; Layout.bottomMargin: 12 }
                    Text { text: "WORKSPACE"; color: muted; font.pixelSize: 10; font.letterSpacing: 1.3 }
                    NavButton { label: "Home"; pageIndex: 0 }
                    NavButton { label: "My Mods"; pageIndex: 1 }
                    NavButton { label: "Game Settings"; pageIndex: 2 }
                    NavButton { label: "Save Manager"; pageIndex: 3 }
                    NavButton { label: "Troubleshooter"; pageIndex: 4 }
                    Text { text: "TOOLS"; color: muted; font.pixelSize: 10; font.letterSpacing: 1.3; Layout.topMargin: 18 }
                    NavButton { label: "Content Creator"; pageIndex: 5 }
                    NavButton { label: "Research Lab"; pageIndex: 6 }
                    NavButton { label: "Knowledge"; pageIndex: 7 }
                    NavButton { label: "Profiles"; pageIndex: 8 }
                    NavButton { label: "Characters"; pageIndex: 9 }
                    NavButton { label: "Trainer"; pageIndex: 10 }
                    NavButton { label: "Activity"; pageIndex: 11 }
                    NavButton { label: "Modules"; pageIndex: 12 }
                    NavButton { label: "Governance"; pageIndex: 13 }
                    Rectangle { Layout.fillWidth: true; height: 1; color: line; Layout.topMargin: 12 }
                    Text { text: "●  Core services ready"; color: "#83a77b"; font.pixelSize: 11 }
                }
            }
        }
        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0
            Rectangle {
                Layout.fillWidth: true
                height: 68
                color: "#11101a"
                Text { anchors.left: parent.left; anchors.leftMargin: 30; anchors.verticalCenter: parent.verticalCenter; text: pageTitles[page] || "EmberVault"; color: ink; font.bold: true; font.pixelSize: 20 }
                RowLayout {
                    anchors.right: parent.right
                    anchors.rightMargin: 24
                    anchors.verticalCenter: parent.verticalCenter
                    ComboBox { model: controlCenter.profileOptions; currentIndex: controlCenter.selectedProfileIndex; onActivated: controlCenter.selectProfile(currentIndex) }
                    Text { text: "●  " + controlCenter.gameStatus; color: "#9ec18e"; font.pixelSize: 12 }
                }
            }
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: page
                HomePage {}
                PackagesPage {}
                GameSettingsPage {}
                SaveManagerPage {}
                TroubleshooterPage {}
                RiskToolsPage { heading: "Content Creator"; capability: "content-creator"; body: "Content creation remains a guarded developer preview." }
                ResearchPage {}
                KnowledgePage {}
                ProfilesPage {}
                CharacterPage {}
                RiskToolsPage { heading: "Trainer"; capability: "trainer"; body: "Trainer capabilities require a research profile, a verified recovery backup, and a separate-process launch contract." }
                ActivityPage {}
                ModulesPage {}
                GovernancePage {}
            }
        }
    }

    component NavButton: Rectangle {
        id: button
        property string label
        property int pageIndex
        Layout.fillWidth: true
        height: 38
        radius: 6
        color: page === pageIndex ? "#25202d" : "transparent"
        Text { anchors.verticalCenter: parent.verticalCenter; anchors.left: parent.left; anchors.leftMargin: 12; text: button.label; color: page === button.pageIndex ? ink : muted; font.pixelSize: 13 }
        MouseArea { anchors.fill: parent; onClicked: page = button.pageIndex }
    }

    component HomePage: ScrollView {
        ColumnLayout {
            width: parent.width
            anchors.margins: 34
            spacing: 20
            Text { text: "GOOD EVENING, JOEL"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Your worlds, under control."; color: ink; font.pixelSize: 32; font.bold: true }
            Text { text: "Review your active profile, protect your saves, and pick up where you left off."; color: muted; font.pixelSize: 15 }
            RowLayout {
                Layout.fillWidth: true
                StatusCard { title: "GAME STATUS"; value: controlCenter.gameStatus; note: controlCenter.gameBuild; accent: "#83a77b" }
                StatusCard { title: "PROFILE"; value: controlCenter.profileName; note: "Core profile"; accent: ember }
                StatusCard { title: "SAFETY"; value: "Ready"; note: controlCenter.saveSummary; accent: "#d8b46a" }
            }
            Rectangle {
                Layout.fillWidth: true
                radius: 8
                color: panel
                border.color: line
                implicitHeight: actionColumn.implicitHeight + 24
                ColumnLayout {
                    id: actionColumn
                    anchors.fill: parent
                    anchors.margins: 12
                    Text { text: "RECOMMENDED NEXT ACTION"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.1 }
                    Text { text: controlCenter.recommendedNextAction; color: ink; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    Text { text: controlCenter.dashboardHealth; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                }
            }
            Text { text: "System signals"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 4 }
            Repeater { model: controlCenter.dashboardSignals; delegate: Text { text: modelData; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true } }
            Text { text: "Update trust"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 4 }
            Text { text: controlCenter.updateTrustStatus; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: "Pending changes"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 4 }
            Repeater { model: controlCenter.pendingChanges; delegate: Text { text: "· " + modelData; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true } }
            Text { text: "Vault state"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 4 }
            Flow {
                Layout.fillWidth: true
                spacing: 8
                Repeater {
                    model: controlCenter.workspaceSummary
                    delegate: Rectangle {
                        width: stateLabel.implicitWidth + 24
                        height: 32
                        radius: 4
                        color: panel
                        border.color: line
                        Text { id: stateLabel; anchors.centerIn: parent; text: modelData; color: muted; font.pixelSize: 12 }
                    }
                }
            }
            Text { text: "Data migration"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Text { text: controlCenter.migrationReport; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Button { text: "Preview data migration"; onClicked: migrationPreviewDialog.open() }
            Button { text: "Apply migration with backup"; onClicked: controlCenter.applyMigration() }
            Dialog {
                id: migrationPreviewDialog
                title: "Migration preview"
                modal: true
                standardButtons: Dialog.Close
                contentItem: Column {
                    spacing: 6
                    Repeater { model: controlCenter.migrationPreview; delegate: Text { text: modelData; color: ink; wrapMode: Text.WordWrap } }
                }
            }
            Button { text: "Choose game folder"; onClicked: controlCenter.chooseGameFolder() }
            Text { text: "Installation suggestions"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.detectedGameOptions
                delegate: RowLayout {
                    Layout.fillWidth: true
                    Text { text: modelData; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
                    Button { visible: modelData.indexOf("FOUND ·") === 0; text: "Use this"; onClicked: controlCenter.selectDetectedGame(index) }
                }
            }
            Text { text: "First steps"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Text { text: "EmberVault keeps the Control Center in charge. Start with the game folder, make a verified backup, then review module safety before enabling anything experimental."; color: muted; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Repeater { model: controlCenter.onboardingOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 12; Layout.fillWidth: true } }
            Text { text: "Continue"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 10 }
            Button { text: "Open Save Manager"; onClicked: page = 3 }
            Button { text: "Review modules"; onClicked: page = 12 }
            Text { text: "Recent activity"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 10 }
            Repeater {
                model: controlCenter.recentOperations
                delegate: Text { text: modelData; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
        }
    }

    component SaveManagerPage: ScrollView {
        ColumnLayout {
            width: parent.width
            anchors.margins: 34
            spacing: 18
            Text { text: "SAVE SAFETY"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Protect before you experiment."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Inspect, back up, verify, preview, and restore. Save contents are not edited."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap }
            Button { text: "Choose save folder"; onClicked: controlCenter.chooseSaveFolder() }
            RowLayout {
                Layout.fillWidth: true
                StatusCard { title: "BACKUPS"; value: controlCenter.saveSummary; note: "Verified snapshots"; accent: "#d8b46a" }
                StatusCard { title: "WRITE POLICY"; value: "Protected"; note: "No direct editing"; accent: "#83a77b" }
            }
            ComboBox { Layout.fillWidth: true; model: controlCenter.backupOptions; onActivated: controlCenter.selectBackup(currentIndex) }
            Dialog {
                id: restoreDialog
                title: "Restore selected backup?"
                modal: true
                standardButtons: Dialog.Ok | Dialog.Cancel
                contentItem: Text {
                    text: "EmberVault will create the required recovery snapshot and then restore the selected verified backup. The current save folder will be replaced."
                    color: ink
                    wrapMode: Text.WordWrap
                    width: 360
                }
                onAccepted: controlCenter.restoreSelected()
            }
            RowLayout {
                Button { text: "Inspect"; onClicked: controlCenter.inspectSaves() }
                Button { text: "Backup now"; enabled: controlCenter.canBackup; onClicked: controlCenter.createBackup("manual") }
                Button { text: "Verify selected"; enabled: controlCenter.backupOptions.length > 0; onClicked: controlCenter.verifySelected() }
                Button { text: "Preview restore"; enabled: controlCenter.backupOptions.length > 0; onClicked: controlCenter.previewRestore() }
                Button { text: "Restore selected"; enabled: controlCenter.canRestore; onClicked: restoreDialog.open() }
            }
            Text { text: controlCenter.restorePreview; color: muted; wrapMode: Text.WordWrap }
            Text { text: controlCenter.lastSaveMessage; color: ink; wrapMode: Text.WordWrap }
        }
    }

    component GovernancePage: ScrollView {
        clip: true
        ColumnLayout {
            width: parent.width
            spacing: 16
            Text { text: "Capability Governance"; color: ink; font.pixelSize: 25; font.bold: true }
            Text { text: "Promotion readiness across Research-only, Experimental, Verified, and Stable capabilities."; color: muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Rectangle { Layout.fillWidth: true; height: 1; color: line }
            Repeater {
                model: controlCenter.capabilityGovernance
                delegate: Rectangle {
                    Layout.fillWidth: true; height: 58; color: panel; border.color: line; radius: 6
                    Text { anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter; text: modelData; color: ink; font.pixelSize: 13; width: parent.width - 32; elide: Text.ElideRight }
                }
            }
            Text { text: "Promotion history"; color: ember; font.bold: true; font.pixelSize: 16; Layout.topMargin: 12 }
            Button { text: "Review selected capability"; onClicked: controlCenter.reviewCapability("embervault.eml") }
            Repeater {
                model: controlCenter.promotionSummary
                delegate: Text { text: modelData; color: muted; font.pixelSize: 12 }
            }
            Text { text: "Release candidate audit"; color: ember; font.bold: true; font.pixelSize: 16; Layout.topMargin: 12 }
            Repeater { model: controlCenter.releaseAuditOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 12 } }
            Text { text: "Runtime adapter boundary"; color: ember; font.bold: true; font.pixelSize: 16; Layout.topMargin: 12 }
            Repeater { model: controlCenter.adapterGovernance; delegate: Text { text: modelData; color: muted; font.pixelSize: 12 } }
        }
    }

    component ModulesPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "MODULES"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Your tools, clearly separated."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "EmberVault discovers independently packaged modules through their contracts. Experimental modules are labeled before they are enabled."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: controlCenter.moduleOptions.length === 0 ? "No modules discovered yet." : "Discovered modules"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Button { text: "Inspect embedded modules"; onClicked: controlCenter.inspectEmbeddedModules() }
            Button { text: "Install module folder"; onClicked: controlCenter.installModuleFolder() }
            Button { text: "Stage module upgrade for review"; onClicked: controlCenter.stageModuleUpgrade() }
            Text { text: controlCenter.moduleUpgradeReview; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            ComboBox { id: embeddedModulePicker; model: controlCenter.embeddedModuleIds; Layout.fillWidth: true }
            Button { text: "Load selected embedded module"; enabled: embeddedModulePicker.currentText.length > 0; onClicked: controlCenter.loadEmbeddedModule(embeddedModulePicker.currentText) }
            Text { text: "Module safety and capability status"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.moduleHealthOptions
                delegate: Rectangle {
                    Layout.fillWidth: true
                    height: 58
                    radius: 7
                    color: panel
                    border.color: line
                    Text { anchors.fill: parent; anchors.margins: 14; text: modelData; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter }
                }
            }
            Repeater {
                model: controlCenter.embeddedModuleOptions
                delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true }
            }
            Repeater {
                model: controlCenter.moduleOptions
                delegate: Rectangle {
                    Layout.fillWidth: true
                    height: 62
                    radius: 7
                    color: panel
                    border.color: line
                    Text { anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter; text: modelData; color: ink; font.pixelSize: 14 }
                }
            }
        }
    }

    component PackagesPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "MY MODS"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Choose what this profile carries."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Packages are enabled per profile. This first release only manages package state; it does not alter gameplay tuning or edit save contents."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: "Dependency graph"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater { model: controlCenter.dependencyGraph; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
            Text { text: "Profile comparison"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater { model: controlCenter.profileComparison; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
            Text { text: controlCenter.packageOptions.length === 0 ? "No packages discovered yet." : "Available packages"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Text { text: controlCenter.externalPackageOptions.length === 0 ? "No unmanaged external mods detected." : "External mods already in the game folder"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater { model: controlCenter.externalPackageOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
            Text { text: "Update detection"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater { model: controlCenter.packageUpdates; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
            Button { text: "Import package folder or ZIP"; onClicked: controlCenter.importPackage() }
            Button { text: "Inspect deployment plan"; onClicked: controlCenter.inspectDeploymentPlan() }
            Button { text: "Deploy ready packages"; enabled: controlCenter.canDeploy; onClicked: deployDialog.open() }
            Repeater { model: controlCenter.deploymentOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
            Text { text: "Installed destination inspection"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater { model: controlCenter.managedDeploymentOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
            property int undeployIndex: -1
            property int removeIndex: -1
            Dialog {
                id: deployDialog
                title: "Deploy ready packages?"
                modal: true
                standardButtons: Dialog.Ok | Dialog.Cancel
                contentItem: Text {
                    text: "Only conflict-free mod packages will be copied into the configured game mods folder. Existing destinations remain protected."
                    color: ink
                    wrapMode: Text.WordWrap
                    width: 360
                }
                onAccepted: controlCenter.deployReadyPackages()
            }
            Dialog {
                id: undeployDialog
                title: "Undeploy selected package?"
                modal: true
                standardButtons: Dialog.Ok | Dialog.Cancel
                contentItem: Text {
                    text: "Only the EmberVault-owned destination will be removed. Unmarked or foreign directories will be refused."
                    color: ink
                    wrapMode: Text.WordWrap
                    width: 360
                }
                onAccepted: if (undeployIndex >= 0) controlCenter.undeployPackage(undeployIndex)
            }
            Dialog {
                id: removeDialog
                title: "Remove package?"
                modal: true
                standardButtons: Dialog.Ok | Dialog.Cancel
                contentItem: Text {
                    text: "This removes the managed package from EmberVault. It does not edit save data, but the package must be disabled in every profile first."
                    color: ink
                    wrapMode: Text.WordWrap
                    width: 360
                }
                onAccepted: if (removeIndex >= 0) controlCenter.removePackage(removeIndex)
            }
            Repeater {
                model: controlCenter.packageOptions
                delegate: RowLayout {
                    Layout.fillWidth: true
                    Button { text: modelData; Layout.fillWidth: true; onClicked: controlCenter.togglePackage(index) }
                    Button { text: "Undeploy"; onClicked: { undeployIndex = index; undeployDialog.open() } }
                    Button { text: "Remove"; onClicked: { removeIndex = index; removeDialog.open() } }
                }
            }
        }
    }

    component ProfilesPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "PROFILES"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Give every experiment a safe home."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Profiles keep stable play, research, and future package choices separate. The selected profile is passed into tracked operations."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: "Available profiles"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            TextField { id: profileNameField; placeholderText: "New profile name"; Layout.fillWidth: true }
            Button { text: "Create custom profile"; onClicked: controlCenter.createProfile(profileNameField.text) }
            Button { text: "Export active profile"; onClicked: controlCenter.exportActiveProfile() }
            Button { text: "Import profile"; onClicked: controlCenter.importProfile() }
            Button { text: "Delete active custom profile"; onClicked: controlCenter.deleteActiveProfile() }
            Repeater {
                model: controlCenter.profileDetails
                delegate: Rectangle {
                    Layout.fillWidth: true
                    height: 70
                    radius: 7
                    color: panel
                    border.color: line
                    Text { anchors.left: parent.left; anchors.leftMargin: 16; anchors.verticalCenter: parent.verticalCenter; text: modelData; color: ink; font.pixelSize: 14; wrapMode: Text.WordWrap; width: parent.width - 32 }
                }
            }
        }
    }

    component TroubleshooterPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "TROUBLESHOOTER"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Find the loose thread."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Run a read-only health scan across the game connection, profiles, modules, and packages. Nothing is changed by this scan."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Button { text: "Run health scan"; onClicked: controlCenter.runDiagnostics() }
            Text { text: controlCenter.diagnosticOptions.length === 0 ? "No diagnostics available." : "Latest scan"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.diagnosticOptions
                delegate: Text { text: modelData; color: ink; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
        }
    }

    component GameSettingsPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "GAME SETTINGS"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Tune a profile, safely."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Values are staged with the selected profile. Export and audit are read-only. Live tuning is available only through the separately identified, experimental EML adapter, with a Research profile, verified recovery point, closed-game gate, and runtime readback verification."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: "Adapter readiness: " + controlCenter.tuningAdapterStatus; color: ember; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Button { text: "Reset profile settings"; onClicked: controlCenter.resetGameSettings() }
            Button { text: "Export staged tuning manifest"; onClicked: controlCenter.exportGameSettings() }
            Button { text: "Import staged tuning manifest"; onClicked: settingsFileDialog.open() }
            Button { text: "Audit staged settings safely"; onClicked: controlCenter.launchTuningAudit() }
            Button { text: "Prepare EML operation (no write)"; onClicked: controlCenter.prepareTuningOperation() }
            Button { text: "Stage EML adapter payload"; onClicked: controlCenter.stageTuningAdapter() }
            Button { text: "Deploy staged EML adapter"; enabled: controlCenter.canDeployTuningAdapter; onClicked: adapterDeployDialog.open() }
            Button { text: "Verify latest EML readback"; enabled: controlCenter.canVerifyTuningAdapter; onClicked: controlCenter.verifyTuningAdapter() }
            Button { text: "Rollback EmberVault EML adapter"; enabled: controlCenter.canRollbackTuningAdapter; onClicked: adapterRollbackDialog.open() }
            Dialog {
                id: adapterDeployDialog
                title: "Deploy EmberVault EML adapter?"
                standardButtons: Dialog.Ok | Dialog.Cancel
                contentItem: Label { text: "This deploys only the EmberVault-owned experimental adapter package. The game must be closed. It does not alter saves or client settings; the requested runtime value still requires launch and readback verification."; wrapMode: Text.WordWrap; width: 360 }
                onAccepted: controlCenter.deployStagedTuningAdapter()
            }
            Dialog {
                id: adapterRollbackDialog
                title: "Rollback EmberVault EML adapter?"
                standardButtons: Dialog.Ok | Dialog.Cancel
                contentItem: Label { text: "This removes only the EmberVault-owned adapter package. Existing mods and saves are not changed."; wrapMode: Text.WordWrap; width: 360 }
                onAccepted: controlCenter.rollbackTuningAdapter()
            }
            Text { text: controlCenter.lastSaveMessage; color: ink; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            FileDialog {
                id: settingsFileDialog
                title: "Import staged settings manifest"
                nameFilters: ["JSON files (*.json)"]
                onAccepted: controlCenter.importGameSettings(selectedFile.toString().replace("file:///", ""))
            }
            Repeater {
                model: controlCenter.settingOptions
                delegate: Button { text: modelData; Layout.fillWidth: true; onClicked: controlCenter.stageSetting(index) }
            }
        }
    }

    component ResearchPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "RESEARCH LAB"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Test ideas without losing the thread."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Research records stay associated with an isolated profile. Evidence is captured before experimental work is promoted into a normal workflow."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            TextField { id: researchSearch; placeholderText: "Filter research by title, hypothesis, or template"; Layout.fillWidth: true; onTextChanged: controlCenter.searchResearch(text) }
            TextField { id: titleField; placeholderText: "Experiment title"; Layout.fillWidth: true }
            TextField { id: hypothesisField; placeholderText: "Hypothesis"; Layout.fillWidth: true }
            ComboBox { id: researchTemplate; model: controlCenter.researchTemplateOptions; Layout.fillWidth: true }
            Button { text: "Create research record"; onClicked: controlCenter.createResearchRecord(titleField.text, hypothesisField.text, researchTemplate.currentText) }
            TextField { id: evidenceField; placeholderText: "Evidence note for latest record"; Layout.fillWidth: true }
            Button { text: "Add evidence note"; onClicked: controlCenter.addResearchEvidence(evidenceField.text) }
            TextField { id: reproductionField; placeholderText: "Reproduction step for latest record"; Layout.fillWidth: true }
            Button { text: "Add reproduction step"; onClicked: controlCenter.addResearchReproductionStep(reproductionField.text) }
            TextField { id: failureField; placeholderText: "Failure or deviation for latest record"; Layout.fillWidth: true }
            Button { text: "Record failure"; onClicked: controlCenter.addResearchFailure(failureField.text) }
            RowLayout {
                Button { text: "Mark running"; onClicked: controlCenter.setLatestResearchStatus("running") }
                Button { text: "Mark completed"; onClicked: controlCenter.setLatestResearchStatus("completed") }
            }
            Button { text: "Publish latest completed research"; onClicked: controlCenter.publishLatestResearch() }
            TextField { id: promotionField; placeholderText: "Promotion review note"; Layout.fillWidth: true }
            RowLayout {
                Button { text: "Request promotion review"; onClicked: controlCenter.requestLatestResearchPromotion(promotionField.text) }
                Button { text: "Approve promotion"; onClicked: controlCenter.approveLatestResearchPromotion(promotionField.text) }
            }
            Button { text: "Unpublish latest research"; onClicked: controlCenter.unpublishLatestResearch() }
            Button { text: "Export latest research summary"; onClicked: controlCenter.exportLatestResearchSummary() }
            Button { text: "Export reproducibility report"; onClicked: controlCenter.exportLatestResearchReport() }
            Button { text: "Stage latest research submission"; onClicked: controlCenter.stageLatestResearchSubmission() }
            Button { text: "Promote latest research to private knowledge draft"; onClicked: controlCenter.promoteLatestResearchToKnowledge() }
            TextField { id: discussionNoteField; placeholderText: "Discussion note for latest experiment"; Layout.fillWidth: true }
            Button { text: "Add discussion note"; onClicked: controlCenter.addLatestResearchDiscussion(discussionNoteField.text) }
            TextField { id: comparisonLabelField; placeholderText: "Comparison label"; Layout.fillWidth: true }
            TextField { id: comparisonOutcomeField; placeholderText: "Comparison outcome"; Layout.fillWidth: true }
            TextField { id: comparisonBuildField; placeholderText: "Comparison game build"; Layout.fillWidth: true }
            Button { text: "Add comparison run"; onClicked: controlCenter.addLatestResearchComparison(comparisonLabelField.text, comparisonOutcomeField.text, comparisonBuildField.text) }
            Text { text: controlCenter.researchOptions.length === 0 ? "No research records yet." : "Research records"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.researchOptions
                delegate: Text { text: modelData; color: ink; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
            Repeater {
                model: controlCenter.researchCollaborationOptions
                delegate: Text { text: modelData; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
            Repeater {
                model: controlCenter.researchEvidenceOptions
                delegate: Text { text: modelData; color: muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
        }
    }

    component KnowledgePage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "KNOWLEDGE"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Keep the reasoning close."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "A local knowledge catalog explains safety rules, profile isolation, and module boundaries. PUBLIC entries are safe for catalog export; PRIVATE entries remain local."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Button { text: "Export website catalog"; onClicked: controlCenter.exportCatalog() }
            Button { text: "Publish catalog to repository folder"; onClicked: controlCenter.syncCatalogFolder() }
            Button { text: "Stage latest knowledge submission"; onClicked: controlCenter.stageLatestKnowledgeSubmission() }
            Button { text: "Stage conflict-safe website handoff"; onClicked: controlCenter.stageCommunityHandoff() }
            TextField { placeholderText: "Search knowledge"; Layout.fillWidth: true; onTextChanged: controlCenter.searchKnowledge(text) }
            TextField { id: knowledgeTitle; placeholderText: "Knowledge title"; Layout.fillWidth: true }
            TextField { id: knowledgeCategory; placeholderText: "Category"; Layout.fillWidth: true }
            TextField { id: knowledgeSummary; placeholderText: "Short summary"; Layout.fillWidth: true }
            TextField { id: knowledgeContent; placeholderText: "Knowledge content or research note"; Layout.fillWidth: true }
            Button { text: "Save local knowledge entry"; onClicked: controlCenter.createKnowledgeEntry(knowledgeTitle.text, knowledgeCategory.text, knowledgeSummary.text, knowledgeContent.text) }
            TextField { id: knowledgeTags; placeholderText: "Tags (comma separated)"; Layout.fillWidth: true }
            TextField { id: knowledgeRelated; placeholderText: "Related article/research IDs (comma separated)"; Layout.fillWidth: true }
            TextField { id: knowledgeEvidence; placeholderText: "Evidence reference IDs (comma separated)"; Layout.fillWidth: true }
            Button { text: "Update latest article"; onClicked: controlCenter.updateLatestKnowledge(knowledgeTitle.text, knowledgeCategory.text, knowledgeSummary.text, knowledgeContent.text, knowledgeTags.text, knowledgeRelated.text, knowledgeEvidence.text) }
            RowLayout {
                Button { text: "Publish latest knowledge"; onClicked: controlCenter.publishLatestKnowledge() }
                Button { text: "Unpublish latest knowledge"; onClicked: controlCenter.unpublishLatestKnowledge() }
            }
            Text { text: controlCenter.knowledgeHistoryOptions.length === 0 ? "No previous versions for latest article." : "Previous versions"; color: muted; font.pixelSize: 13 }
            Repeater { model: controlCenter.knowledgeHistoryOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 12; Layout.fillWidth: true } }
            Repeater {
                model: controlCenter.knowledgeOptions
                delegate: Rectangle {
                    Layout.fillWidth: true
                    height: 76
                    radius: 7
                    color: panel
                    border.color: line
                    Text { anchors.fill: parent; anchors.margins: 16; text: modelData; color: ink; font.pixelSize: 13; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter }
                }
            }
        }
    }

    component CharacterPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "CHARACTER EDITOR"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Plan a character, protect the original."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Character projects are stored separately from saves. This first slice records plans only; it does not write character changes into game data."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            TextField { id: characterName; placeholderText: "Character name"; Layout.fillWidth: true }
            TextField { id: characterNotes; placeholderText: "Build notes or intended progression"; Layout.fillWidth: true }
            TextField { id: characterGoals; placeholderText: "Build goals (semicolon-separated)"; Layout.fillWidth: true }
            TextField { id: characterProgression; placeholderText: "Progression plan (semicolon-separated)"; Layout.fillWidth: true }
            TextField { id: characterEquipment; placeholderText: "Equipment notes (semicolon-separated)"; Layout.fillWidth: true }
            TextField { id: characterSkills; placeholderText: "Skill notes (semicolon-separated)"; Layout.fillWidth: true }
            TextField { id: characterBackup; placeholderText: "Verified backup ID (optional)"; Layout.fillWidth: true }
            Button { text: "Create character project"; onClicked: controlCenter.createCharacter(characterName.text, characterNotes.text) }
            ComboBox { id: characterTemplate; model: controlCenter.characterTemplateOptions; Layout.fillWidth: true }
            Button { text: "Set latest build template"; onClicked: controlCenter.setLatestCharacterTemplate(characterTemplate.currentText) }
            Button { text: "Update latest plan notes"; onClicked: controlCenter.updateLatestCharacterNotes(characterNotes.text) }
            Button { text: "Update structured character plan"; onClicked: controlCenter.updateLatestCharacterPlan(characterGoals.text, characterProgression.text, characterEquipment.text, characterSkills.text, characterBackup.text) }
            SpinBox { id: characterLevel; from: 1; to: 50; value: 1; Layout.fillWidth: true }
            Button { text: "Stage level for latest project"; onClicked: controlCenter.stageLatestCharacterLevel(characterLevel.value) }
            Button { text: "Simulate progression"; onClicked: controlCenter.simulateLatestCharacterProgression(characterLevel.value) }
            Button { text: "Compare latest equipment plans"; onClicked: controlCenter.compareLatestCharacterEquipment() }
            Button { text: "Export latest character plan"; onClicked: controlCenter.exportLatestCharacterPlan() }
            Text { text: controlCenter.characterOptions.length === 0 ? "No character projects yet." : "Character projects"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.characterOptions
                delegate: Text { text: modelData; color: ink; font.pixelSize: 13; Layout.fillWidth: true }
            }
            Repeater { model: controlCenter.characterPlanningOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 12; Layout.fillWidth: true } }
        }
    }

    component RiskToolsPage: ScrollView {
        property string heading
        property string capability
        property string body
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: capability.toUpperCase(); color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: heading; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: body; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: "Safety gates"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            TextField { id: trainerTarget; visible: capability === "trainer"; placeholderText: "Trainer target or test objective"; Layout.fillWidth: true }
            TextField { id: trainerNotes; visible: capability === "trainer"; placeholderText: "Trainer plan notes"; Layout.fillWidth: true }
            TextField { id: trainerStep; visible: capability === "trainer"; placeholderText: "Trainer test step"; Layout.fillWidth: true }
            RowLayout {
                visible: capability === "trainer"
                Button { text: "Create plan"; onClicked: controlCenter.createTrainerPlan(trainerTarget.text, trainerNotes.text) }
                Button { text: "Add test step"; onClicked: controlCenter.addLatestTrainerTestStep(trainerStep.text) }
                Button { text: "Simulate recovery"; onClicked: controlCenter.simulateLatestTrainerRecovery(true) }
                Button { text: "Export latest plan"; onClicked: controlCenter.exportLatestTrainerPlan() }
            }
            Repeater { visible: capability === "trainer"; model: controlCenter.trainerPlanOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 12; Layout.fillWidth: true } }
            TextField { id: contentName; visible: capability === "content-creator"; placeholderText: "Content project name"; Layout.fillWidth: true }
            TextField { id: contentDescription; visible: capability === "content-creator"; placeholderText: "Development brief or intended outcome"; Layout.fillWidth: true }
            TextField { id: contentDesignNotes; visible: capability === "content-creator"; placeholderText: "Design notes, dimensions, materials, or recipe details"; Layout.fillWidth: true }
            TextField { id: contentAssetRefs; visible: capability === "content-creator"; placeholderText: "Asset references (comma-separated, project-relative)"; Layout.fillWidth: true }
            TextField { id: contentMaterials; visible: capability === "content-creator"; placeholderText: "Materials (comma-separated)"; Layout.fillWidth: true }
            TextField { id: contentDimensions; visible: capability === "content-creator"; placeholderText: "Dimensions (width=2,height=1)"; Layout.fillWidth: true }
            TextField { id: contentRecipe; visible: capability === "content-creator"; placeholderText: "Recipe plan steps (semicolon-separated)"; Layout.fillWidth: true }
            TextField { id: contentRegistration; visible: capability === "content-creator"; placeholderText: "Registration plan"; Layout.fillWidth: true }
            TextField { id: contentCompatibility; visible: capability === "content-creator"; placeholderText: "Compatibility notes"; Layout.fillWidth: true }
            TextField { id: contentDecision; visible: capability === "content-creator"; placeholderText: "Design decision"; Layout.fillWidth: true }
            TextField { id: contentDecisionRationale; visible: capability === "content-creator"; placeholderText: "Decision rationale"; Layout.fillWidth: true }
            TextField { id: contentDecisionResearch; visible: capability === "content-creator"; placeholderText: "Decision research IDs (comma-separated)"; Layout.fillWidth: true }
            TextField { id: contentDecisionKnowledge; visible: capability === "content-creator"; placeholderText: "Decision knowledge IDs (comma-separated)"; Layout.fillWidth: true }
            ComboBox { id: contentDesignType; visible: capability === "content-creator"; model: ["furniture", "building", "recipe", "other"]; Layout.fillWidth: true }
            Button { visible: capability === "content-creator"; text: "Create project"; onClicked: controlCenter.createContentProject(contentName.text, contentDescription.text, contentDesignType.currentText, contentDesignNotes.text, contentAssetRefs.text, contentMaterials.text, contentDimensions.text, contentRecipe.text, contentRegistration.text, contentCompatibility.text) }
            Button { visible: capability === "content-creator"; text: "Update latest design"; onClicked: controlCenter.updateLatestContentDesign(contentDesignType.currentText, contentDesignNotes.text, contentAssetRefs.text, contentMaterials.text, contentDimensions.text, contentRecipe.text, contentRegistration.text, contentCompatibility.text) }
            Button { visible: capability === "content-creator"; text: "Export latest design manifest"; onClicked: controlCenter.exportLatestContentProject() }
            Button { visible: capability === "content-creator"; text: "Stage latest content submission"; onClicked: controlCenter.stageLatestContentSubmission() }
            Button { visible: capability === "content-creator"; text: "Refresh design preview"; onClicked: controlCenter.previewLatestContentProject() }
            Button { visible: capability === "content-creator"; text: "Record design decision"; onClicked: controlCenter.recordLatestContentDecision(contentDecision.text, contentDecisionRationale.text, contentDecisionResearch.text, contentDecisionKnowledge.text) }
            Repeater {
                visible: capability === "content-creator"
                model: controlCenter.contentPreview
                delegate: Text { text: modelData; color: index === 0 ? ember : muted; font.pixelSize: 12; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            }
            RowLayout {
                visible: capability === "content-creator"
                Button { text: "Publish latest"; onClicked: controlCenter.publishLatestContentProject() }
                Button { text: "Unpublish latest"; onClicked: controlCenter.unpublishLatestContentProject() }
            }
            RowLayout {
                visible: capability === "content-creator"
                Button { text: "Mark ready"; onClicked: controlCenter.setLatestContentStatus("ready") }
                Button { text: "Mark blocked"; onClicked: controlCenter.setLatestContentStatus("blocked") }
            }
            Repeater { visible: capability === "content-creator"; model: controlCenter.contentOptions; delegate: Text { text: modelData; color: ink; font.pixelSize: 13; Layout.fillWidth: true } }
            Repeater {
                model: controlCenter.riskOptions
                delegate: Text { text: modelData; color: ink; font.pixelSize: 13; Layout.fillWidth: true }
            }
            RowLayout {
                Button { text: "Run guarded worker"; onClicked: capability === "trainer" ? controlCenter.launchTrainer() : capability === "research" ? controlCenter.launchResearchWorker() : controlCenter.launchContentWorker() }
            }
            Text { text: "Launch is permitted only when this profile and recovery state satisfy the gate. Included workers are non-mutating contract tests."; color: muted; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
    }

    component ActivityPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "ACTIVITY"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "See what EmberVault did."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "Operations are recorded with their status and context so recovery and troubleshooting have an auditable history."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: controlCenter.activitySummary; color: muted; font.pixelSize: 13; Layout.fillWidth: true }
            RowLayout {
                Layout.fillWidth: true
                TextField { placeholderText: "Search activity"; Layout.fillWidth: true; onTextChanged: controlCenter.setActivityQuery(text) }
                ComboBox { model: controlCenter.activityFilters; onCurrentTextChanged: controlCenter.setActivityFilter(currentText) }
                Button { text: "Export"; onClicked: controlCenter.exportActivity() }
            }
            Text { text: "Safety context"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.operationDetails
                delegate: Rectangle {
                    Layout.fillWidth: true
                    height: 106
                    radius: 7
                    color: panel
                    border.color: line
                    Text { anchors.left: parent.left; anchors.right: parent.right; anchors.top: parent.top; anchors.margins: 14; height: 58; text: modelData; color: ink; font.pixelSize: 13; wrapMode: Text.WordWrap }
                    Row {
                        anchors.right: parent.right; anchors.bottom: parent.bottom; anchors.margins: 8; spacing: 8
                        Button { text: "Acknowledge"; onClicked: controlCenter.acknowledgeOperation(modelData) }
                        Button { text: "Review recovery"; visible: modelData.indexOf("RECOVER") >= 0 || modelData.indexOf("FAILED") >= 0; onClicked: controlCenter.reviewOperationRecovery(modelData) }
                    }
                }
            }
        }
    }

    component PlaceholderPage: ScrollView {
        property string heading
        property string body
        ColumnLayout {
            anchors.margins: 34
            Text { text: heading; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: body; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap }
        }
    }

    component StatusCard: Rectangle {
        property string title
        property string value
        property string note
        property color accent
        Layout.fillWidth: true
        height: 108
        radius: 8
        color: panel
        border.color: line
        Column {
            anchors.fill: parent
            anchors.margins: 16
            spacing: 7
            Text { text: title; color: muted; font.pixelSize: 10 }
            Text { text: value; color: accent; font.pixelSize: 21; font.bold: true }
            Text { text: note; color: muted; font.pixelSize: 11 }
        }
    }
}
