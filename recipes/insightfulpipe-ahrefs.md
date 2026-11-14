# Recipe: Connecting Ahrefs to Insightful Pipe via Generic REST API Connector

This recipe documents how to connect **Ahrefs** to **Insightful Pipe** using Insightful Pipe's generic REST API connector.

Insightful Pipe offers 46 native integrations (including Google Analytics 4, Instagram, Meta Ads, TikTok, Google Search Console, Bing Webmaster Tools, and DataForSEO), but does not have a native Ahrefs connector. Connecting Ahrefs through the REST API connector exposes Ahrefs SEO metrics directly to Insightful Pipe workspaces and MCP toolsets.

---

## Technical Obstacles with Raw Ahrefs OpenAPI Specs

Directly pointing Insightful Pipe to the official Ahrefs OpenAPI URL (`https://docs.ahrefs.com/openapi.json`) or uploading raw sub-specs from `https://docs.ahrefs.com/reference/` fails due to four specific constraints:

1. **512 KB Manifest Limit**:
   - The full Ahrefs API v3 specification covers 154 endpoints and is **2.8 MB**.
   - Insightful Pipe enforces a strict 512 KB limit on manifests, returning:
     > `Could not generate a preview. Manifest exceeded the 524288 byte limit.`

2. **Enum Size Cap (200 values)**:
   - Ahrefs defines exhaustive lists of 249 ISO country codes on query parameters (`country`) and response schemas.
   - Insightful Pipe's backend validator rejects enums with more than 200 items, returning:
     > `parameter 'country' exceeds the maximum supported enum size of 200 values.`

3. **OpenAPI 3.1 vs. 3.0 Incompatibilities**:
   - Ahrefs uses OpenAPI 3.1 / 3.2 schema features, such as `examples` (plural) lists inside parameter schema objects.
   - Insightful Pipe validates against OpenAPI 3.0.x rules where `examples` inside a `schema` object causes a validation failure:
     > `OpenAPI validation failed: ... is not valid under any of the given schemas (Failed validating 'oneOf')`

4. **Upstream Schema Bugs**:
   - Certain Ahrefs endpoints have default values that violate their own enum definitions (e.g. an empty default `""` in a country enum list on `/volume-by-country`), causing strict validators to fail:
     > `OpenAPI validation failed: '' is not one of ['ad', 'ae', ...]`

5. **Tool Context Overhead**:
   - Exposing 154 raw endpoints into an AI agent's tool context consumes substantial prompt tokens on every turn. Curating a high-signal set of 5–10 endpoints delivers the necessary SEO data with minimal token overhead.

---

## Curated Endpoints for Store/Brand SEO

For e-commerce stores (such as MangaJDM), the 6 most impactful endpoints are:

| Endpoint | Method | Purpose |
| :--- | :--- | :--- |
| `/site-explorer/metrics` | GET | Domain overview: organic traffic, organic traffic value, paid traffic, and historical trends. |
| `/site-explorer/domain-rating` | GET | Domain Rating (DR) and referring domain counts. |
| `/site-explorer/organic-keywords` | GET | Ranked search queries, positions, traffic share, and URL mappings. |
| `/site-explorer/top-pages` | GET | Top organic traffic-driving pages. |
| `/site-explorer/backlinks-stats` | GET | Total backlinks, referring domains, live vs. broken links. |
| `/keywords-explorer/overview` | GET | Search volume, keyword difficulty (KD), and click metrics for target terms. |

---

## Python Spec Generator & Sanitizer

Run this script to fetch the upstream Ahrefs v3 spec, extract the target endpoints, resolve all referenced `$ref` components, sanitize country enums, and output a valid OpenAPI 3.0.3 file under 100 KB:

