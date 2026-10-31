#!/usr/bin/env python3
"""Create the Jump to the Cloud (JTTC) Jira project and its own workflow/schemes.

Modes:
  validate  Check the workflow payload against Jira. Creates nothing.
  apply     Create statuses, workflow, workflow scheme, issue type scheme,
            the project, and attach the schemes. Skips what already exists.

Env: JIRA_API_TOKEN (required), JIRA_EMAIL, JIRA_SITE (defaults below).
Only creates new resources; never edits or deletes existing ones.
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

SITE = os.environ.get("JIRA_SITE", "https://jumptothecloud.atlassian.net")
EMAIL = os.environ.get("JIRA_EMAIL", "antonio.marquez@jumptothecloud.tech")
TOKEN = os.environ["JIRA_API_TOKEN"]

PROJECT_KEY = "JTTC"
PROJECT_NAME = "Jump to the Cloud"
WORKFLOW = "JTTC Workflow"
WORKFLOW_SCHEME = "JTTC Unified Workflow Scheme"
ISSUE_TYPE_SCHEME = "JTTC Unified Issue Type Scheme"
SCRUM_TEMPLATE = "com.pyxis.greenhopper.jira:gh-scrum-template"

# Existing site statuses reused as-is (id), so history/reporting stay consistent.
EXISTING = {"Backlog": "10023", "In refinement": "10015", "In Progress": "3", "Done": "10011"}
EXISTING_CATEGORY = {"Backlog": "TODO", "In refinement": "IN_PROGRESS", "In Progress": "IN_PROGRESS", "Done": "DONE"}
# New statuses: name -> status category.
NEW = {
    "Refined": "TODO",
    "Ready": "TODO",
    "In Review": "IN_PROGRESS",
}
ORDER = ["Backlog", "In refinement", "Refined", "Ready", "In Progress", "In Review", "Done"]

# Existing issue type ids (site-wide). Epic, Story, Task, Bug, plus the five typed sub-tasks
# that the iteration-plan skill creates: Analysis (spike), Automation, Architecture Design,
# Development, Documentation. The generic Sub-task (10008) is deliberately excluded so every
# sub-task is classified.
ISSUE_TYPES = ["10000", "10009", "10007", "10010", "10026", "10027", "10012", "10013", "10014"]
DEFAULT_ISSUE_TYPE = "10009"
REMOVED_ISSUE_TYPES = ["10008"]

SCREEN = "JTTC Default Screen"
SCREEN_SCHEME = "JTTC Screen Scheme"
ISSUE_TYPE_SCREEN_SCHEME = "JTTC Unified Issue Type Screen Scheme"
FIELD_CONFIG = "JTTC Field Configuration"
FIELD_CONFIG_SCHEME = "JTTC Field Configuration Scheme"
# One screen for create/edit/view on every issue type (Flagged = blocked marker, Parent = Epic/Story link).
SCREEN_FIELDS = [
    "summary", "issuetype", "parent", "components", "description", "labels", "priority",
    "assignee", "reporter", "customfield_10041",  # Story Points
    "customfield_10020",  # Sprint
    "customfield_10021",  # Flagged
    "customfield_10231",  # Mode (AFK / HITL), set by iteration-plan
    "customfield_10100",  # Size, set by refine-story
    "customfield_10098",  # Business Value, set by refine-story
    "customfield_10131",  # Risk, set by refine-story
    "fixVersions", "versions", "issuelinks", "attachment",
]

_AUTH = "Basic " + base64.b64encode(f"{EMAIL}:{TOKEN}".encode()).decode()


def api(method, path, body=None, ok=(200, 201, 204)):
    req = urllib.request.Request(
        SITE + "/rest/api/3" + path,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": _AUTH, "Accept": "application/json", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()
        sys.exit(f"HTTP {e.code} on {method} {path}\n{detail}")


def workflow_payload():
    ref = {n: str(uuid.uuid4()) for n in [*NEW, *EXISTING]}
    statuses = [{"name": n, "statusCategory": c, "statusReference": ref[n]} for n, c in NEW.items()]
    # Existing statuses are declared with their id so Jira reuses them instead of creating copies.
    statuses += [
        {"id": i, "name": n, "statusCategory": EXISTING_CATEGORY[n], "statusReference": ref[n]}
        for n, i in EXISTING.items()
    ]
    wf_statuses = [
        {"statusReference": ref[n], "layout": {"x": 120.0 + i * 190.0, "y": 80.0}, "properties": {}}
        for i, n in enumerate(ORDER)
    ]
    # One INITIAL transition into Backlog, and one GLOBAL transition per status:
    # any status can move to any other (allows shortcuts like Backlog -> Ready).
    transitions = [
        {"id": "1", "name": "Create", "type": "INITIAL", "toStatusReference": ref["Backlog"], "links": []}
    ]
    for i, n in enumerate(ORDER):
        transitions.append(
            {"id": str(11 + i), "name": n, "type": "GLOBAL", "toStatusReference": ref[n], "links": []}
        )
    return {
        "scope": {"type": "GLOBAL"},
        "statuses": statuses,
        "workflows": [
            {
                "name": WORKFLOW,
                "description": "Backlog > In Refinement > Refined > Ready > In Progress > In Review > Done. Free transitions.",
                "statuses": wf_statuses,
                "transitions": transitions,
            }
        ],
    }


def workflow_exists():
    found = api("GET", f"/workflows/search?queryString={urllib.parse.quote(WORKFLOW)}&maxResults=50")
    return any(w["name"] == WORKFLOW for w in found.get("values", []))


def validate():
    if workflow_exists():
        # The payload would only clash with itself (same status and workflow names).
        print(f"workflow '{WORKFLOW}' already exists: nothing to validate, the project is built.")
        return True
    res = api("POST", "/workflows/create/validation",
              {"payload": workflow_payload(), "validationOptions": {"levels": ["WARNING", "ERROR"]}})
    errors = res.get("errors", [])
    print(json.dumps(res, indent=2))
    print("\nVALID" if not errors else f"\n{len(errors)} validation error(s)")
    return not errors


def find(path, key, name, field="name"):
    start = 0
    while True:
        res = api("GET", f"{path}{'&' if '?' in path else '?'}startAt={start}&maxResults=50")
        for v in res.get("values", []):
            if v[field] == name:
                return v
        if res.get("isLast", True):
            return None
        start += 50


def apply():
    wf = api("GET", f"/workflows/search?queryString={urllib.parse.quote(WORKFLOW)}&maxResults=50")
    if any(w["name"] == WORKFLOW for w in wf.get("values", [])):
        print(f"workflow '{WORKFLOW}' exists, skipping")
    else:
        if not validate():
            sys.exit("Fix validation errors first.")
        api("POST", "/workflows/create", workflow_payload())
        print(f"created workflow '{WORKFLOW}'")

    ws = find("/workflowscheme", "values", WORKFLOW_SCHEME)
    if not ws:
        ws = api("POST", "/workflowscheme", {"name": WORKFLOW_SCHEME, "defaultWorkflow": WORKFLOW})
        print(f"created workflow scheme {ws['id']}")
    its = find("/issuetypescheme", "values", ISSUE_TYPE_SCHEME)
    if not its:
        its = api("POST", "/issuetypescheme",
                  {"name": ISSUE_TYPE_SCHEME, "issueTypeIds": ISSUE_TYPES, "defaultIssueTypeId": DEFAULT_ISSUE_TYPE})
        its = {"id": its["issueTypeSchemeId"]}
        print(f"created issue type scheme {its['id']}")
    # Keep an existing scheme in sync: add missing types, drop the excluded ones.
    have = {m["issueTypeId"] for m in api("GET", f"/issuetypescheme/mapping?issueTypeSchemeId={its['id']}")["values"]}
    missing = [t for t in ISSUE_TYPES if t not in have]
    if missing:
        api("PUT", f"/issuetypescheme/{its['id']}/issuetype", {"issueTypeIds": missing})
        print(f"added issue types {missing}")
    for t in REMOVED_ISSUE_TYPES:
        if t in have:
            api("DELETE", f"/issuetypescheme/{its['id']}/issuetype/{t}")
            print(f"removed issue type {t}")

    me = api("GET", "/myself")
    try:
        proj = api("GET", f"/project/{PROJECT_KEY}")
        print(f"project {PROJECT_KEY} exists, skipping creation")
    except SystemExit:
        proj = api("POST", "/project", {
            "key": PROJECT_KEY, "name": PROJECT_NAME, "projectTypeKey": "software",
            "projectTemplateKey": SCRUM_TEMPLATE, "leadAccountId": me["accountId"], "assigneeType": "UNASSIGNED",
        })
        print(f"created project {PROJECT_KEY} (id {proj['id']})")

    api("PUT", "/workflowscheme/project", {"projectId": proj["id"], "workflowSchemeId": str(ws["id"])})
    api("PUT", "/issuetypescheme/project", {"projectId": proj["id"], "issueTypeSchemeId": str(its["id"])})
    print("attached workflow scheme and issue type scheme")

    # --- screens -> screen scheme -> issue type screen scheme
    screen = find(f"/screens?queryString={urllib.parse.quote(SCREEN)}", "values", SCREEN)
    if not screen:
        screen = api("POST", "/screens", {"name": SCREEN, "description": "JTTC create/edit/view screen"})
        tabs = api("GET", f"/screens/{screen['id']}/tabs")
        tab_id = tabs[0]["id"] if tabs else api("POST", f"/screens/{screen['id']}/tabs", {"name": "Fields"})["id"]
        for fid in SCREEN_FIELDS:
            api("POST", f"/screens/{screen['id']}/tabs/{tab_id}/fields", {"fieldId": fid})
        print(f"created screen {screen['id']} with {len(SCREEN_FIELDS)} fields")
    else:
        # Keep an existing screen in sync: add fields that are missing.
        tab_id = api("GET", f"/screens/{screen['id']}/tabs")[0]["id"]
        on_tab = {f["id"] for f in api("GET", f"/screens/{screen['id']}/tabs/{tab_id}/fields")}
        for fid in SCREEN_FIELDS:
            if fid not in on_tab:
                api("POST", f"/screens/{screen['id']}/tabs/{tab_id}/fields", {"fieldId": fid})
                print(f"added field {fid} to screen {screen['id']}")
    ss = find(f"/screenscheme?queryString={urllib.parse.quote(SCREEN_SCHEME)}", "values", SCREEN_SCHEME)
    if not ss:
        ss = api("POST", "/screenscheme", {
            "name": SCREEN_SCHEME,
            "screens": {k: screen["id"] for k in ("default", "create", "edit", "view")},
        })
        print(f"created screen scheme {ss['id']}")
    itss = find(f"/issuetypescreenscheme?queryString={urllib.parse.quote(ISSUE_TYPE_SCREEN_SCHEME)}", "values",
                ISSUE_TYPE_SCREEN_SCHEME)
    if not itss:
        r = api("POST", "/issuetypescreenscheme", {
            "name": ISSUE_TYPE_SCREEN_SCHEME,
            "issueTypeMappings": [{"issueTypeId": "default", "screenSchemeId": str(ss["id"])}],
        })
        itss = {"id": r["id"]}
        print(f"created issue type screen scheme {itss['id']}")
    api("PUT", "/issuetypescreenscheme/project",
        {"projectId": proj["id"], "issueTypeScreenSchemeId": str(itss["id"])})

    # --- field configuration (own copy so required/hidden tweaks never touch other projects)
    fc = find("/fieldconfiguration", "values", FIELD_CONFIG)
    if not fc:
        try:
            fc = api("POST", "/fieldconfiguration", {"name": FIELD_CONFIG, "description": "JTTC field configuration"})
            print(f"created field configuration {fc['id']}")
        except SystemExit:
            # This Jira refuses to create or list field configurations via REST, so they are
            # managed in the UI (Settings > Work items > Field configurations). JTTC has its own
            # copy there with Components required. Never mark a field required on the Default
            # Field Configuration: every other project shares it. Verify the real effect with
            # GET /issue/createmeta/JTTC/issuetypes/<id> and look for required fields.
            print(f"NOTE field configuration '{FIELD_CONFIG}' is managed in the Jira UI, not by this script")
            return
    fcs = find("/fieldconfigurationscheme", "values", FIELD_CONFIG_SCHEME)
    if not fcs:
        fcs = api("POST", "/fieldconfigurationscheme", {"name": FIELD_CONFIG_SCHEME})
        api("PUT", f"/fieldconfigurationscheme/{fcs['id']}/mapping",
            {"mappings": [{"issueTypeId": "default", "fieldConfigurationId": str(fc["id"])}]})
        print(f"created field configuration scheme {fcs['id']}")
    api("PUT", "/fieldconfigurationscheme/project",
        {"projectId": proj["id"], "fieldConfigurationSchemeId": str(fcs["id"])})
    print("attached screens and field configuration schemes")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "validate":
        sys.exit(0 if validate() else 1)
    elif mode == "apply":
        apply()
    else:
        sys.exit(__doc__)
