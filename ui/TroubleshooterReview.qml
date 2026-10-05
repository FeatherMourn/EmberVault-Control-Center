import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: review
    property string title: "Troubleshooter Review"
    property var findings: []
    property var recovery: null
    property var errors: []
    property bool readOnly: true

    spacing: 10
    Text { text: review.title; color: "#edeaf4"; font.bold: true; font.pixelSize: 22 }
    Text { text: "READ-ONLY DIAGNOSTICS"; color: "#ef8b4d"; font.pixelSize: 11; font.letterSpacing: 1.2 }
    Text { text: "Save Manager remains the owner of save operations."; color: "#918da4"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    Text { visible: review.findings.length === 0; text: "No diagnostic findings available."; color: "#918da4" }
    Repeater {
        model: review.findings
        delegate: Text { text: modelData.title || modelData.id || "Finding"; color: "#edeaf4"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    }
    Text { visible: review.recovery !== null; text: review.recovery === null ? "" : "Recovery reviews: " + review.recovery.review_count + " · Rollback-ready: " + review.recovery.rollback_ready_count; color: "#d8b46a"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
    Text { visible: review.errors.length > 0; text: "Errors: " + review.errors.join("; "); color: "#d97b7b"; wrapMode: Text.WordWrap; Layout.fillWidth: true }
}
