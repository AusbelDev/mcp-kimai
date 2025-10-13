Sure! Here’s the full README content directly in **Markdown**, ready to save as `README.md`:

---


# Kimai MCP Server

A **Model Context Protocol (MCP)** server that connects to your Kimai instance to list, create, and manage activities and projects directly from Claude Desktop.

---

## 🎯 Purpose

This MCP server provides a simple bridge between Claude Desktop and your company’s **Kimai** time-tracking system (`https://kimai.mindfactory.com.mx/`), allowing you to:

- Browse activities and projects  
- Create and edit activities  
- Update meta-fields  
- Quickly check connectivity and version information

---

## 🧩 Features

### Current Tools

| Tool | Description |
|------|--------------|
| `kimai_ping` | Verifies connectivity and authentication |
| `kimai_version` | Displays Kimai server version |
| `kimai_list_projects` | Lists projects filtered by term, customer, or visibility |
| `kimai_list_activities` | Lists activities filtered by term, project, or visibility |
| `kimai_get_activity` | Fetches details of one activity by ID |
| `kimai_create_activity` | Creates a new activity |
| `kimai_update_activity` | Updates existing activity attributes |
| `kimai_set_activity_meta` | Sets or updates a meta-field value on an activity |

---

## 🔒 Authentication

Your Kimai instance requires **X-AUTH headers** (not Bearer tokens).  
Each request must include:

```

X-AUTH-USER: <your username>
X-AUTH-TOKEN: <your API token>

````

### Required Environment Variables

| Variable | Description | Example |
|-----------|--------------|----------|
| `KIMAI_USER` | Your Kimai username | `john.doe` |
| `KIMAI_TOKEN` | Your Kimai API token (generated in profile) | `kT-abc123xyz` |
| `KIMAI_BASE_URL` | (Optional) Override the default Kimai URL | `https://kimai.mindfactory.com.mx` |

---

## 🧠 API Overview

- **Base URL:** `https://kimai.mindfactory.com.mx`  
- **Protocol:** HTTPS (required)  
- **Authentication:** `X-AUTH-USER` and `X-AUTH-TOKEN`  
- **Endpoints used:**
  - `/api/ping`
  - `/api/version`
  - `/api/projects`
  - `/api/activities`
  - `/api/activities/{id}`
  - `/api/activities/{id}/meta`

---

## 🧰 Installation

### 1. Prerequisites
- Docker Desktop with **MCP Toolkit** enabled  
- Docker MCP CLI plugin (`docker mcp`)  
- A valid Kimai API token  

### 2. Build & Configure
```bash
mkdir kimai-mcp-server
cd kimai-mcp-server
# (Place Dockerfile, requirements.txt, kimai_server.py, readme.txt, CLAUDE.md here)
docker build -t kimai-mcp-server .
````

### 3. Secrets

```bash
docker mcp secret set KIMAI_USER="your.username"
docker mcp secret set KIMAI_TOKEN="your-api-token"
docker mcp secret set KIMAI_BASE_URL="https://kimai.mindfactory.com.mx"
docker mcp secret list
```

### 4. Custom Catalog Entry

In `~/.docker/mcp/catalogs/custom.yaml`:

```yaml
version: 2
name: custom
displayName: Custom MCP Servers
registry:
  kimai:
    description: "Manage and list Kimai activities and projects"
    title: "Kimai"
    type: server
    dateAdded: "2025-10-12T00:00:00Z"
    image: kimai-mcp-server:latest
    ref: ""
    tools:
      - name: kimai_ping
      - name: kimai_version
      - name: kimai_list_projects
      - name: kimai_list_activities
      - name: kimai_get_activity
      - name: kimai_create_activity
      - name: kimai_update_activity
      - name: kimai_set_activity_meta
    secrets:
      - name: KIMAI_USER
        env: KIMAI_USER
        example: "john.doe"
      - name: KIMAI_TOKEN
        env: KIMAI_TOKEN
        example: "kT-xxxxxxxxxxxxxxxxxxxx"
      - name: KIMAI_BASE_URL
        env: KIMAI_BASE_URL
        example: "https://kimai.mindfactory.com.mx"
    metadata:
      category: integration
      tags:
        - kimai
        - time-tracking
        - activities
        - projects
      license: MIT
      owner: local
```

---

## 💡 Usage Examples

### Ping and Version

```
kimai_ping
kimai_version
```

### List Projects

```
kimai_list_projects term="client"
kimai_list_projects customer="3" visible="1"
```

### List Activities

```
kimai_list_activities term="meeting"
kimai_list_activities project="42"
```

### Manage Activities

```
kimai_create_activity name="Internal Review" project="42"
kimai_update_activity id="85" name="Client Call"
kimai_set_activity_meta id="85" meta_name="priority" meta_value="high"
```

---

## 🏗️ Development

### Local Testing

```bash
export KIMAI_USER="testuser"
export KIMAI_TOKEN="apitoken"
export KIMAI_BASE_URL="https://kimai.mindfactory.com.mx"
python kimai_server.py
```

### JSON-RPC Test

```bash
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python kimai_server.py
```

---

## 🧱 Architecture

Claude Desktop → MCP Gateway → **Kimai MCP Server** → **Kimai REST API**
↓
Docker Desktop Secrets (`KIMAI_USER`, `KIMAI_TOKEN`, `KIMAI_BASE_URL`)

---

## 🧰 Troubleshooting

**❌ Authentication required / missing headers**
→ Ensure `KIMAI_USER` and `KIMAI_TOKEN` are set.
→ Rebuild the Docker image if environment changed.

**⚠️ No activities/projects found**
→ Try with different filters (`visible="1"`) or check project IDs.

**Tools not appearing**
→ Confirm image built successfully and `custom.yaml` is in your catalog path.

**Malformed response (`int object has no attribute get`)**
→ Fixed in latest version: functions now support both integer and object response formats.

---

## 🔒 Security Notes

* Credentials stored securely as Docker secrets
* Runs under a non-root user inside container
* Never logs tokens or sensitive data
* Uses HTTPS for all API communication

---

