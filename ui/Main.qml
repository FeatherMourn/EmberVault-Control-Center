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

    RowLayout {
        anchors.fill: parent
        spacing: 0
        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 230
            color: "#100f18"
            ColumnLayout {
                anchors.fill: parent
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
                Item { Layout.fillHeight: true }
                Rectangle { Layout.fillWidth: true; height: 1; color: line }
                Text { text: "●  Core services ready"; color: "#83a77b"; font.pixelSize: 11 }
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
                Text { anchors.left: parent.left; anchors.leftMargin: 30; anchors.verticalCenter: parent.verticalCenter; text: page === 3 ? "Save Manager" : page === 0 ? "Home" : "Embervault"; color: ink; font.bold: true; font.pixelSize: 20 }
                RowLayout {
                    anchors.right: parent.right
                    anchors.rightMargin: 24
                    anchors.verticalCenter: parent.verticalCenter
                    ComboBox { model: controlCenter.profileOptions; onActivated: controlCenter.selectProfile(currentIndex) }
                    Text { text: "●  " + controlCenter.gameStatus; color: "#9ec18e"; font.pixelSize: 12 }
                }
            }
            StackLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                currentIndex: page
                HomePage {}
                PackagesPage {}
                PlaceholderPage { heading: "Game Settings"; body: "Gameplay tuning will be added as an independently packaged module." }
                SaveManagerPage {}
                PlaceholderPage { heading: "Troubleshooter"; body: "Health scans will use Core logs, operations, compatibility, and module state." }
                PlaceholderPage { heading: "Content Studio"; body: "Content creation remains a guarded developer preview." }
                PlaceholderPage { heading: "Research Lab"; body: "Research runs in isolated profiles and records evidence before promotion." }
                PlaceholderPage { heading: "Knowledge"; body: "Offline documentation will be linked from every module." }
                ProfilesPage {}
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
            RowLayout {
                Button { text: "Inspect"; onClicked: controlCenter.inspectSaves() }
                Button { text: "Backup now"; enabled: controlCenter.canBackup; onClicked: controlCenter.createBackup("manual") }
                Button { text: "Preview restore"; enabled: controlCenter.backupOptions.length > 0; onClicked: controlCenter.previewRestore() }
                Button { text: "Restore selected"; enabled: controlCenter.backupOptions.length > 0; onClicked: controlCenter.restoreSelected() }
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
            Repeater {
                model: controlCenter.packageOptions
                delegate: Button { text: modelData; Layout.fillWidth: true; onClicked: controlCenter.togglePackage(index) }
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
