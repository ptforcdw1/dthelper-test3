# Skill: Create a new Monaco v2 template (chat output only)

You are helping a human build a **new template** for the `dthelper-test3` repo. You will ask the human questions, ask them to run a couple of `curl` commands for you (because **you cannot run commands on their computer**), and then print the contents of 5 files to the chat. The human copies them into `templates/<new-template-name>/` manually.

---

## HARD RULES — read first, never break

1. **DO NOT write any file to disk.** No file-create, no file-edit.
2. **DO NOT run any shell, git, or HTTP command on the human's computer.** If you need something run, **tell the human the exact command** and wait for them to paste the output back.
3. **DO NOT touch git.** No `git add`, `git commit`, `git push`.
4. **DO NOT invent a Dynatrace schema.** The schema must come from a real `GET /api/v2/settings/schemas/<id>` response the human pastes to you.
5. **ALWAYS use Monaco v2 syntax** — `configs[].config.template` + `configs[].type.settings.schema`. Never Monaco v1.
6. **ALWAYS produce all 5 files** for the template (listed below). If you can only produce 4, stop and tell the human what's blocking you.
7. Output ONLY in chat, inside fenced code blocks. The human copies and pastes.

---

## The standard template — 5 files, NO exceptions

Every template directory under `templates/<name>/` must contain exactly these 5 files:

| File                  | Purpose                                                                    |
|-----------------------|----------------------------------------------------------------------------|
| `config.yaml`         | Monaco v2 config: id, name, parameters, schema, scope. Uses `# EDIT:` lines. |
| `template.json`       | Monaco template body with `{{ .paramName }}` placeholders for parameters.   |
| `request-schema.json` | Input contract for `/new-task`: which params to ask, prompts, defaults, required flags. |
| `schema.json`         | Verbatim Dynatrace Settings 2.0 schema (the JSON returned by the API).      |
| `template-help.md`    | Human documentation: schema id, level, name template, parameter table, notes. |

If the human is missing any of these later, the deploy pipeline will fail.

---

## URLs you may fetch (read-only, GitHub raw)

You need these to check for name collisions and to see real examples:

| Purpose                       | URL                                                                                       |
|-------------------------------|-------------------------------------------------------------------------------------------|
| Existing template index       | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/template-index.md`        |
| Example: config.yaml          | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/log-ingest-k8s-namespace/config.yaml` |
| Example: template.json        | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/log-ingest-k8s-namespace/template.json` |
| Example: request-schema.json  | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/log-ingest-k8s-namespace/request-schema.json` |
| Example: template-help.md     | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/log-ingest-k8s-namespace/template-help.md` |

If you do not have an HTTP fetch tool, tell the human to paste these files; do **not** make up their contents.

---

## Step-by-step procedure

### Step 1 — Ask what the human wants to template

Ask, in plain English:

> "What Dynatrace setting do you want a template for? (Examples: 'alerting profile for high severity', 'disk usage anomaly detection', 'k8s namespace log ingest'.)"

Wait for a free-text reply. Keep their phrasing — you'll use it as keywords in Step 2.

### Step 2 — Have the human list candidate schemas

You cannot call the Dynatrace API. Tell the human to run this on their machine and paste the output:

````
Please run the following on your machine and paste the JSON output back to me.

```
curl -s -H "Authorization: Api-Token $DT_API_TOKEN" \
  "https://<YOUR-TENANT>.live.dynatrace.com/api/v2/settings/schemas"
```

Replace `<YOUR-TENANT>` with your Dynatrace tenant id (e.g. `ylq89164`). The token is in the `.env` file at the root of your `dthelper-test3` clone.

The response is a JSON object with an `items[]` array. Each item has `schemaId`, `displayName`, and `latestSchemaVersion`. The full list is long (~300 items) — paste the whole thing or use `jq` to pre-filter:

```
curl -s -H "Authorization: Api-Token $DT_API_TOKEN" \
  "https://<YOUR-TENANT>.live.dynatrace.com/api/v2/settings/schemas" \
  | jq '.items[] | select((.schemaId + " " + .displayName) | test("<KEYWORD>"; "i"))'
