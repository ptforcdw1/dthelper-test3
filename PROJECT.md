# DTHelperPOCv3 — Monaco Configuration as Code POC

## Overview

This project demonstrates using [Monaco v2 (Dynatrace Monitoring as Code)](https://github.com/dynatrace-oss/dynatrace-monitoring-as-code) to manage Dynatrace configuration programmatically, deployed via a Jenkins CI/CD pipeline.

**Stack:**
- Monaco v2.28.7
- Jenkins (running as a Linux container in Docker Desktop on Windows)
- GitHub as the source repository
- Dynatrace tenant: `ylq89164` at `https://ylq89164.live.dynatrace.com`

---

## What We Built

### 1. Project Structure

```
DTHelperPOCv3/
├── manifest.yaml                       # Monaco entry point: defines environments + projects
├── Jenkinsfile                         # CI/CD pipeline: validate → deploy
├── .env.example                        # Template for local API token setup
├── .gitignore                          # Excludes .env, .exe, .logs/
└── configs/
    ├── log-storage/                    # ACTIVE: log ingest rule via Settings 2.0
    │   ├── config.yaml
    │   └── log-storage-rule.json
    ├── alerting-profiles/              # SKIPPED: deprecated API on this tenant
    ├── auto-tagging/                   # SKIPPED: deprecated API on this tenant
    └── dashboards/                     # SKIPPED: deprecated API on this tenant
```

### 2. Jenkins Pipeline

The pipeline has three stages:

| Stage | What it does |
|---|---|
| **Setup Monaco** | Downloads the Monaco Linux binary (cached by version number) |
| **Validate (Dry Run)** | Runs `monaco deploy --dry-run` to validate config without applying |
| **Deploy** | Runs the real deploy; skippable via `SKIP_DEPLOY` parameter |

The API token is injected from Jenkins credentials (`dynatrace-api-token`) — never stored in code.

### 3. Active Configuration

**Log ingest rule** (`builtin:logmonitoring.log-storage-settings`) — routes syslog entries to Dynatrace Log Monitoring storage.

---

## How Monaco Works

Monaco pairs a **`config.yaml`** (what to create and with which schema) with a **JSON template** (the payload, with Go template variables).

### The Three Key Files

#### `manifest.yaml` — Defines environments and projects

```yaml
manifestVersion: "1.0"

projects:
  - name: DTHelperPOCv3
    path: configs              # Monaco looks for config.yaml files under this folder

environmentGroups:
  - name: production
    environments:
      - name: ylq89164
        url:
          value: https://ylq89164.live.dynatrace.com
        auth:
          token:
            name: DT_API_TOKEN # Read from environment variable at deploy time
```

#### `config.yaml` — Declares the configuration object

Two styles: **classic API** (deprecated on modern tenants) and **Settings 2.0** (recommended).

**Settings 2.0 style (use this):**
```yaml
configs:
  - id: my-rule                          # Unique ID within the project
    config:
      name: My Rule Name                 # Becomes {{ .name }} in the template
      template: my-rule.json             # Path to the JSON template
      parameters:                        # Optional extra variables for the template
        logPath: /var/log/app.log
    type:
      settings:
        schema: builtin:logmonitoring.log-storage-settings
        scope: environment               # or HOST, HOST_GROUP, etc.
```

**Classic API style (not supported on this tenant):**
```yaml
configs:
  - id: my-dashboard
    config:
      name: My Dashboard
      template: my-dashboard.json
      skip: true                         # Set true to disable without deleting
    type:
      api: dashboard
```

#### `my-rule.json` — The payload template

Uses [Go templates](https://pkg.go.dev/text/template). Variables from `config.yaml` are injected with `{{ .variableName }}`.

```json
{
  "enabled": true,
  "config-item-title": "{{ .name }}",
  "send-to-storage": true,
  "matchers": [
    {
      "attribute": "log.source",
      "operator": "MATCHES",
      "values": ["{{ .logPath }}"]
    }
  ]
}
```

---

## Sample Monaco Configs

### Example 1 — Ownership Team (Settings 2.0)

Available schema: `builtin:ownership.teams`

**`configs/ownership/config.yaml`:**
```yaml
configs:
  - id: platform-team
    config:
      name: Platform Team
      template: platform-team.json
      parameters:
        identifier: platform-team
    type:
      settings:
        schema: builtin:ownership.teams
        scope: environment
```

**`configs/ownership/platform-team.json`:**
```json
{
  "name": "{{ .name }}",
  "identifier": "{{ .identifier }}",
  "description": "Owns platform infrastructure and observability tooling",
  "supplementaryIdentifiers": [],
  "responsibilities": {
    "development": false,
    "security": false,
    "operations": true,
    "infrastructure": true,
    "lineOfBusiness": false
  },
  "contactDetails": [],
  "links": [],
  "additionalInformation": []
}
```

### Example 2 — Attribute Allow List (Settings 2.0)

Available schema: `builtin:attribute-allow-list`

**`configs/attributes/config.yaml`:**
```yaml
configs:
  - id: allow-http-url
    config:
      name: allow-http-url
      template: allow-http-url.json
    type:
      settings:
        schema: builtin:attribute-allow-list
        scope: environment
```

**`configs/attributes/allow-http-url.json`:**
```json
{
  "enabled": true,
  "key": "http.url"
}
```

### Example 3 — Multiple environments

To deploy to multiple environments, extend the manifest and use parameters per environment:

**`manifest.yaml`:**
```yaml
manifestVersion: "1.0"

projects:
  - name: DTHelperPOCv3
    path: configs

environmentGroups:
  - name: non-production
    environments:
      - name: staging
        url:
          value: https://staging-tenant.live.dynatrace.com
        auth:
          token:
            name: DT_API_TOKEN_STAGING
  - name: production
    environments:
      - name: ylq89164
        url:
          value: https://ylq89164.live.dynatrace.com
        auth:
          token:
            name: DT_API_TOKEN
```

Deploy to a specific environment:
```bash
monaco deploy manifest.yaml --environment staging
```

---

## Local Development

### Prerequisites

- Monaco binary (`monaco.exe` on Windows, `monaco` on Linux)
- Dynatrace API token with `Read configuration` + `Write configuration` scopes

### Setup

```powershell
# Copy and fill in the template
cp .env.example .env
# Edit .env: set DT_API_TOKEN=dt0c01.XXXX...

# Load token and validate without deploying
$env:DT_API_TOKEN = (Get-Content .env | Select-String "DT_API_TOKEN=(.+)" | % { $_.Matches[0].Groups[1].Value })
.\monaco.exe deploy manifest.yaml --environment ylq89164 --dry-run

# Deploy for real
.\monaco.exe deploy manifest.yaml --environment ylq89164
```

---

## Jenkins Setup

| Setting | Value |
|---|---|
| Pipeline definition | Pipeline script from SCM |
| SCM | Git |
| Repository URL | `https://github.com/ptforcdw1/dthelper-test3.git` |
| Credentials | `github-token` (Username + PAT) |
| Branch | `*/main` |
| Script Path | `Jenkinsfile` |
| Required credential | `dynatrace-api-token` (Secret text, your DT API token) |

---

## Tenant Notes

This tenant (`ylq89164`) is a **Dynatrace Platform-only** tenant. Key findings:

- Classic config API (`/api/config/v1/*`) returns `404` — **do not use `type.api`**
- Standard Settings 2.0 schemas like `builtin:management-zones` and `builtin:tags.auto-tagging` are **not available**
- Always query available schemas before adding a new config type:

```powershell
$headers = @{ "Authorization" = "Api-Token $env:DT_API_TOKEN" }
$schemas = Invoke-RestMethod -Uri "https://ylq89164.live.dynatrace.com/api/v2/settings/schemas" -Headers $headers
$schemas.items | Select-Object schemaId, displayName | Sort-Object schemaId
```

**Confirmed available schemas (as of 2026-05-15):**

| Schema ID | Purpose |
|---|---|
| `builtin:logmonitoring.log-storage-settings` | Log ingest routing rules |
| `builtin:ownership.teams` | Ownership teams (modern MZ replacement) |
| `builtin:ownership.config` | Ownership configuration |
| `builtin:attribute-allow-list` | Attribute ingestion allow list |
| `builtin:attribute-masking` | Sensitive attribute masking |
