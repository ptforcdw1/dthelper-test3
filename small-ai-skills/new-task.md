# Skill: Generate a new Monaco task (chat output only)

You are helping a human create a Monaco task. You will read template files from this repo, ask the human for parameter values, then **print** the final `config.yaml` and `template.json` to the chat. The human will copy them manually.

---

## HARD RULES — read these first, never break them

1. **DO NOT write any file to disk.** No file-create, no file-edit.
2. **DO NOT run any git command** (`git add`, `git commit`, `git push`, etc.).
3. **DO NOT touch `task-index.txt`.**
4. **DO NOT change `template.json`** — copy it byte-for-byte into the chat output.
5. **DO NOT change the `name:` field in `config.yaml`** — it has `{{ .paramName }}` placeholders that Monaco resolves later.
6. **DO NOT touch `scope:`** — if you see a value like `RESOLVE_FROM_SERVICE` or `environment`, leave it.
7. **DO NOT invent parameter values.** If the human skips a parameter, leave the template default.
8. **DO NOT pick the task ID.** The human picks the folder name themselves.
9. Output the two files inside fenced code blocks in chat, nothing else fancy.

---

## Where the templates live (fetch over HTTP, do NOT clone)

All templates are in a public GitHub repo. **Fetch them as raw files over HTTP.** Do not assume you can read local files — use your HTTP/web-fetch tool.

Base URL (always the `main` branch):

```
https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/
```

The exact four URLs you will fetch:

| Purpose                | URL                                                                                          |
|------------------------|----------------------------------------------------------------------------------------------|
| Template index         | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/template-index.md`           |
| Param schema (per tpl) | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/<TPL>/request-schema.json` |
| Config (per tpl)       | `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/<TPL>/config.yaml` |
| Template body (per tpl)| `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/<TPL>/template.json` |

Replace `<TPL>` with the template name the human chose in Step 1 (e.g. `log-ingest-k8s-namespace`).

URLs you must **NOT** fetch (large or irrelevant — they will confuse you):
- `.../templates/<TPL>/schema.json` (huge Dynatrace Settings 2.0 schema)
- `.../templates/<TPL>/template-help.md`
- `.../template-param.md` (legacy fallback — assume `request-schema.json` always exists)

If a fetch returns 404, tell the human the URL that failed and stop. Do not guess a different URL.

---

## Step-by-step procedure

### Step 1 — List the templates

**Fetch** `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/template-index.md`. It is structured like this:

```
## anomaly-service-failure-fix
- **Level:** app-specific
- **Name template:** `[<AppName>-<Env>] <serviceName> failure rate fixed`
- Service failure rate anomaly detection — fixed-threshold alerts.

## log-ingest-k8s-namespace
- **Level:** app-specific
- **Name template:** `[<AppName>-<Env>] log ingest - <namespaceName> namespace`
- Log ingest rule that stores logs from a specific Kubernetes namespace.
```

For every `## <name>` heading, print **one bullet** in chat:

```
- <name> — <the last bullet, which is the 1-line description>
```

Then ask the human: **"Which template do you want to use?"** and wait for their reply.

Match their reply case-insensitively against the template names. If it doesn't match exactly one, ask again.

---

### Step 2 — Fetch the parameter schema

**Fetch** `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/<chosen-template>/request-schema.json`. It looks like:

```json
{
  "params": {
    "appName":        { "required": true,  "prompt": "Which application?" },
    "env":            { "required": true,  "enum": ["prod","staging","dev"], "prompt": "Which environment?" },
    "namespaceName":  { "required": true,  "prompt": "Which k8s namespace?" },
    "ruleTitle":      { "suggested": true, "default": "Ingest logs from k8s namespace", "prompt": "Rule title?" }
  }
}
```

Build a list of params to ask, using this rule:

| Flag in schema       | Do you ask?               | If the human leaves it blank        |
|----------------------|---------------------------|-------------------------------------|
| `required: true`     | YES                       | Re-ask. Blank is not allowed.       |
| `suggested: true`    | YES (show the default)    | Use the default. Do not edit line.  |
| neither              | NO — skip the param.      | (n/a)                               |

---

### Step 3 — Ask the human, one parameter at a time

For each param in the list, print exactly this format and wait for a reply:

```
Parameter: <param name>
Question:  <the "prompt" field from the schema>
Default:   <the "default" field, or "(no default — required)">
Allowed:   <comma-separated "enum" values, or "any string">
Your answer:
```

Rules:
- If the schema has `enum`, the human's answer MUST be one of those values. Otherwise re-ask.
- Required + blank reply → re-ask.
- Suggested + blank reply → record "skip" (you will leave the template default in place).

---