```

Replace `<KEYWORD>` with one of the words from your description (e.g. `log`, `anomaly`, `tagging`).
````

Wait for the paste.

### Step 3 — Show the human the top 3 candidates

From their paste, pick the **3** items whose `schemaId` or `displayName` best matches the human's Step 1 keywords (case-insensitive substring match — at least one keyword present).

Print them as a numbered list:

```
Candidate schemas:
1. <displayName>  (schemaId: <schemaId>)
2. <displayName>  (schemaId: <schemaId>)
3. <displayName>  (schemaId: <schemaId>)
4. None of these — go back

Which one (1-4)?
```

If the human picks 4, go back to Step 1.
If zero items matched their keywords, tell them and go back to Step 2 with a wider keyword.

### Step 4 — Have the human fetch the full schema

Tell the human:

````
Please run this and paste the JSON output back. This will be saved as `schema.json` in the new template directory.

```
curl -s -H "Authorization: Api-Token $DT_API_TOKEN" \
  "https://<YOUR-TENANT>.live.dynatrace.com/api/v2/settings/schemas/<chosen-schemaId>" \
  | jq .
```
````

Wait for the paste. From this JSON, extract and remember:
- `schemaId`
- `version` (or `latestSchemaVersion`)
- `displayName`
- `description`
- `maxObjects` (if present)
- `allowedScopes[]` — use the **first** entry as the default scope (usually `"environment"`)
- `properties` and `types` — for Step 5

### Step 5 — Identify parameterizable fields

Walk the schema's `properties` (and any `types` referenced from there) and find every **leaf** field — a property whose `type` is one of: `text`, `integer`, `boolean`, `enum`, or a `$ref` to a simple enum type.

Sort each leaf into one of three buckets:

| Bucket                 | Rule                                                                                                     |
|------------------------|----------------------------------------------------------------------------------------------------------|
| **Recommended**        | `text` fields whose name/displayName contains `name`, `title`, `id`, `displayName` — OR fields with `nullable: false` and no `default`. |
| **Optional**           | Other simple-type top-level fields. Cap at **8** of these (keep the ones with friendliest displayNames). |
| **Skip**               | Nested structural fields, anything with a `precondition`, internal plumbing (e.g. `enabled` flags, scope markers). |

Print the lists to the human:

```
Recommended params to expose (good candidates):
- <fieldPath>  (<displayName>) — <type>

Optional params (also exposable):
- <fieldPath>  (<displayName>) — <type>

Skipped (internal / nested / preconditioned):
- <fieldPath>
- ...

Which fields do you want to expose as parameters? Reply with a comma-separated list of paths.
If you reply blank, I'll use all Recommended fields.
```

Wait for their reply. Validate every path against the bucketed lists — if any path is unknown, re-ask.

### Step 6 — Collect template metadata

Ask the human **four** questions in one turn:

```
1) Template name (kebab-case, no spaces, e.g. "log-ingest-k8s-namespace"):
   - Must not collide with an existing template under `templates/`.
   - (Tip: I'll check the index for you if you ask.)

2) One-line description (used in template-index.md and template-help.md):

3) Config ID (kebab-case — becomes the `id:` under `configs:` in config.yaml.
   Usually the same as the template name):

4) Level — app-specific or global?
   - app-specific: the config targets one application/service. Monaco `name:` will be
     prefixed with `[<AppName>-<Env>]`. /new-task will always prompt for appName + env.
   - global: tenant-wide, no prefix.
```

After they answer, ask **one more question** (because it depends on the level):

```
5) Name template — the descriptive part of the Monaco config name.
   Use <paramName> placeholders to interpolate parameter values.
   - For app-specific: full name will be "[<AppName>-<Env>] <your text>"
     Example: "<serviceName> response time fixed"
   - For global: full name is exactly what you type
     Example: "POC <ruleName>"
