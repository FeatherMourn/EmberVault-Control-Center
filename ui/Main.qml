import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 1280
    height: 800
    minimumWidth: 980
    minimumHeight: 640
    title: "Embervault Control Center"
    color: "#0d0c14"

    property color ink: "#edeaf4"
    property color muted: "#918da4"
    property color panel: "#15141e"
    property color line: "#2b2739"
    property color ember: "#ef8b4d"

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Rectangle {
            Layout.fillHeight: true
            Layout.preferredWidth: 248
            color: "#100f18"
            border.color: line
            border.width: 1

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 22
                spacing: 12

                RowLayout {
                    Layout.fillWidth: true
                    Text { text: "✦"; color: ember; font.pixelSize: 23 }
                    Column {
                        Text { text: "EMBERVAULT"; color: ink; font.bold: true; font.pixelSize: 13; font.letterSpacing: 1.5 }
                        Text { text: "CONTROL CENTER"; color: muted; font.pixelSize: 10; font.letterSpacing: 1.1 }
                    }
                }

                Rectangle { Layout.fillWidth: true; height: 1; color: line; Layout.topMargin: 18; Layout.bottomMargin: 10 }

                Text { text: "WORKSPACE"; color: muted; font.pixelSize: 10; font.letterSpacing: 1.4; Layout.bottomMargin: 4 }
                NavButton { label: "Home"; icon: "⌂"; selected: true }
                NavButton { label: "My Mods"; icon: "◈" }
                NavButton { label: "Game Settings"; icon: "◌" }
                NavButton { label: "Save Manager"; icon: "▣" }
                NavButton { label: "Troubleshooter"; icon: "⌁" }

                Text { text: "TOOLS"; color: muted; font.pixelSize: 10; font.letterSpacing: 1.4; Layout.topMargin: 22; Layout.bottomMargin: 4 }
                NavButton { label: "Content Studio"; icon: "◇" }
                NavButton { label: "Research Lab"; icon: "⌬"; badge: "Experimental" }
                NavButton { label: "Knowledge"; icon: "?" }

                Item { Layout.fillHeight: true }
                Rectangle { Layout.fillWidth: true; height: 1; color: line }
                NavButton { label: "Settings"; icon: "⚙" }
                RowLayout { Text { text: "●"; color: "#83a77b"; font.pixelSize: 9 }; Text { text: "Core services ready"; color: muted; font.pixelSize: 11 } }
            }
        }

        ColumnLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            spacing: 0

            Rectangle {
                Layout.fillWidth: true
                Layout.preferredHeight: 72
                color: "#11101a"
                border.color: line
                Text { anchors.left: parent.left; anchors.leftMargin: 34; anchors.verticalCenter: parent.verticalCenter; text: "Home"; color: ink; font.pixelSize: 20; font.bold: true }
                RowLayout { anchors.right: parent.right; anchors.rightMargin: 34; anchors.verticalCenter: parent.verticalCenter; spacing: 18; Text { text: "Default profile"; color: muted; font.pixelSize: 12 }; Rectangle { width: 1; height: 22; color: line }; Text { text: "●  Enshrouded detected"; color: "#9ec18e"; font.pixelSize: 12 } }
            }

            ScrollView {
                Layout.fillWidth: true
                Layout.fillHeight: true
                clip: true
                ColumnLayout {
                    width: parent.width
                    spacing: 26
                    anchors.margins: 38

                    ColumnLayout { Layout.fillWidth: true; spacing: 8; Text { text: "Good evening, Joel"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.4 }; Text { text: "Your worlds, under control."; color: ink; font.pixelSize: 34; font.bold: true }; Text { text: "Review your active profile, protect your saves, and pick up where you left off."; color: muted; font.pixelSize: 15 } }

                    RowLayout { Layout.fillWidth: true; spacing: 14; StatusCard { title: "GAME STATUS"; value: controlCenter.gameStatus; note: controlCenter.gameBuild; accent: "#83a77b" }; StatusCard { title: "ACTIVE PROFILE"; value: controlCenter.profileName; note: "Core profile"; accent: ember }; StatusCard { title: "SAFETY"; value: "Ready"; note: controlCenter.safetySummary + " · " + controlCenter.saveSummary; accent: "#d8b46a" } }

                    RowLayout { Layout.fillWidth: true; spacing: 16; ColumnLayout { Layout.fillWidth: true; spacing: 10; Text { text: "Continue"; color: ink; font.pixelSize: 17; font.bold: true }; ActionCard { title: "Open Save Manager"; description: "Inspect your saves or create a verified backup before testing."; action: "Open" }; ActionCard { title: "Review modules"; description: "See what is installed, compatible, or waiting for review."; action: "View modules" } }; ColumnLayout { Layout.preferredWidth: 290; spacing: 10; Text { text: "Recent activity"; color: ink; font.pixelSize: 17; font.bold: true }; ActivityCard { title: "Core initialized"; note: "Just now" }; ActivityCard { title: "Default profile created"; note: "Just now" }; ActivityCard { title: "No actions recorded"; note: "Ready" } } }
                }
            }
        }
    }

    component NavButton: Rectangle {
        id: nav
        property string label
        property string icon
        property string badge: ""
        property bool selected: false
        Layout.fillWidth: true
        height: 40
        radius: 7
        color: selected ? "#25202d" : "transparent"
        border.color: selected ? "#4c3940" : "transparent"
        RowLayout { anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 10; Text { text: nav.icon; color: selected ? ember : muted; font.pixelSize: 16; Layout.preferredWidth: 23 }; Text { text: nav.label; color: selected ? ink : "#aaa5b7"; font.pixelSize: 13 }; Item { Layout.fillWidth: true }; Text { text: nav.badge; color: muted; font.pixelSize: 9 } }
    }

    component StatusCard: Rectangle {
        property string title; property string value; property string note; property color accent
        Layout.fillWidth: true; height: 116; radius: 9; color: panel; border.color: line
        Column { anchors.fill: parent; anchors.margins: 18; spacing: 7; Text { text: title; color: muted; font.pixelSize: 10; font.letterSpacing: 1.1 }; Text { text: value; color: accent; font.pixelSize: 23; font.bold: true }; Text { text: note; color: muted; font.pixelSize: 11 } }
    }

    component ActionCard: Rectangle {
        property string title; property string description; property string action
        Layout.fillWidth: true; height: 86; radius: 9; color: panel; border.color: line
        RowLayout { anchors.fill: parent; anchors.margins: 17; Text { text: "✦"; color: ember; font.pixelSize: 21; Layout.preferredWidth: 32 }; ColumnLayout { Layout.fillWidth: true; Text { text: title; color: ink; font.pixelSize: 14; font.bold: true }; Text { text: description; color: muted; font.pixelSize: 11; wrapMode: Text.WordWrap; Layout.fillWidth: true } }; Button { text: action; flat: true; contentItem: Text { text: action; color: ember; font.pixelSize: 12 } } }
    }

    component ActivityCard: Rectangle {
        property string title; property string note
        Layout.fillWidth: true; height: 58; radius: 8; color: panel; border.color: line
        Column { anchors.left: parent.left; anchors.leftMargin: 14; anchors.verticalCenter: parent.verticalCenter; spacing: 4; Text { text: title; color: ink; font.pixelSize: 12 }; Text { text: note; color: muted; font.pixelSize: 10 } }
    }
}
