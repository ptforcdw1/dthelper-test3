Build a new Monaco template (config.yaml + template.json + schema.json + template-help.md) for a Dynatrace Settings 2.0 schema, then register it in `template-index.md` and `template-param.md`. Follow every step in order.

---

## Step 1 — Ask the user what they want to configure

Ask in plain English: "What Dynatrace setting do you want a template for?" Accept a short free-form description (e.g. "alerting profile for high severity", "disk usage anomaly detection", "attribute masking for credit cards"). Do **not** ask for a schema ID — derive it in Step 2.

## Step 2 — Find candidate schemas

Read `DT_API_TOKEN` from the project root `.env`. Query `https://ylq89164.live.dynatrace.com/api/v2/settings/schemas` and filter the 298-ish items by the user's keywords against `schemaId` and `displayName` (case-insensitive substring match; split user input into terms and require at least one match per item).

Show the top **3** candidates to the user via AskUserQuestion, with `displayName` as the label and `schemaId` as the description. Add a 4th option "None of these — let me refine the search" that loops back to Step 1.

If zero candidates match, tell the user and loop back to Step 1.

## Step 3 — Fetch the chosen schema

`GET /api/v2/settings/schemas/<chosenSchemaId>` and hold the JSON in memory. Note the `version`, `displayName`, `description`, `maxObjects`, and `allowedScopes`.

## Step 4 — Walk the schema and classify properties

