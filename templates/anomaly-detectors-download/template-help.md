# anomaly-detectors-download

Download all Davis anomaly detectors from Dynatrace.

**Schema:** `builtin:davis.anomaly-detectors` (version 1.0.14 at the time this template was generated)
**Scope:** environment
**Max objects per environment:** 1000
**Level:** global (download-only)
**Task type:** download — exports existing configuration, does not deploy

## What this does

This is a **download-only** task. It exports all configured Davis anomaly detectors from your Dynatrace environment into a JSON file. The configuration is not stored in the git repository — the exported file is archived as a Jenkins build artifact for manual download.

After running this task in Jenkins, navigate to the build's "Artifacts" section and download the `.json` files from the `export/` folder.

## How to use

1. In Jenkins, run the existing `Jenkinsfile` pipeline.
2. Set `TASK_ID` to `anomaly-download` (or create a task folder from this template).
3. The pipeline will run `monaco deploy --download`, exporting all anomaly detectors.
4. Artifacts are available in the build's "Artifacts" section — no git commit needed.

## Notes

- This template has no parameters — it exports all Davis anomaly detectors configured in the target environment.
- The exported JSON can be version-controlled manually if desired, but they are not included in the default `tasks/` gitignore.
- Refresh the stored schema with `/refresh-schema` if Dynatrace updates the tenant.