```

Finally, for each parameter the human chose in Step 5 (plus the implicit `appName` and `env` for app-specific templates), ask for:
- A **default value** (or "(no default — required)" for things like `appName`, `env`, `namespaceName`)
- A **friendly prompt** (the question /new-task will show the operator) — propose one based on the schema's `displayName` + `description`, let the human edit.

Mark each parameter with one of:
- `required: true` — operator MUST provide a value (no default)
- `suggested: true` — operator is asked, default is shown, they can skip
- (neither) — fully optional, /new-task won't ask

Also note: `appName` and `env` are **always `required: true`** for app-specific templates.

### Step 7 — Check the template name doesn't collide

Fetch `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/template-index.md` (or ask the human to paste it). For every `## <name>` heading, compare to the new template name. If there's a collision, tell the human and loop back to Step 6's question 1.

### Step 8 — Generate `config.yaml`

**For app-specific templates:**

```yaml
configs:
  - id: <configId>
    config:
      name: "[{{ .appName }}-{{ .env }}] <descriptive name with {{ .paramName }} placeholders>"
      template: template.json
      parameters:
        appName: "myapp"                   # EDIT: application name (used in config name prefix)
        env: "prod"                        # EDIT: environment (used in config name prefix)
        <paramName1>: "<default1>"         # EDIT: <one-line purpose from schema displayName>
        <paramName2>: <default2>           # EDIT: <one-line purpose>
    type:
      settings:
        schema: <chosenSchemaId>
        scope: <first allowedScope, usually "environment">
```

**For global templates** (no `appName`/`env`):

```yaml
configs:
  - id: <configId>
    config:
      name: "<descriptive name with {{ .paramName }} placeholders>"
      template: template.json
      parameters:
        <paramName1>: "<default1>"         # EDIT: <one-line purpose>
        ...
    type:
      settings:
        schema: <chosenSchemaId>
        scope: <first allowedScope>
```

Rules:
- Quote **string** defaults, leave **integer/boolean** unquoted.
- Convert `<paramName>` in the human's Step 6 "name template" to Monaco's `{{ .paramName }}` syntax in the `name:` field.
- The `# EDIT:` comment text is the parameter's `displayName` from the Dynatrace schema (or a short purpose if you have a better phrasing).
- **DO NOT** invent a `scope:` — use the schema's first `allowedScopes` entry. If the human wants a narrower scope (e.g. a specific service or host group), they can edit `config.yaml` later.

### Step 9 — Generate `template.json`

Start from a **minimum valid payload** that the chosen schema accepts:
- For every required leaf field, include it.
- For optional fields the human did NOT parameterize, use the schema's default if present; otherwise omit.
- For every parameter the human chose, replace its value with a Monaco placeholder:
  - String type → `"{{ .paramName }}"`  (quoted in JSON)
  - Integer / boolean → `{{ .paramName }}`  (unquoted — Monaco substitutes the raw value)
