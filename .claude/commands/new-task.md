Create a new Monaco task from a template and commit it to git. Follow every step below in order without skipping.

---

## Step 1 — Read the template index

Read `template-index.md`. For every `## <name>` heading, parse the section into a metadata record:
- `name` (the heading text)
- `level` — `app-specific` or `global` (from the `- **Level:** ...` line)
- `nameTemplate` — the backtick-quoted string on the `- **Name template:** ...` line (only present for some templates)
- `description` — the remaining bullet (the one-line summary)

**Do not** read `template-param.md` yet — parameters are loaded in Step 5 only for the chosen template.

## Step 2 — Ask the user which task type to create

List every template as plain text in chat — one bullet per template, using the template's description line. Do **not** use AskUserQuestion. Ask: "Which task template do you want to use?" and wait for the user's free-text reply.

Match the user's reply against template names case-insensitively. If the reply is ambiguous or doesn't match any template, ask again. Do not proceed until you have a single concrete template name.

## Step 3 — Generate the next taskID

Read `task-index.txt` (each line is `<taskID>:<template>:<created-datetime>`). Take the last line, parse the `taskNNN` value at the start, increment by 1, and zero-pad to 3 digits (e.g. last line starts with `task010` → new is `task011`). If the file is missing or empty, start at `task001`.

Do **not** list `tasks/` to determine the next ID — `task-index.txt` is the source of truth.

Show the user the generated taskID before proceeding.

## Step 4 — Create the task directory and copy template files

Use PowerShell to:
1. Create the directory `tasks/<taskID>/`
2. Copy `templates/<chosen-template>/config.yaml` to `tasks/<taskID>/config.yaml`
3. Copy `templates/<chosen-template>/template.json` to `tasks/<taskID>/template.json`

## Step 5 — Load parameter definitions

**Prefer `request-schema.json` if it exists** — it is the canonical source for prompts and required/suggested flags. Check for `templates/<chosen-template>/request-schema.json`:

- **If present**: read it. For each entry under `"params"`, capture: `name`, `prompt` (friendly question to ask), `description`, `default`, `required` (bool), `suggested` (bool), `enum` (if present), `min`/`max` (if present).
- **If absent**: fall back to parsing `template-param.md`. Find the `## <chosen-template>` section and parse its table rows (columns: Parameter, Description, Default). Treat all such params as "ask the user" (no required/suggested distinction).

Implicit params for `app-specific` templates (`appName`, `env`) are handled in Step 6 if not already in the schema.

## Step 6 — Ask the user for each parameter value

Build the list of parameters to ask about:

- **Always ask** for params flagged `required: true`. The user MUST provide a value — re-ask if they leave it blank.
- **Always ask** for params flagged `suggested: true`. Show the default. The user may skip (leave blank) to accept the default.
- **Do not ask** for params with neither flag (fully optional — the template default stays in place).
- For templates falling back to `template-param.md`, treat every row as `suggested`.

For each parameter, use the **`prompt` field from `request-schema.json` as the question**. This is human-friendly wording (e.g. "Which Dynatrace service do you want to monitor?") rather than the raw param name. Always include the default value in the prompt or option description. If the schema only has a `description` field (no `prompt`), use the description.

Ask all parameters in a single AskUserQuestion call where possible (up to 4 at a time). If there are more than 4, ask in batches.

**Additionally, if the chosen template's `level` is `app-specific` and the schema does not already include `appName` / `env`**, ask the user for those two as implicit values in the same flow:
- `appName` — application name for the `[<AppName>-<Env>]` config-name prefix (no default — user must provide)
- `env` — environment (e.g. `prod`, `staging`, `dev`) for the same prefix

Skip these two if `level` is `global` or if the schema already declares them.

## Step 7 — Update config.yaml with the provided values

For each parameter where the **user provided a non-empty value**, use Edit to replace the default value in `tasks/<taskID>/config.yaml` with the user's value. Preserve the `# EDIT:` comment on the line.

**If the user skipped a `suggested` parameter (left it blank), do NOT touch that line in config.yaml.** Leave the template's default in place — never substitute a different value of your own. The same applies to fully optional params (neither required nor suggested): they stay untouched.

The `scope:` field is **not** asked or set here — it is resolved at deploy time by `scripts/resolve.py` based on `serviceName`. Leave any `RESOLVE_FROM_*` sentinel value untouched.

For `app-specific` templates, also set the `appName` and `env` parameter values in `config.yaml`.

Show the user the final state of config.yaml so they can confirm. The `name:` field in `config.yaml` should contain the templated string (e.g. `"[{{ .appName }}-{{ .env }}] {{ .serviceName }} ..."`) — do **not** pre-resolve it; Monaco resolves it at deploy time.

## Step 8 — Append to task-index.txt

Append a single line to `task-index.txt` in the format:

```
<taskID>:<chosen-template>:<ISO-8601 datetime>
```

Use the current local datetime in ISO 8601 with timezone offset (e.g. `2026-05-17T14:32:10+07:00`).

**Important — guard against a missing trailing newline.** `PowerShell`'s `Add-Content` does not insert a leading newline, so if the previous last line lacks one, the new entry gets concatenated onto it. Use this PowerShell snippet (or equivalent logic) so the result is robust either way:

```powershell
$ts = (Get-Date).ToString("yyyy-MM-ddTHH:mm:sszzz")
$line = "<taskID>:<chosen-template>:$ts"
$path = "task-index.txt"
# Read raw bytes to detect a trailing newline without stripping
$needsLeadingNewline = $false
if (Test-Path $path) {
    $raw = [System.IO.File]::ReadAllText($path)
    if ($raw.Length -gt 0 -and -not ($raw.EndsWith("`n") -or $raw.EndsWith("`r`n"))) {
        $needsLeadingNewline = $true
    }
}
$toAppend = if ($needsLeadingNewline) { "`n$line`n" } else { "$line`n" }
[System.IO.File]::AppendAllText($path, $toAppend)
```

After appending, verify the new line is on its own line (e.g. `Get-Content task-index.txt | Select-Object -Last 1` should equal the new entry exactly).

## Step 9 — Commit to git

Run these commands:
```
git add tasks/<taskID>/ task-index.txt
git commit -m "Add <taskID>: <chosen-template> task"
git push origin main
```

## Step 10 — Advise the user

Tell the user:
- Their taskID
- To go to Jenkins → Build with Parameters
- Set TASK_ID = `<taskID>`
- Set TARGET_ENVIRONMENT = `ylq89164` (or change if needed)
- Leave SKIP_DEPLOY unchecked for a real deploy, or check it for dry-run only
- Click Build
- The `Resolve Names to IDs` stage will look up `serviceName` against Dynatrace and fill in the `scope:` field automatically
