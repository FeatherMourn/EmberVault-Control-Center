import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    visible: true
    width: 1080
    height: 720
    minimumWidth: 820
    minimumHeight: 560
    title: "EmberVault Content Creator"
    color: "#0d0c14"
    property color ink: "#edeaf4"
    property color muted: "#918da4"
    property color ember: "#ef8b4d"
    property int step: 0

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 34
        spacing: 18
        Text { text: "CONTENT CREATOR"; color: ember; font.pixelSize: 11; font.letterSpacing: 1.3 }
        Text { text: "Design your next idea."; color: ink; font.pixelSize: 30; font.bold: true }
        Text { text: "Furniture, buildings, recipes, and other design-only projects live here. Nothing writes to the live game installation."; color: muted; font.pixelSize: 15; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Text { text: step < 4 ? "Step " + (step + 1) + " of 4" : "Project ready"; color: ember; font.bold: true }

        ComboBox { id: type; visible: step === 0; model: ["furniture", "building", "recipe", "other"]; Layout.fillWidth: true }
        TextField { id: name; visible: step === 1; placeholderText: "Project name"; Layout.fillWidth: true }
        TextField { id: description; visible: step === 1; placeholderText: "What are you creating?"; Layout.fillWidth: true }
        TextField { id: notes; visible: step === 2; placeholderText: "Design details and notes"; Layout.fillWidth: true }
        TextField { id: materials; visible: step === 2; placeholderText: "Materials, separated by commas (optional)"; Layout.fillWidth: true }
        TextField { id: dimensions; visible: step === 2; placeholderText: "Dimensions, for example width=2,height=1 (optional)"; Layout.fillWidth: true }
        TextField { id: recipe; visible: step === 3; placeholderText: "Recipe or build steps (optional)"; Layout.fillWidth: true }
        TextField { id: assets; visible: step === 3; placeholderText: "Reference assets (optional)"; Layout.fillWidth: true }
        TextField { id: compatibility; visible: step === 3; placeholderText: "Compatibility notes (optional)"; Layout.fillWidth: true }
        Text { visible: step === 4; text: "Your design is saved as a Content Creator project. Review it below before exporting."; color: muted; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Text { visible: step >= 3; text: controlCenter.lastSaveMessage; color: ember; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        Repeater {
            visible: step === 4
            model: controlCenter.contentPreview
            delegate: Text { text: modelData; color: index === 0 ? ember : muted; font.pixelSize: 13; wrapMode: Text.WordWrap; Layout.fillWidth: true }
        }
        RowLayout {
            Layout.fillWidth: true
            Button { visible: step > 0 && step < 4; text: "Back"; onClicked: step -= 1 }
            Button { visible: step < 3; text: "Next"; onClicked: step += 1 }
            Button {
                visible: step === 3
                text: "Create project"
                onClicked: {
                    controlCenter.createContentProject(name.text, description.text, type.currentText, notes.text, assets.text, materials.text, dimensions.text, recipe.text, "", compatibility.text)
                    if (controlCenter.contentOptions.length > 0) {
                        step = 4
                        controlCenter.previewLatestContentProject()
                    }
                }
            }
            Button { visible: step === 4; text: "Refresh preview"; onClicked: controlCenter.previewLatestContentProject() }
            Button { visible: step === 4; text: "Export manifest"; onClicked: controlCenter.exportLatestContentProject() }
            Button { visible: step === 4; text: "New project"; onClicked: step = 0 }
        }
    }
}
