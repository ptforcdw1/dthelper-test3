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

Use PowerShell to list all subdirectories under `tasks/` whose names match the pattern `task` followed by digits (e.g. `task001`, `task002`). Find the highest number. The new taskID is that number + 1, zero-padded to 3 digits (e.g. if highest is `task002`, new is `task003`). If no matching directories exist, start at `task001`.

Show the user the generated taskID before proceeding.

## Step 4 — Create the task directory and copy template files

Use PowerShell to:
1. Create the directory `tasks/<taskID>/`
2. Copy `templates/<chosen-template>/config.yaml` to `tasks/<taskID>/config.yaml`
3. Copy `templates/<chosen-template>/template.json` to `tasks/<taskID>/template.json`

## Step 5 — Load parameter definitions

Read `template-param.md`. Find the `## <chosen-template>` section and parse its table rows (columns: Parameter, Description, Default).

`appName` and `env` are **not** in `template-param.md` for `app-specific` templates — they are implicit and handled in Step 6.

## Step 6 — Ask the user for each parameter value

For each parameter from Step 5, ask the user for a value. Show:
- The parameter name
- What it controls (the Description column)
- The current default value

Ask all parameters in a single AskUserQuestion call where possible (up to 4 at a time). If there are more than 4, ask in batches.

**Additionally, if the chosen template's `level` is `app-specific`**, ask the user for two extra implicit values in the same flow:
- `appName` — application name for the `[<AppName>-<Env>]` config-name prefix (no default — user must provide)
- `env` — environment (e.g. `prod`, `staging`, `dev`) for the same prefix

Skip these two if `level` is `global`.

## Step 7 — Update config.yaml with the provided values

Use Edit to replace each parameter's default value in `tasks/<taskID>/config.yaml` with the value the user provided. Preserve the `# EDIT:` comment on the line.

For `app-specific` templates, also set the `appName` and `env` parameter values in `config.yaml` — they appear as the first two `parameters:` rows in templates that follow the convention.

Show the user the final state of config.yaml and template.json so they can confirm. The `name:` field in `config.yaml` should contain the templated string (e.g. `"[{{ .appName }}-{{ .env }}] {{ .serviceName }} ..."`) — do **not** pre-resolve it; Monaco resolves it at deploy time.

## Step 8 — Commit to git

Run these commands:
```
git add tasks/<taskID>/
git commit -m "Add <taskID>: <chosen-template> task"
git push origin main
```

## Step 9 — Advise the user

Tell the user:
- Their taskID
- To go to Jenkins → Build with Parameters
- Set TASK_ID = `<taskID>`
- Set TARGET_ENVIRONMENT = `ylq89164` (or change if needed)
- Leave SKIP_DEPLOY unchecked for a real deploy, or check it for dry-run only
- Click Build
