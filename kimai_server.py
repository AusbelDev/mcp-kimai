#!/usr/bin/env python3
"""
Simple Kimai MCP Server - Manage and list Kimai activities via REST API.
"""
import os
import sys
import logging
from datetime import datetime, timezone
import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging to stderr
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)
logger = logging.getLogger("kimai-server")

# Initialize MCP server - NO PROMPT PARAMETER!
mcp = FastMCP("kimai")

# === CONFIGURATION ===
DEFAULT_BASE_URL = "https://kimai.mindfactory.com.mx"
KIMAI_BASE_URL = os.environ.get("KIMAI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
KIMAI_TOKEN = os.environ.get("KIMAI_TOKEN", "")

def now_utc_iso():
    """Return ISO8601 timestamp in UTC."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def auth_headers():
    """Return headers for Kimai X-AUTH-USER / X-AUTH-TOKEN authentication."""
    user = (os.environ.get("KIMAI_USER") or "").strip()
    token = (os.environ.get("KIMAI_TOKEN") or "").strip()
    if not user or not token:
        return {}
    return {"X-AUTH-USER": user, "X-AUTH-TOKEN": token}

def base_url():
    """Return configured Kimai base URL without trailing slash."""
    return (os.environ.get("KIMAI_BASE_URL", KIMAI_BASE_URL) or DEFAULT_BASE_URL).rstrip("/")

def missing_token_msg():
    """Return a friendly message if API token is missing."""
    return ("❌ Error: KIMAI_API_TOKEN is not set. "
            "Create an API token in your Kimai profile and pass it as a Docker secret/env.")

# === LOW-LEVEL HTTP HELPERS ===
async def get_json(client, path, params=None):
    """Perform a GET and return JSON with friendly errors."""
    if not (KIMAI_TOKEN or "").strip():
        return None, missing_token_msg()
    url = f"{base_url()}{path}"
    try:
        r = await client.get(url, headers=auth_headers(), params=params or {}, timeout=15)
        r.raise_for_status()
        return r.json(), ""
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.text
        except Exception:
            detail = ""
        return None, f"❌ API Error {e.response.status_code} on GET {path}: {detail}"
    except Exception as e:
        return None, f"❌ Network Error on GET {path}: {str(e)}"

async def post_json(client, path, body=None, params=None):
    """Perform a POST and return JSON with friendly errors."""
    if not (KIMAI_TOKEN or "").strip():
        return None, missing_token_msg()
    url = f"{base_url()}{path}"
    try:
        r = await client.post(url, headers=auth_headers(), json=body or {}, params=params or {}, timeout=20)
        r.raise_for_status()
        return r.json(), ""
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.text
        except Exception:
            detail = ""
        return None, f"❌ API Error {e.response.status_code} on POST {path}: {detail}"
    except Exception as e:
        return None, f"❌ Network Error on POST {path}: {str(e)}"

async def patch_json(client, path, body=None, params=None):
    """Perform a PATCH and return JSON with friendly errors."""
    if not (KIMAI_TOKEN or "").strip():
        return None, missing_token_msg()
    url = f"{base_url()}{path}"
    try:
        r = await client.patch(url, headers=auth_headers(), json=body or {}, params=params or {}, timeout=20)
        r.raise_for_status()
        return r.json(), ""
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.text
        except Exception:
            detail = ""
        return None, f"❌ API Error {e.response.status_code} on PATCH {path}: {detail}"
    except Exception as e:
        return None, f"❌ Network Error on PATCH {path}: {str(e)}"

# === FORMATTING HELPERS ===
def fmt_activity_row(a):
    """Render one activity line."""
    if not isinstance(a, dict):
        return f"- [unexpected item: {a}]"

    aid = a.get("id", "n/a")
    name = a.get("name", "n/a")

    # project can be an int ID or an embedded object
    proj = a.get("project")
    if isinstance(proj, dict):
        pid = proj.get("id", "")
        pnm = proj.get("name", "")
    elif isinstance(proj, int):
        pid = proj
        pnm = ""
    else:
        pid = str(proj) if proj not in (None, "") else ""
        pnm = ""

    vis = a.get("visible", True)
    vis_flag = 1 if str(vis).lower() in ("1", "true") or vis is True else 0

    return f"- #{aid} • {name} • project:{pid or '—'} {pnm or ''} • visible:{vis_flag}"


def parse_bool_flag(val):
    """Parse a visibility flag string to bool or None."""
    s = (val or "").strip().lower()
    if s in ("1", "true", "yes", "y", "on"):
        return True
    if s in ("0", "false", "no", "n", "off"):
        return False
    return None

def parse_int_or_empty(s):
    """Parse int from string or return empty string if invalid."""
    try:
        return int(s.strip()) if s.strip() else ""
    except Exception:
        return ""

# === MCP TOOLS ===

@mcp.tool()
async def kimai_ping() -> str:
    """Ping the Kimai API to verify connectivity and token."""
    logger.info("kimai_ping")
    try:
        async with httpx.AsyncClient() as client:
            j, err = await get_json(client, "/api/ping")
            if err:
                return err
            return f"✅ kimai_ping OK at {now_utc_iso()} • Response: {str(j)}"
    except Exception as e:
        logger.error(f"kimai_ping error: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def kimai_version() -> str:
    """Get Kimai version info."""
    logger.info("kimai_version")
    try:
        async with httpx.AsyncClient() as client:
            j, err = await get_json(client, "/api/version")
            if err:
                return err
            return f"✅ Version: {j}"
    except Exception as e:
        logger.error(f"kimai_version error: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def kimai_list_activities(term: str = "", project: str = "", visible: str = "") -> str:
    """List activities filtered by optional term/project/visible."""
    logger.info(f"kimai_list_activities term='{term}' project='{project}' visible='{visible}'")
    try:
        params = {}
        if term.strip():
            params["term"] = term.strip()
        pid = parse_int_or_empty(project)
        if pid != "":
            params["project"] = str(pid)
        vis_flag = parse_bool_flag(visible)
        if vis_flag is not None:
            params["visible"] = "1" if vis_flag else "2"
        async with httpx.AsyncClient() as client:
            j, err = await get_json(client, "/api/activities", params=params)
            if err:
                return err
            # API may return array of collections; normalize to list of objects
            rows = []
            if isinstance(j, list):
                for item in j:
                    # try common shapes
                    a = item.get("activity") if isinstance(item, dict) and "activity" in item else item
                    if isinstance(a, dict):
                        rows.append(fmt_activity_row(a))
            elif isinstance(j, dict):
                rows.append(fmt_activity_row(j))
            if not rows:
                return "⚠️ No activities found for given filters."
            header = f"📊 Activities ({len(rows)}) • fetched {now_utc_iso()}"
            return "\n".join([header, ""] + rows)
    except Exception as e:
        logger.error(f"kimai_list_activities error: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def kimai_get_activity(id: str = "") -> str:
    """Get one activity by ID."""
    logger.info(f"kimai_get_activity id='{id}'")
    if not id.strip():
        return "❌ Error: id is required"
    try:
        async with httpx.AsyncClient() as client:
            j, err = await get_json(client, f"/api/activities/{id.strip()}")
            if err:
                return err
            return f"✅ Activity #{id.strip()}:\n{j}"
    except Exception as e:
        logger.error(f"kimai_get_activity error: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def kimai_create_activity(name: str = "", project: str = "", visible: str = "1") -> str:
    """Create a new activity (requires name; optional project, visible)."""
    logger.info(f"kimai_create_activity name='{name}' project='{project}' visible='{visible}'")
    if not name.strip():
        return "❌ Error: name is required"
    try:
        body = {"name": name.strip()}
        pid = parse_int_or_empty(project)
        if pid != "":
            body["project"] = pid
        vis_flag = parse_bool_flag(visible)
        if vis_flag is not None:
            body["visible"] = 1 if vis_flag else 0
        async with httpx.AsyncClient() as client:
            j, err = await post_json(client, "/api/activities", body=body)
            if err:
                return err
            return f"✅ Created activity:\n{j}"
    except Exception as e:
        logger.error(f"kimai_create_activity error: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def kimai_update_activity(id: str = "", name: str = "", project: str = "", visible: str = "") -> str:
    """Update an activity (any subset of name/project/visible)."""
    logger.info(f"kimai_update_activity id='{id}' name='{name}' project='{project}' visible='{visible}'")
    if not id.strip():
        return "❌ Error: id is required"
    try:
        body = {}
        if name.strip():
            body["name"] = name.strip()
        pid = parse_int_or_empty(project)
        if pid != "":
            body["project"] = pid
        vis_flag = parse_bool_flag(visible)
        if vis_flag is not None:
            body["visible"] = 1 if vis_flag else 0
        if not body:
            return "⚠️ Nothing to update. Provide at least one of: name, project, visible."
        async with httpx.AsyncClient() as client:
            j, err = await patch_json(client, f"/api/activities/{id.strip()}", body=body)
            if err:
                return err
            return f"✅ Updated activity #{id.strip()}:\n{j}"
    except Exception as e:
        logger.error(f"kimai_update_activity error: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def kimai_set_activity_meta(id: str = "", meta_name: str = "", meta_value: str = "") -> str:
    """Set a configured meta-field on an activity."""
    logger.info(f"kimai_set_activity_meta id='{id}' name='{meta_name}'")
    if not id.strip():
        return "❌ Error: id is required"
    if not meta_name.strip():
        return "❌ Error: meta_name is required"
    try:
        body = {"name": meta_name.strip(), "value": meta_value}
        async with httpx.AsyncClient() as client:
            j, err = await patch_json(client, f"/api/activities/{id.strip()}/meta", body=body)
            if err:
                return err
            return f"✅ Set meta on activity #{id.strip()}:\n{j}"
    except Exception as e:
        logger.error(f"kimai_set_activity_meta error: {e}")
        return f"❌ Error: {str(e)}"
    
@mcp.tool()
async def kimai_list_customers(term: str = "") -> str:
    """List customers filtered by optional term."""
    logger.info(f"kimai_list_customers term='{term}'")
    try:
        params = {}
        if term.strip():
            params["term"] = term.strip()
        async with httpx.AsyncClient() as client:
            j, err = await get_json(client, "/api/customers", params=params)
            if err:
                return err
            rows = []
            if isinstance(j, list):
                for c in j:
                    cid = c.get("id", "n/a")
                    name = c.get("name", "n/a")
                    rows.append(f"- #{cid} • {name}")
            if not rows:
                return "⚠️ No customers found for given filters."
            header = f"📋 Customers ({len(rows)}) • fetched {now_utc_iso()}"
            return "\n".join([header, ""] + rows)
    except Exception as e:
        logger.error(f"kimai_list_customers error: {e}")
        return f"❌ Error: {str(e)}"

@mcp.tool()
async def kimai_create_timesheet(activity: str = "", begin: str = "", end: str = "", description: str = "", customer: str = "", project: str = "") -> str:
    """Create a new timesheet entry (requires activity, begin; optional end, description, customer, project)."""
    logger.info(f"kimai_create_timesheet activity='{activity}' begin='{begin}' end='{end}' customer='{customer}' project='{project}'")
    if not activity.strip():
        return "❌ Error: activity is required"
    if not begin.strip():
        return "❌ Error: begin is required"
    try:
        body = {"activity": parse_int_or_empty(activity), "begin": begin.strip()}
        if end.strip():
            body["end"] = end.strip()
        if description.strip():
            body["description"] = description.strip()
        cid = parse_int_or_empty(customer)
        if cid != "":
            body["customer"] = cid
        pid = parse_int_or_empty(project)
        if pid != "":
            body["project"] = pid
        async with httpx.AsyncClient() as client:
            j, err = await post_json(client, "/api/timesheets", body=body)
            if err:
                return err
            return f"✅ Created timesheet entry:\n{j}"
    except Exception as e:
        logger.error(f"kimai_create_timesheet error: {e}")
        return f"❌ Error: {str(e)}"
    
@mcp.tool()
async def kimai_list_projects(term: str = "", customer: str = "", visible: str = "") -> str:
    """List projects filtered by optional term/customer/visible."""
    logger.info(f"kimai_list_projects term='{term}' customer='{customer}' visible='{visible}'")
    try:
        params = {}
        if term.strip():
            params["term"] = term.strip()

        # customer can be int; stringify only if valid
        cid_filter = parse_int_or_empty(customer)
        if cid_filter != "":
            params["customer"] = str(cid_filter)

        # visible: map truthy to 1 (visible) / 2 (hidden)
        vis_flag = parse_bool_flag(visible)
        if vis_flag is not None:
            params["visible"] = "1" if vis_flag else "2"

        async with httpx.AsyncClient() as client:
            j, err = await get_json(client, "/api/projects", params=params)
            if err:
                return err

            # Normalize payload to a list of project dicts
            items = []
            if isinstance(j, list):
                items = j
            elif isinstance(j, dict):
                # Some installs might wrap results; try common containers
                if "data" in j and isinstance(j["data"], list):
                    items = j["data"]
                else:
                    items = [j]
            else:
                return "⚠️ Unexpected response format from /api/projects"

            rows = []
            for p in items:
                try:
                    # Some serializers nest under "project"
                    proj = p.get("project") if isinstance(p, dict) else None
                    if isinstance(proj, dict):
                        p = proj

                    if not isinstance(p, dict):
                        logger.info(f"Skipping non-dict project item: {p}")
                        continue

                    pid = p.get("id", "n/a")
                    name = p.get("name", "n/a")

                    # customer can be int ID or embedded object
                    cust = p.get("customer", {})
                    if isinstance(cust, dict):
                        cid = cust.get("id", "")
                        cnm = cust.get("name", "")
                    elif isinstance(cust, int):
                        cid = cust
                        cnm = ""
                    else:
                        # string or None
                        cid = str(cust) if cust not in (None, "") else ""
                        cnm = ""

                    vis = p.get("visible", True)
                    rows.append(f"- #{pid} • {name} • customer:{cid or '—'} {cnm or ''} • visible:{1 if vis else 0}")
                except Exception as inner_e:
                    logger.error(f"Project parse error: {inner_e}; raw={p}")
                    continue

            if not rows:
                return "⚠️ No projects found for given filters."
            header = f"📂 Projects ({len(rows)}) • fetched {now_utc_iso()}"
            return "\n".join([header, ""] + rows)

    except Exception as e:
        logger.error(f"kimai_list_projects error: {e}")
        return f"❌ Error: {str(e)}"


# === SERVER STARTUP ===
if __name__ == "__main__":
    logger.info("Starting Kimai MCP server...")
    if not (KIMAI_TOKEN or "").strip():
        logger.warning("KIMAI_API_TOKEN not set; tools will return a friendly error until provided.")
    try:
        mcp.run(transport='stdio')
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)
