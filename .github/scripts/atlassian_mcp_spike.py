#!/usr/bin/env python3
"""Spike: can a CI job talk to the Atlassian Rovo MCP server with an API token?

Talks to the MCP endpoint directly (JSON-RPC over streamable HTTP), without Claude Code, so
that authentication and tool availability are tested apart from the plugin configuration.

Checks, in order (each prints PASS/FAIL, the script exits non-zero if any FAIL):
  1. initialize                  -> the token is accepted
  2. tools/list                  -> which tools exist with token auth; the ones atlassian-toolkit
                                    needs are compared against the list
  3. getAccessibleAtlassianResources -> the token sees the JTTC site
  4. searchJiraIssuesUsingJql    -> a read on project JTTC
  5. addOrEditJiraIssueComment   -> a write, ONLY when WRITE_ISSUE_KEY is set

Secrets come from the environment and are never printed:
  ATLASSIAN_EMAIL, ATLASSIAN_API_TOKEN
"""
import base64
import json
import os
import sys
import urllib.error
import urllib.request

ENDPOINT = os.environ.get("MCP_URL", "https://mcp.atlassian.com/v2/mcp")
CLOUD_ID = os.environ.get("CLOUD_ID", "41be3e35-e509-4a4c-93e1-5460248e11ab")
SITE_HOST = os.environ.get("SITE_HOST", "jumptothecloud.atlassian.net")
WRITE_ISSUE_KEY = os.environ.get("WRITE_ISSUE_KEY", "").strip()

# Tools the atlassian-toolkit agent and skills call (see agents/atlassian-operator.md).
REQUIRED_TOOLS = [
    "atlassianUserInfo",
    "getAccessibleAtlassianResources",
    "discover",
    "executeRead",
    "executeWrite",
    "getJiraIssue",
    "searchJiraIssuesUsingJql",
    "createJiraIssue",
    "editJiraIssue",
    "transitionJiraIssue",
    "addOrEditJiraIssueComment",
    "listJiraIssueComments",
    "getConfluenceContent",
    "searchConfluence",
    "createConfluenceContent",
    "updateConfluenceContent",
]

failures = []
session_id = None
_next_id = 0


def auth_candidates():
    """Return [(label, Authorization header value)] to try, in order, until initialize works.

    The MCP guide documents Basic (email:token) for personal tokens and Bearer for service
    account API keys. A service account *token* with its email fits neither case cleanly, so
    both forms are tried and the one that works is reported.
    """
    candidates = []
    api_key = os.environ.get("ATLASSIAN_API_KEY", "")
    if api_key:
        candidates.append(("service account API key (Bearer)", "Bearer " + api_key))
    email = os.environ.get("ATLASSIAN_EMAIL", "")
    token = os.environ.get("ATLASSIAN_API_TOKEN", "")
    if email and token:
        raw = f"{email}:{token}".encode()
        candidates.append(("email + token (Basic)", "Basic " + base64.b64encode(raw).decode()))
        candidates.append(("token alone (Bearer)", "Bearer " + token))
    if not candidates:
        sys.exit("FAIL: set ATLASSIAN_API_KEY, or ATLASSIAN_EMAIL and ATLASSIAN_API_TOKEN "
                 "(as repository SECRETS, not variables)")
    return candidates


CANDIDATES = auth_candidates()
AUTH = CANDIDATES[0][1]


def parse_body(content_type, text):
    """The server may answer with plain JSON or with an SSE stream; return the JSON-RPC message."""
    if "text/event-stream" in content_type:
        for line in text.splitlines():
            if line.startswith("data:"):
                payload = line[5:].strip()
                if payload:
                    return json.loads(payload)
        return None
    return json.loads(text) if text.strip() else None


