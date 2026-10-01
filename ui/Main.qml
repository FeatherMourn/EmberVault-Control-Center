import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 1200
    height: 760
    minimumWidth: 900
    minimumHeight: 600
    title: "Embervault Control Center"
    color: "#0d0c14"
    property color ink: "#edeaf4"
    property color muted: "#918da4"
    property color panel: "#15141e"
    property color line: "#2b2739"
    property color ember: "#ef8b4d"
    property int page: 0
    property var pageTitles: ["Home", "My Mods", "Game Settings", "Save Manager", "Troubleshooter", "Content Studio", "Research Lab", "Knowledge", "Profiles", "Characters", "Trainer", "Activity", "Modules"]

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
                    NavButton { label: "Content Studio"; pageIndex: 5 }
                    NavButton { label: "Research Lab"; pageIndex: 6 }
                    NavButton { label: "Knowledge"; pageIndex: 7 }
                    NavButton { label: "Profiles"; pageIndex: 8 }
                    NavButton { label: "Characters"; pageIndex: 9 }
                    NavButton { label: "Trainer"; pageIndex: 10 }
                    NavButton { label: "Activity"; pageIndex: 11 }
                    NavButton { label: "Modules"; pageIndex: 12 }
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
                Text { anchors.left: parent.left; anchors.leftMargin: 30; anchors.verticalCenter: parent.verticalCenter; text: pageTitles[page] || "Embervault"; color: ink; font.bold: true; font.pixelSize: 20 }
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
                RiskToolsPage { heading: "Content Studio"; capability: "content-creator"; body: "Content creation remains a guarded developer preview." }
                ResearchPage {}
                KnowledgePage {}
                ProfilesPage {}
                CharacterPage {}
                RiskToolsPage { heading: "Trainer"; capability: "trainer"; body: "Trainer capabilities require a research profile, a verified recovery backup, and a separate-process launch contract." }
                ActivityPage {}
                ModulesPage {}
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
            Button { text: "Choose game folder"; onClicked: controlCenter.chooseGameFolder() }
            Text { text: "Continue"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 10 }
            Button { text: "Open Save Manager"; onClicked: page = 3 }
            Button { text: "Review modules"; onClicked: page = 1 }
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

    component ModulesPage: ScrollView {
        ColumnLayout {
            anchors.margins: 34
            spacing: 18
            Text { text: "MODULES"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
            Text { text: "Your tools, clearly separated."; color: ink; font.pixelSize: 30; font.bold: true }
            Text { text: "EmberVault discovers independently packaged modules through their contracts. Experimental modules are labeled before they are enabled."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Text { text: controlCenter.moduleOptions.length === 0 ? "No modules discovered yet." : "Discovered modules"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Button { text: "Inspect embedded modules"; onClicked: controlCenter.inspectEmbeddedModules() }
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
            Text { text: controlCenter.packageOptions.length === 0 ? "No packages discovered yet." : "Available packages"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Text { text: controlCenter.externalPackageOptions.length === 0 ? "No unmanaged external mods detected." : "External mods already in the game folder"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater { model: controlCenter.externalPackageOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
            Button { text: "Import package folder or ZIP"; onClicked: controlCenter.importPackage() }
            Button { text: "Inspect deployment plan"; onClicked: controlCenter.inspectDeploymentPlan() }
            Button { text: "Deploy ready packages"; onClicked: deployDialog.open() }
            Repeater { model: controlCenter.deploymentOptions; delegate: Text { text: modelData; color: muted; font.pixelSize: 13; Layout.fillWidth: true } }
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
            Text { text: "Values are stored with the selected profile. You can export them and run a read-only audit; this page does not edit save data or inject changes into the game."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
            Button { text: "Reset profile settings"; onClicked: controlCenter.resetGameSettings() }
            Button { text: "Export staged tuning manifest"; onClicked: controlCenter.exportGameSettings() }
            Button { text: "Audit staged settings safely"; onClicked: controlCenter.launchTuningAudit() }
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
            TextField { id: titleField; placeholderText: "Experiment title"; Layout.fillWidth: true }
            TextField { id: hypothesisField; placeholderText: "Hypothesis"; Layout.fillWidth: true }
            Button { text: "Create research record"; onClicked: controlCenter.createResearchRecord(titleField.text, hypothesisField.text) }
            TextField { id: evidenceField; placeholderText: "Evidence note for latest record"; Layout.fillWidth: true }
            Button { text: "Add evidence note"; onClicked: controlCenter.addResearchEvidence(evidenceField.text) }
            RowLayout {
                Button { text: "Mark running"; onClicked: controlCenter.setLatestResearchStatus("running") }
                Button { text: "Mark completed"; onClicked: controlCenter.setLatestResearchStatus("completed") }
            }
            Button { text: "Publish latest completed research"; onClicked: controlCenter.publishLatestResearch() }
            Button { text: "Unpublish latest research"; onClicked: controlCenter.unpublishLatestResearch() }
            Button { text: "Export latest research summary"; onClicked: controlCenter.exportLatestResearchSummary() }
            Text { text: controlCenter.researchOptions.length === 0 ? "No research records yet." : "Research records"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.researchOptions
                delegate: Text { text: modelData; color: ink; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
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
            TextField { placeholderText: "Search knowledge"; Layout.fillWidth: true; onTextChanged: controlCenter.searchKnowledge(text) }
            TextField { id: knowledgeTitle; placeholderText: "Knowledge title"; Layout.fillWidth: true }
            TextField { id: knowledgeCategory; placeholderText: "Category"; Layout.fillWidth: true }
            TextField { id: knowledgeSummary; placeholderText: "Short summary"; Layout.fillWidth: true }
            TextField { id: knowledgeContent; placeholderText: "Knowledge content or research note"; Layout.fillWidth: true }
            Button { text: "Save local knowledge entry"; onClicked: controlCenter.createKnowledgeEntry(knowledgeTitle.text, knowledgeCategory.text, knowledgeSummary.text, knowledgeContent.text) }
            RowLayout {
                Button { text: "Publish latest knowledge"; onClicked: controlCenter.publishLatestKnowledge() }
                Button { text: "Unpublish latest knowledge"; onClicked: controlCenter.unpublishLatestKnowledge() }
            }
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
            Button { text: "Create character project"; onClicked: controlCenter.createCharacter(characterName.text, characterNotes.text) }
            Button { text: "Update latest plan notes"; onClicked: controlCenter.updateLatestCharacterNotes(characterNotes.text) }
            SpinBox { id: characterLevel; from: 1; to: 50; value: 1; Layout.fillWidth: true }
            Button { text: "Stage level for latest project"; onClicked: controlCenter.stageLatestCharacterLevel(characterLevel.value) }
            Button { text: "Export latest character plan"; onClicked: controlCenter.exportLatestCharacterPlan() }
            Text { text: controlCenter.characterOptions.length === 0 ? "No character projects yet." : "Character projects"; color: ink; font.bold: true; font.pixelSize: 17; Layout.topMargin: 8 }
            Repeater {
                model: controlCenter.characterOptions
                delegate: Text { text: modelData; color: ink; font.pixelSize: 13; Layout.fillWidth: true }
            }
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
            RowLayout {
                visible: capability === "trainer"
                Button { text: "Create plan"; onClicked: controlCenter.createTrainerPlan(trainerTarget.text, trainerNotes.text) }
                Button { text: "Export latest plan"; onClicked: controlCenter.exportLatestTrainerPlan() }
            }
            TextField { id: contentName; visible: capability === "content-creator"; placeholderText: "Content project name"; Layout.fillWidth: true }
            TextField { id: contentDescription; visible: capability === "content-creator"; placeholderText: "Development brief or intended outcome"; Layout.fillWidth: true }
            TextField { id: contentDesignNotes; visible: capability === "content-creator"; placeholderText: "Design notes, dimensions, materials, or recipe details"; Layout.fillWidth: true }
            TextField { id: contentAssetRefs; visible: capability === "content-creator"; placeholderText: "Asset references (comma-separated, project-relative)"; Layout.fillWidth: true }
            ComboBox { id: contentDesignType; visible: capability === "content-creator"; model: ["furniture", "building", "recipe", "other"]; Layout.fillWidth: true }
            Button { visible: capability === "content-creator"; text: "Create project"; onClicked: controlCenter.createContentProject(contentName.text, contentDescription.text, contentDesignType.currentText, contentDesignNotes.text, contentAssetRefs.text) }
            Button { visible: capability === "content-creator"; text: "Update latest design"; onClicked: controlCenter.updateLatestContentDesign(contentDesignType.currentText, contentDesignNotes.text, contentAssetRefs.text) }
            Button { visible: capability === "content-creator"; text: "Export latest design manifest"; onClicked: controlCenter.exportLatestContentProject() }
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
            Repeater {
                model: controlCenter.recentOperations
                delegate: Rectangle {
                    Layout.fillWidth: true
                    height: 60
                    radius: 7
                    color: panel
                    border.color: line
                    Text { anchors.fill: parent; anchors.margins: 14; text: modelData; color: ink; font.pixelSize: 13; wrapMode: Text.WordWrap; verticalAlignment: Text.AlignVCenter }
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
