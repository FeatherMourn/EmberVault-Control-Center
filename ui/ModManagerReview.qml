import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: review
    property string title: "Mod Manager Review"
    property string packageId: ""
    property string version: ""
    property string compatibility: "unknown"
    property string integrity: "unknown"
    property string backupReadiness: "unknown"
    property string recoverySummary: ""

    spacing: 8
    Text { text: review.title; color: "#edeaf4"; font.bold: true; font.pixelSize: 22 }
    Text { text: "READ-ONLY PASSPORT REVIEW"; color: "#ef8b4d"; font.pixelSize: 11; font.letterSpacing: 1.2 }
    Text { text: review.packageId + " " + review.version; color: "#edeaf4"; Layout.fillWidth: true }
    Text { text: "Compatibility: " + review.compatibility; color: "#d8b46a"; Layout.fillWidth: true }
    Text { text: "Integrity: " + review.integrity; color: "#d8b46a"; Layout.fillWidth: true }
    Text { text: "Backup readiness: " + review.backupReadiness; color: "#d8b46a"; Layout.fillWidth: true }
    Text { text: review.recoverySummary; color: "#918da4"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    Text { text: "Approval and package actions are disabled."; color: "#918da4"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
}
