# Kimai MCP Server

A Model Context Protocol (MCP) server that lists and manages Kimai activities against your instance.

## Purpose
Provide simple tools for assistants to list, create, update, and annotate Kimai activities to speed up filling timesheet activities.

## Features

### Current Implementation
- `kimai_ping` - Connectivity check using your token.
- `kimai_version` - Show Kimai version info.
- `kimai_list_activities` - List activities with filters: term/project/visible.
- `kimai_get_activity` - Fetch one activity by ID.
- `kimai_create_activity` - Create a new activity (name, optional project, visible).
- `kimai_update_activity` - Update an existing activity (any subset).
- `kimai_set_activity_meta` - Set a configured meta-field on an activity.

## APIs & Auth
- Base URL (default): https://kimai.mindfactory.com.mx
- Auth: Bearer token in `Authorization` header.
- HTTPS required.

## Prerequisites
- Docker Desktop with MCP Toolkit enabled
- Docker MCP CLI plugin (`docker mcp`)
- A valid Kimai API token from your user profile

## Usage Examples
In Claude Desktop, try:
- `kimai_ping`
- `kimai_version`
- `kimai_list_activities term="design" visible="1"`
- `kimai_create_activity name="Sprint Planning" project="42" visible="1"`
- `kimai_update_activity id="101" name="Sprint Planning (Q4)"`
- `kimai_set_activity_meta id="101" meta_name="cost_center" meta_value="RND-42"`

## Environment
- `KIMAI_BASE_URL` (optional) – defaults to https://kimai.mindfactory.com.mx
- `KIMAI_API_TOKEN` (required) – your Kimai API token

## Architecture
Claude Desktop → MCP Gateway → Kimai MCP Server → Kimai REST API
↓
Docker Desktop Secrets (`KIMAI_API_TOKEN`)

## Development

### Local Testing
```bash
# Set environment variables for testing
export KIMAI_API_TOKEN="test-token"
export KIMAI_BASE_URL="https://kimai.mindfactory.com.mx"

# Run directly
python kimai_server.py

# Test MCP protocol
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python kimai_server.py
