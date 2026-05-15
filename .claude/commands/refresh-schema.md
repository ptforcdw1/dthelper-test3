Re-fetch the Dynatrace Settings 2.0 schema for a template and save it as `templates/<template>/schema.json`. Use when a Dynatrace tenant has been updated and stored schemas may be stale, or when adding schema reference material to a template that was created without it. Follow every step in order.

---

## Step 1 — List templates that have a Settings 2.0 schema

Use Glob to find all `templates/*/config.yaml` files. For each file, read it and look for a line matching `schema: <value>`. Skip templates that don't have one (e.g. `get-alerts` uses `task_type: download` instead). Build a list of `{ templateName, schemaId, hasStoredSchema }` where `hasStoredSchema` is true if `templates/<name>/schema.json` already exists.

## Step 2 — Ask the user which template to refresh

Use AskUserQuestion. Max 4 options per question — page in groups of 3 with "More →" as the 4th slot if more remain (same pattern as `/new-task`). For each option, show the template name as the label and the schemaId + current stored version (if stored) as the description, e.g. `builtin:ownership.teams (stored v1.0.6)` or `builtin:ownership.teams (not yet stored)`.

You can also accept "All templates" as a final option if the user wants to refresh every schema in one shot.

## Step 3 — Read the API token

Read `DT_API_TOKEN` from the project's `.env` file (root). If `.env` doesn't exist or doesn't contain the token, tell the user to create it from `.env.example` and stop.

## Step 4 — Fetch and save

For each template to refresh, call:
```
GET https://ylq89164.live.dynatrace.com/api/v2/settings/schemas/<schemaId>
Authorization: Api-Token <token>
```

Save the JSON response (pretty-printed, depth ≥ 20) to `templates/<templateName>/schema.json`.

## Step 5 — Report what changed

For each template, compare the new schema's `version` to the previous (if any) and report:
- `unchanged`: same version as before
- `updated`: version differs (show old → new)
- `new`: no previous file existed

Show as a table. Don't commit automatically — let the user review the diff first.