- For required nested objects: emit the minimum structure the schema needs (use `enabled: false` or equivalent for sub-blocks the human didn't parameterize).
- For required arrays with `minObjects ≥ 1`: emit one item with schema defaults.

If a nested structure is too complex to fill confidently, emit it with a top-level marker key like `"_TODO": "review nested X.Y.Z structure"` and call out the TODO in your chat output. Do not pretend the file is complete.

### Step 10 — Generate `request-schema.json`

This is the input contract `/new-task` reads to know what to ask the operator. Format:

```json
{
    "_comment": "ITSM input contract. resolve.py and /new-task both read this. Distinct from schema.json (Dynatrace Settings 2.0 schema).",
    "params": {
        "appName": {
            "type": "string",
            "required": true,
            "prompt": "Which application? (used in the config name prefix)",
            "description": "Application name."
        },
        "env": {
            "type": "string",
            "required": true,
            "enum": ["prod", "staging", "dev"],
            "prompt": "Which environment? (prod / staging / dev)",
            "description": "Environment label used in the config name prefix."
        },
        "<paramName>": {
            "type": "<string|integer|boolean>",
            "required": <true|false>,
            "suggested": <true|false — only if not required>,
            "default": <the default value, omit if required and no default>,
            "enum": [<...>],
            "prompt": "<friendly question from Step 6>",
            "description": "<one-line description; can quote the schema description>"
        }
    }
}
```

Rules:
- Include `appName` and `env` at the top of `params` for **app-specific** templates only. Omit them for **global**.
- Order params: required first, then suggested, then fully optional.
- `required` and `suggested` are **mutually exclusive**. A param has at most one of them set to `true`.
- Always include `prompt` — `/new-task` shows this to the operator.
- Always include `description` — used as fallback documentation.

### Step 11 — Generate `template-help.md`

```markdown
# <templateName>

<one-line description from Step 6>

**Schema:** `<chosenSchemaId>` (version <version> at the time this template was generated)
**Scope:** `<scope>` <one-line note about what other scopes the schema allows, if interesting>
**Max objects per environment:** <maxObjects, or "unlimited" if not in schema>
**Level:** <app-specific | global>
**Name template:** `<full name template, including the [<AppName>-<Env>] prefix for app-specific>`

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `appName` | string | `myapp` | (app-specific only) Application name used in the `[<AppName>-<Env>]` config-name prefix. |
| `env` | string | `prod` | (app-specific only) Environment used in the prefix. |
| `<param1>` | <type> | `<default>` | <description, can quote schema> |
| ... |

(Omit `appName` and `env` rows for global templates.)

## Example deployment outcome

<2–3 sentences describing what the operator will see in Dynatrace after deploy. Derive from the schema's top-level `description`.>

## Notes

- The non-parameterized fields in `template.json` use defaults from the schema. Edit `template.json` directly if you need to change them.
- <List any hardcoded values worth flagging — e.g. `enabled: true`, single-matcher assumptions, etc.>
- <If you emitted any `_TODO` markers in Step 9, list them here as bullets.>
- Refresh the stored schema with `/refresh-schema <templateName>` if Dynatrace updates the schema version.
```

### Step 12 — `schema.json` — DO NOT re-print

`schema.json` is the **verbatim JSON** the human pasted in Step 4. Schemas are typically 20–100 KB — re-printing them into chat is wasteful.

Instead, say:

```
schema.json: save the EXACT JSON you pasted in Step 4 as `templates/<templateName>/schema.json`. Do not edit it. (I'm not re-printing it here because it's large.)
```

### Step 13 — Print all output to chat

Print in this order, with section headings:

````markdown
Here is your new template. Create the directory `templates/<templateName>/` in your repo and save these 5 files inside it.

### 1. `config.yaml`
```yaml
<generated config.yaml>
```

### 2. `template.json`
```json
<generated template.json>
```

### 3. `request-schema.json`
```json
<generated request-schema.json>
```

### 4. `template-help.md`
```markdown
<generated template-help.md>
```

### 5. `schema.json`
Save the exact JSON you pasted in Step 4 as this file. Do not edit it.

---

### Register the template in the index

Open `template-index.md` (root of the repo) and **append** this section at the end:

```markdown

## <templateName>
- **Level:** <level>
- **Name template:** `<full name template>`
- <one-line description>
```

### Manual commit (run on your machine)

```
git add templates/<templateName>/ template-index.md
git commit -m "Add <templateName> template"
git push origin main
```

Then use `/new-task` to create a task from this new template.
````

If you emitted any `_TODO` markers, repeat them in a final "Things to review" bullet list before signing off.

---

## Self-check before you send the output

- [ ] All 5 files present? (config.yaml, template.json, request-schema.json, schema.json instruction, template-help.md)
- [ ] config.yaml uses Monaco v2 (`type.settings.schema`, not v1's flat layout)?
- [ ] For app-specific: `appName` + `env` in both `config.yaml` parameters AND `request-schema.json` params?
- [ ] For app-specific: `name:` starts with `[{{ .appName }}-{{ .env }}]`?
- [ ] Every `{{ .paramName }}` in `template.json` has a matching entry in `config.yaml`'s `parameters:` block?
- [ ] Every `{{ .paramName }}` in `template.json` has a matching entry in `request-schema.json`?
- [ ] `scope:` came from the schema's `allowedScopes`, not invented?
- [ ] You did NOT run any command? You did NOT write any file? You did NOT touch git?
- [ ] You showed the human the exact `git add / commit / push` commands instead of running them?

If any check fails, fix before sending.

---

## Reference: a complete real template

This is the existing `log-ingest-k8s-namespace` template. Use it as your **shape template** — your output must look like this in structure (different field names and values, of course).

**`templates/log-ingest-k8s-namespace/config.yaml`**
```yaml
configs:
  - id: log-ingest-k8s-namespace
    config:
      name: "[{{ .appName }}-{{ .env }}] log ingest - {{ .namespaceName }} namespace"
      template: template.json
      parameters:
        appName: "myapp"                          # EDIT: application name (used in config name prefix)
        env: "prod"                               # EDIT: environment (used in config name prefix)
        namespaceName: "my-namespace"             # EDIT: Kubernetes namespace name to match (writes to matchers[0].values[0])
        ruleTitle: "Ingest logs from k8s namespace"  # EDIT: rule title shown in Dynatrace UI (config-item-title)
    type:
      settings:
        schema: builtin:logmonitoring.log-storage-settings
        scope: environment
```

**`templates/log-ingest-k8s-namespace/template.json`**
```json
{
  "enabled": true,
  "config-item-title": "{{ .ruleTitle }}",
  "send-to-storage": true,
  "matchers": [
    {
      "attribute": "k8s.namespace.name",
      "operator": "MATCHES",
      "values": ["{{ .namespaceName }}"]
    }
  ]
}
```

**`templates/log-ingest-k8s-namespace/request-schema.json`**
```json
{
    "_comment": "ITSM input contract. resolve.py and /new-task both read this. Distinct from schema.json (Dynatrace Settings 2.0 schema).",
    "params": {
        "appName": {
            "type": "string",
            "required": true,
            "prompt": "Which application is this log ingest rule for? (used in the config name prefix)",
            "description": "Application name."
        },
        "env": {
            "type": "string",
            "required": true,
            "enum": ["prod", "staging", "dev"],
            "prompt": "Which environment? (prod / staging / dev)",
            "description": "Environment label used in the config name prefix."
        },
        "namespaceName": {
            "type": "string",
            "required": true,
            "prompt": "Which Kubernetes namespace should this rule match?",
            "description": "Kubernetes namespace to match. Written as matchers[0].values[0]."
        },
        "ruleTitle": {
            "type": "string",
            "default": "Ingest logs from k8s namespace",
            "suggested": true,
            "prompt": "Rule name shown in the Dynatrace UI?",
            "description": "Rule name displayed in Dynatrace (written into config-item-title)."
        }
    }
}
```

Notice in the example above:
- `appName` and `env` appear in BOTH `config.yaml` (with placeholder defaults `"myapp"` / `"prod"`) AND `request-schema.json` (as `required: true`).
- `namespaceName` is required (no default in `request-schema.json`, just a placeholder in `config.yaml`).
- `ruleTitle` is suggested (has a `default` and `suggested: true`).
- The `name:` in `config.yaml` uses Monaco `{{ .paramName }}` substitution, not the `<paramName>` syntax that `template-index.md` documents.

That is the shape every new template must follow.