def rpc(method, params=None, notification=False):
    global session_id, _next_id
    message = {"jsonrpc": "2.0", "method": method}
    if params is not None:
        message["params"] = params
    if not notification:
        _next_id += 1
        message["id"] = _next_id
    headers = {
        "Authorization": AUTH,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(message).encode(), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            session_id = resp.headers.get("Mcp-Session-Id") or session_id
            body = resp.read().decode()
            return parse_body(resp.headers.get("Content-Type", ""), body)
    except urllib.error.HTTPError as err:
        detail = err.read().decode(errors="replace")[:500]
        raise RuntimeError(f"HTTP {err.code} {err.reason}: {detail}") from None


def check(name, fn):
    try:
        detail = fn()
        print(f"PASS  {name}" + (f" - {detail}" if detail else ""))
    except Exception as exc:  # noqa: BLE001 - a spike reports every failure and keeps going
        failures.append(name)
        print(f"FAIL  {name} - {exc}")


def call_tool(name, arguments):
    reply = rpc("tools/call", {"name": name, "arguments": arguments})
    if reply is None:
        raise RuntimeError("empty reply")
    if "error" in reply:
        raise RuntimeError(json.dumps(reply["error"])[:500])
    result = reply["result"]
    text = " ".join(c.get("text", "") for c in result.get("content", []))
    if result.get("isError"):
        raise RuntimeError(text[:500])
    return text


def step_initialize():
    global AUTH, session_id
    errors = []
    for label, header in CANDIDATES:
        AUTH = header
        session_id = None
        try:
            reply = rpc(
                "initialize",
                {
                    "protocolVersion": "2025-03-26",
                    "capabilities": {},
                    "clientInfo": {"name": "atlassian-mcp-spike", "version": "0"},
                },
            )
        except RuntimeError as exc:
            errors.append(f"{label}: {exc}")
            continue
        if reply is None or "error" in reply:
            errors.append(f"{label}: {json.dumps(reply)[:300]}")
            continue
        rpc("notifications/initialized", notification=True)
        info = reply["result"].get("serverInfo", {})
        return (f"accepted with [{label}]; server {info.get('name')} {info.get('version')}, "
                f"session {'set' if session_id else 'none'}")
    raise RuntimeError("no authentication form accepted -> " + " | ".join(errors))


tools_seen = {}


def step_tools_list():
    cursor = None
    while True:
        reply = rpc("tools/list", {"cursor": cursor} if cursor else {})
        if reply is None or "error" in reply:
            raise RuntimeError(json.dumps(reply)[:500])
        for tool in reply["result"].get("tools", []):
            tools_seen[tool["name"]] = tool
        cursor = reply["result"].get("nextCursor")
        if not cursor:
            break
    missing = [t for t in REQUIRED_TOOLS if t not in tools_seen]
    print("      tools exposed with this token:", ", ".join(sorted(tools_seen)))
    if missing:
        raise RuntimeError("tools the toolkit needs but the token does not expose: " + ", ".join(missing))
    return f"{len(tools_seen)} tools, all {len(REQUIRED_TOOLS)} required ones present"


SITE_FORMS = [("cloudId UUID", CLOUD_ID), ("hostname", SITE_HOST)]


def step_resources():
    # Informational: read:me / read:account are OAuth scopes and may not exist for API tokens.
    # The toolkit skills carry the cloudId, so this tool is not needed if the others work.
    try:
        text = call_tool("getAccessibleAtlassianResources", {})
    except RuntimeError as exc:
        return f"not usable with this token (ok if the others pass): {str(exc)[:160]}"
    return "JTTC site visible" if CLOUD_ID in text else "answered, JTTC not listed"


def step_userinfo():
    text = call_tool("atlassianUserInfo", {})
    return f"{len(text)} chars returned (account id not printed)"


def first_working(tool, build_args):
    """Try the site in each form (UUID, hostname); pass if any works and say which."""
    errors = []
    for label, site in SITE_FORMS:
        try:
            text = call_tool(tool, build_args(site))
            return f"worked with {label}; {len(text)} chars returned"
        except RuntimeError as exc:
            errors.append(f"{label}: {str(exc)[:200]}")
    raise RuntimeError(" | ".join(errors))


def step_read():
    return first_working(
        "searchJiraIssuesUsingJql",
        lambda site: {"cloudId": site, "jql": "project = JTTC ORDER BY created DESC", "maxResults": 1},
    )


def step_confluence():
    return first_working(
        "searchConfluence",
        lambda site: {"cloudId": site, "cql": "type = page", "limit": 1},
    )


def step_write():
    text = call_tool(
        "addOrEditJiraIssueComment",
        {
            "cloudId": CLOUD_ID,
            "issueIdOrKey": WRITE_ISSUE_KEY,
            "commentBody": "Spike: headless API-token write from CI (safe to delete this comment).",
        },
    )
    return f"comment added on {WRITE_ISSUE_KEY}"


check("1 initialize (token accepted)", step_initialize)
if "1 initialize (token accepted)" not in failures:
    check("2 tools/list", step_tools_list)
    check("3 getAccessibleAtlassianResources (informational)", step_resources)
    check("4 atlassianUserInfo", step_userinfo)
    check("5 read Jira: searchJiraIssuesUsingJql", step_read)
    check("6 read Confluence: searchConfluence", step_confluence)
    if WRITE_ISSUE_KEY:
        check("7 write: addOrEditJiraIssueComment", step_write)
    else:
        print("SKIP  7 write (set WRITE_ISSUE_KEY to test it)")

print()
if failures:
    print("RESULT: FAIL -", "; ".join(failures))
    sys.exit(1)
print("RESULT: PASS")