### Step 4 — Fetch and edit the config

**Fetch** `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/<chosen-template>/config.yaml`. Lines that hold parameter values look like:

```
        appName: "myapp"                          # EDIT: application name
```

Pattern to match:
- Some leading spaces (keep them)
- `<paramName>:` (keep it)
- A quoted value `"..."` (THIS is what you replace)
- Optional whitespace
- The comment `# EDIT: ...` (keep it)

For each parameter where the human gave a value:
- Replace the quoted value with the human's value, still wrapped in double quotes.
- Keep everything else on the line as it was.

For parameters the human skipped (or that you never asked): **do not touch that line.**

Lines without `# EDIT:` are off-limits — copy them as-is. In particular:
- The `name: "..."` line (with `{{ .paramName }}` placeholders).
- The `scope:` line.
- Indentation, blank lines, comments.

---

### Step 5 — Fetch the template body

**Fetch** `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/<chosen-template>/template.json`. Do **nothing** to it. You will paste it verbatim in Step 6.

---

### Step 6 — Print the output to chat

Print this exact structure (no extra prose before or after):

````markdown
Here are your two files. Copy each into a new folder `tasks/<your-task-id>/` of your repo.

**`config.yaml`**
```yaml
<the edited config.yaml content>
```

**`template.json`**
```json
<the verbatim template.json content>
```

Pick a `<your-task-id>` like `task011`, `task012`, … — any name not already under `tasks/`. Do not commit `task-index.txt`; that file is managed by a different workflow.
````

You are done. Do not offer to do anything else.

---

## Worked example (study this carefully)

**Human runs the skill. You start at Step 1.**

You fetch `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/template-index.md` and print:

```
Available templates:
- anomaly-service-failure-fix — Service failure rate anomaly detection.
- log-ingest-k8s-namespace — Log ingest rule for a specific k8s namespace.

Which template do you want to use?
```

**Human replies:** `log-ingest-k8s-namespace`

**Step 2.** You fetch `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/log-ingest-k8s-namespace/request-schema.json`.
You see 4 params: `appName` (required), `env` (required, enum), `namespaceName` (required), `ruleTitle` (suggested).

**Step 3.** You ask one by one:

```
Parameter: appName
Question:  Which application is this log ingest rule for?
Default:   (no default — required)
Allowed:   any string
Your answer:
```

**Human:** `testapp`

You continue with `env`, `namespaceName`, `ruleTitle`. Suppose the human answers:
- `env` → `dev`
- `namespaceName` → `mytest-logingest-ns`
- `ruleTitle` → (blank — they want the default)

**Step 4.** You fetch `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/log-ingest-k8s-namespace/config.yaml`:

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

You edit lines that have a value from the human. `ruleTitle` was skipped → leave it alone. `name:`, `scope:`, indentation → untouched.

**Step 5.** You fetch `https://raw.githubusercontent.com/ptforcdw1/dthelper-test3/main/templates/log-ingest-k8s-namespace/template.json`. Keep it exactly as-is.

**Step 6.** You print this to chat and stop:

````markdown
Here are your two files. Copy each into a new folder `tasks/<your-task-id>/` of your repo.

**`config.yaml`**
```yaml
configs:
  - id: log-ingest-k8s-namespace
    config:
      name: "[{{ .appName }}-{{ .env }}] log ingest - {{ .namespaceName }} namespace"
      template: template.json
      parameters:
        appName: "testapp"                        # EDIT: application name (used in config name prefix)
        env: "dev"                                # EDIT: environment (used in config name prefix)
        namespaceName: "mytest-logingest-ns"      # EDIT: Kubernetes namespace name to match (writes to matchers[0].values[0])
        ruleTitle: "Ingest logs from k8s namespace"  # EDIT: rule title shown in Dynatrace UI (config-item-title)
    type:
      settings:
        schema: builtin:logmonitoring.log-storage-settings
        scope: environment
```

**`template.json`**
```json
<<< paste the exact bytes you fetched from the template.json URL here >>>
```

Pick a `<your-task-id>` like `task011`, `task012`, … — any name not already under `tasks/`. Do not commit `task-index.txt`; that file is managed by a different workflow.
````

---

## Self-check before you send the output

- [ ] Did you change any line in `config.yaml` that did NOT have `# EDIT:`? → If yes, undo it.
- [ ] Did you modify `template.json` in any way? → If yes, re-fetch it from the URL.
- [ ] Did you keep the `{{ .paramName }}` placeholders inside the `name:` field? → They must stay.
- [ ] Did you write any file or run any git command? → You must not. Output is chat-only.
- [ ] For each `required` param, did the human give a non-blank value? → If not, go back and re-ask.

If all checks pass, you are done.