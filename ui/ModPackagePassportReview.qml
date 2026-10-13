import QtQuick 2.15
import QtQuick.Controls 2.15

Column {
    objectName: "modPackagePassportReview"
    spacing: 6
    property string title: "MOD PACKAGE PASSPORT"
    property string statusText: "READ-ONLY REVIEW"
    property string packageText: "No Passport loaded"
    property string issuesText: ""
    Label { text: title }
    Label { text: statusText }
    Label { text: packageText; wrapMode: Text.WordWrap }
    Label { text: issuesText; wrapMode: Text.WordWrap }
}