```python
import json
import urllib.request

AHREFS_SPEC_URL = "https://docs.ahrefs.com/openapi.json"

TARGET_PATHS = [
    "/site-explorer/metrics",
    "/site-explorer/domain-rating",
    "/site-explorer/organic-keywords",
    "/site-explorer/top-pages",
    "/site-explorer/backlinks-stats",
    "/keywords-explorer/overview",
]

# 1. Fetch upstream spec
req = urllib.request.Request(AHREFS_SPEC_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    raw_data = json.load(resp)

filtered_paths = {p: raw_data["paths"][p] for p in TARGET_PATHS if p in raw_data["paths"]}

# 2. Recursively extract all referenced components
components = {
    "securitySchemes": {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Key",
        }
    },
    "schemas": {},
    "parameters": {},
    "responses": {},
}

def extract_refs(obj):
    refs = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str) and v.startswith("#/components/"):
                parts = v.split("/")
                if len(parts) == 4:
                    refs.add((parts[2], parts[3]))
            else:
                refs.update(extract_refs(v))
    elif isinstance(obj, list):
        for item in obj:
            refs.update(extract_refs(item))
    return refs

unresolved = extract_refs(filtered_paths)
resolved = set()

while unresolved:
    kind, name = unresolved.pop()
    if (kind, name) in resolved:
        continue
    resolved.add((kind, name))
    if kind in raw_data.get("components", {}) and name in raw_data["components"][kind]:
        item = raw_data["components"][kind][name]
        if kind not in components:
            components[kind] = {}
        components[kind][name] = item
        new_refs = extract_refs(item)
        unresolved.update(new_refs - resolved)

# 3. Sanitize enums exceeding 200 items (e.g. country codes) and fix OpenAPI 3.1 examples
def sanitize(obj):
    if isinstance(obj, dict):
        # Strip enums larger than 50 items (country lists) to avoid the 200 enum limit
        if "enum" in obj and isinstance(obj["enum"], list) and len(obj["enum"]) > 50:
            del obj["enum"]
            obj["type"] = "string"
            if "example" not in obj:
                obj["example"] = "us"
        # Remove invalid enum defaults
        if "enum" in obj and "default" in obj and obj["default"] not in obj["enum"]:
            del obj["default"]
        # Convert OpenAPI 3.1 schema.examples to OpenAPI 3.0 schema.example
        if "examples" in obj and isinstance(obj["examples"], list):
            if "example" not in obj and len(obj["examples"]) > 0:
                obj["example"] = obj["examples"][0]
            del obj["examples"]
        for v in obj.values():
            sanitize(v)
    elif isinstance(obj, list):
        for item in obj:
            sanitize(item)

sanitize(filtered_paths)
sanitize(components)

# 4. Construct valid OpenAPI 3.0.3 specification
curated_spec = {
    "openapi": "3.0.3",
    "info": {
        "title": "Ahrefs API for Insightful Pipe",
        "description": "Curated Ahrefs API v3 endpoints for domain metrics, keywords, and backlinks.",
        "version": "3.0.0",
    },
    "servers": [{"url": "https://api.ahrefs.com/v3"}],
    "security": [{"bearerAuth": []}],
    "paths": filtered_paths,
    "components": components,
}

output_path = "brands/mangajdm/ahrefs-openapi.json"
with open(output_path, "w") as f:
    json.dump(curated_spec, f, indent=2)

print(f"Generated {output_path} (size: {len(json.dumps(curated_spec))} bytes)")
```

---

## Step-by-Step Setup Guide in Insightful Pipe

### Step 1: Obtain Your Ahrefs API Key
1. Log in to [Ahrefs](https://app.ahrefs.com/).
2. Navigate to **Account settings > API keys** (`https://app.ahrefs.com/account/api-keys`).
3. Under **API keys**, click **Generate API key** (or copy an existing active API v3 token). Note: This is an API key (`Authorization: Bearer <TOKEN>`), not an MCP key.

### Step 2: Open Insightful Pipe Connector Setup
1. In Insightful Pipe, navigate to **Connected accounts** > **Add integration**.
2. Select **REST API** (`/connectors/rest-api/new/`).
3. Set **Name**: `Ahrefs`.

### Step 3: Configure Authentication
1. Under **Auth type**, select **BEARER TOKEN**.
2. Paste your Ahrefs API key into the **Bearer token** input field.

### Step 4: Supply the OpenAPI Specification
1. Choose either:
   - **PASTE**: Select the **PASTE** tab and paste the contents of `brands/mangajdm/ahrefs-openapi.json`.
   - **UPLOAD**: Select the **UPLOAD** tab and choose `brands/mangajdm/ahrefs-openapi.json` from disk.
2. Click **Load the endpoints** under **Preview / Connector runner**.
3. Verify that the 6 endpoints appear in the list with `TRY` and `REMOVE` buttons:
   - `GET /site-explorer/metrics`
   - `GET /site-explorer/domain-rating`
   - `GET /site-explorer/organic-keywords`
   - `GET /site-explorer/top-pages`
   - `GET /site-explorer/backlinks-stats`
   - `GET /keywords-explorer/overview`

### Step 5: Save & Activate
1. Click **Save & activate** in the top right header.
2. The Ahrefs integration is now active and exposed to Insightful Pipe's workspace and MCP servers.

---

## Alternative: Ahrefs Official MCP Server

If you only need AI agents (such as Claude Desktop, Cursor, or T3 Code) to query Ahrefs directly without unifying data in Insightful Pipe:

1. Ahrefs provides an official native MCP server: [`github.com/ahrefs/ahrefs-mcp-server`](https://github.com/ahrefs/ahrefs-mcp-server).
2. On the Ahrefs API keys page, click **Generate MCP key**.
3. Add the MCP server configuration directly to your AI client's config file (e.g. `claude_desktop_config.json`).
