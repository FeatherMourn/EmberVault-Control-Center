"""Display-only adapter for the Troubleshooter review view model."""


def prepare_troubleshooter_display(view: dict) -> dict:
    if not isinstance(view, dict) or view.get("view_version") != 1:
        raise ValueError("Troubleshooter view version is unsupported.")
    if view.get("read_only") is not True or view.get("mutates_workspace") is not False:
        raise ValueError("Troubleshooter display requires a read-only view.")
    if view.get("controls") != []:
        raise ValueError("Troubleshooter display cannot expose operational controls.")
    return {
        "title": str(view.get("title", "Troubleshooter Review")),
        "read_only_label": "Read-only diagnostics",
        "finding_count": int(view.get("finding_count", 0)),
        "findings": list(view.get("findings", [])),
        "recovery": view.get("recovery"),
        "errors": list(view.get("errors", [])),
        "actions": [],
    }