Recursively walk the schema's `properties` and `types` tree. For every **leaf** property (`type` is `text`, `integer`, `boolean`, or enum/`$ref` to an enum), collect:
- path (e.g. `name`, `executionSettings.delay`, `idContributors.serverName.value`)
- displayName
- description (truncate to ~120 chars)
- type
- default (from the schema if present)
- whether it has a `precondition` (skip these on first pass — they're conditional)
- whether it's `nullable: false` and has no default (likely required)

Classify each leaf into one of three buckets:

- **Recommended for parameterization** — `text` fields that look like names/titles/labels (path or displayName contains "name", "title", "id", "displayName"), OR required fields with no sensible default.
- **Optional** — other top-level fields with simple types.
- **Skip** — nested structural fields, fields gated by `precondition` on a value the user hasn't picked yet, fields whose entire purpose is internal plumbing (`enabled` flags, scope markers).

Cap the **Optional** bucket at 8 entries — pick the ones with the most user-friendly displayNames.

## Step 5 — Present parameters and get the user's selection

Use AskUserQuestion with `multiSelect: true` to show **Recommended ∪ Optional** parameters. Mark each recommended option's label with "(recommended)". Max 4 options per question — page if needed (groups of 3 + "More →" + "Done selecting").

If the user picks zero parameters, default to all recommended.

## Step 6 — Collect metadata for the template

Single AskUserQuestion call (up to 4 questions in one call):
- **Template name** (kebab-case, must not collide with existing folder under `templates/`)
- **One-line description** (used in `template-index.md`)
- **Config ID** (kebab-case, becomes the `id:` under `configs:` in `config.yaml`)
- **Default value for each chosen parameter** — present as a follow-up batch if more than 4

For defaults, suggest something sensible based on the parameter's `type` and `displayName`: e.g. for a `text` field named "title" suggest `"POC <displayName>"`; for an `integer` use the schema default if present.

## Step 6b — Confirm levelFlag and naming convention

This step is mandatory — do not skip even if the template "looks global".

**Ask the user (one AskUserQuestion with 2 questions):**

1. **`levelFlag`** — `app-specific` or `global`?
   - `app-specific`: the config targets a particular application/service. The Monaco `name:` will be prefixed with `[<AppName>-<Env>]` and `/new-task` will prompt for `appName` and `env` at task-creation time.
   - `global`: the config is tenant-wide and not tied to one app. No prefix.

2. **`nameTemplate`** — the descriptive part of the Monaco config name. Use `<paramName>` placeholders to interpolate parameter values.
   - For `app-specific`, the **full** name template will be `[<AppName>-<Env>] <your text>` — you provide everything after the prefix.
   - For `global`, you provide the full name template (no prefix).
   - Example for `app-specific` k8s log ingestion: user enters `k8s namespace logs - <namespace>` → full template becomes `[<AppName>-<Env>] k8s namespace logs - <namespace>`.
   - Suggest a default based on the template's purpose; let the user accept or edit.

Hold both `levelFlag` and the full `nameTemplate` in memory — they're used in Step 7 and Step 12.

## Step 7 — Generate `config.yaml`

For `app-specific` templates, add `appName` and `env` as the first two `parameters:` rows and use a templated `name:`:

```yaml
configs:
  - id: <configId>
    config:
      name: "[{{ .appName }}-{{ .env }}] <descriptiveNameWithMonacoPlaceholders>"
      template: template.json
      parameters:
        appName: "myapp"              # EDIT: application name (used in config name prefix)
        env: "prod"                   # EDIT: environment (used in config name prefix)
        <paramName1>: "<default1>"    # EDIT: <one-line purpose>
        <paramName2>: <default2>      # EDIT: <one-line purpose>
    type:
      settings:
        schema: <chosenSchemaId>
        scope: <first item from schema.allowedScopes — usually "environment">
```

For `global` templates, omit `appName`/`env` and use a plain `name:`:

```yaml
configs:
  - id: <configId>
    config:
      name: "<descriptiveNameWithMonacoPlaceholders>"
      template: template.json
      parameters:
        <paramName1>: "<default1>"    # EDIT: <one-line purpose>
        ...
```

Convert each `<paramName>` placeholder from the user-supplied `nameTemplate` to Monaco's `{{ .paramName }}` syntax in the `name:` field. Quote string defaults; leave numbers/booleans unquoted. The `# EDIT:` comment is the parameter's displayName from the schema.

## Step 8 — Generate `template.json`

Start with a minimum valid payload using the schema's defaults for every required field. Replace each user-chosen parameter's value with `{{ .paramName }}`. Use these rules:

- For `text` parameters: `"{{ .paramName }}"` (quoted)
- For `integer`/`boolean` parameters: `{{ .paramName }}` (unquoted)
- For required nested objects (like `idContributors` with multiple sub-contributors all required by a `custom-validator-ref` constraint): emit all the sub-objects with `enabled: false` or equivalent minimal-disabled state, only filling the ones the user parameterized
- For required arrays with `minObjects ≥ 1`: emit one item using schema defaults

If the schema has complex nested structures you can't confidently fill in, emit the minimum scaffolding and add a top-level JSON comment-style key like `"_TODO": "review nested X.Y.Z structure"` — the user will see it in Step 11.

## Step 9 — Save `schema.json`

Write the schema fetched in Step 3 (pretty-printed, depth ≥ 20) to `templates/<templateName>/schema.json`.

## Step 10 — Generate `template-help.md`

```markdown
# <templateName>

<one-line description from Step 6>

**Schema:** `<chosenSchemaId>` (version <version> at the time this template was generated)
**Scope:** <scope>
**Max objects per environment:** <maxObjects from schema, if defined>
**Level:** <levelFlag from Step 6b>
**Name template:** `<full nameTemplate from Step 6b>`

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `appName` | string | `myapp` | (app-specific only) Application name used in the `[<AppName>-<Env>]` config-name prefix. |
| `env` | string | `prod` | (app-specific only) Environment used in the prefix. |
| `<param1>` | <type> | `<default>` | <description from schema> |
| ... |

(omit the `appName` and `env` rows for `global` templates)

## Example deployment outcome

<2–3 sentences describing what the user will see in Dynatrace after deploy — derived from the schema's top-level description>

## Notes

- The non-parameterized fields in `template.json` use defaults from the schema. Edit `template.json` directly if you need to change them.
- Refresh the stored schema with `/refresh-schema` if Dynatrace updates the tenant.
- <Add any `_TODO` items emitted in Step 8 as bullet points here.>
```

## Step 11 — Show the generated files and ask for confirmation

Show file paths and contents (or summaries for the schema.json since it's large) to the user. Ask: "Files look right? Reply 'yes' to update `template-index.md` + `template-param.md` and finish."

If the user wants changes, make them and re-show.

## Step 12 — Update `template-index.md` and `template-param.md`

**Append to `template-index.md`** (one new section):

```markdown

## <templateName>
- **Level:** <levelFlag>
- **Name template:** `<full nameTemplate>`
- <one-line description from Step 6>
```

**Append to `template-param.md`** (one new section). For `app-specific` templates, do **not** include `appName`/`env` rows in this table — they are implicit and handled by `/new-task`:

```markdown

## <templateName>

| Parameter | Description | Default |
|---|---|---|
| `<param1>` | <short purpose> | `<default1>` |
| ... |
```

## Step 13 — Done

Tell the user:
- The template is ready under `templates/<templateName>/`
- They can now run `/new-task`, pick this template, fill parameters (plus `appName`/`env` if `app-specific`), and deploy via Jenkins
- Suggest committing: `git add templates/<templateName>/ template-index.md template-param.md && git commit && git push`

Do **not** auto-commit — the user should review the generated files first.
