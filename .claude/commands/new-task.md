Create a new Monaco task from a template and commit it to git. Follow every step below in order without skipping.

---

## Step 1 — Read the template index

Read `template-index.md`. Parse every `## <name>` heading as an available template name. For each template, also parse the parameter table rows (columns: Parameter, Description, Default) — you will need these in Step 6.

## Step 2 — Ask the user which task type to create

Use AskUserQuestion with the template names from `template-index.md` as options (one option per template, use the description line as the option description). Ask: "Which task template do you want to use?"

## Step 3 — Generate the next taskID

Use PowerShell to list all subdirectories under `tasks/` whose names match the pattern `task` followed by digits (e.g. `task001`, `task002`). Find the highest number. The new taskID is that number + 1, zero-padded to 3 digits (e.g. if highest is `task002`, new is `task003`). If no matching directories exist, start at `task001`.

Show the user the generated taskID before proceeding.

## Step 4 — Create the task directory and copy template files

Use PowerShell to:
1. Create the directory `tasks/<taskID>/`
2. Copy `templates/<chosen-template>/config.yaml` to `tasks/<taskID>/config.yaml`
3. Copy `templates/<chosen-template>/template.json` to `tasks/<taskID>/template.json`

## Step 5 — Load parameter definitions

From the data already parsed in Step 1, extract the parameter rows for the chosen template. Each row gives you: parameter name, description, and default value. No file reads needed.

## Step 6 — Ask the user for each parameter value

For each parameter from Step 5, ask the user for a value. Show:
- The parameter name
- What it controls (the Description column)
- The current default value

Ask all parameters in a single AskUserQuestion call where possible (up to 4 at a time). If there are more than 4, ask in batches.

## Step 7 — Update config.yaml with the provided values

Use Edit to replace each parameter's default value in `tasks/<taskID>/config.yaml` with the value the user provided. Preserve the `# EDIT:` comment on the line.

Show the user the final state of config.yaml and template.json so they can confirm.

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
