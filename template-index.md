# Template Index

## log-ingest-k8s
Kubernetes log ingestion — configures which namespace's logs to ingest into Dynatrace.

| Parameter | Description | Default |
|---|---|---|
| `namespace` | target k8s namespace | `default` |

## auto-tagging
Automated ownership tagging — creates a team tag rule in Dynatrace.

| Parameter | Description | Default |
|---|---|---|
| `teamName` | team display name | `POC Team` |
| `identifier` | unique identifier (lowercase, no spaces) | `poc-team` |

## update-windows
Weekly maintenance update window — defines a recurring deployment window.

| Parameter | Description | Default |
|---|---|---|
| `windowName` | window display name | `POC Update Window` |

## host-alerts
Host CPU anomaly alerting — creates a Davis anomaly detector for host CPU.

| Parameter | Description | Default |
|---|---|---|
| `alertTitle` | alert display title | `POC Host CPU Alert` |

## get-alerts
Download all existing alert configs from Dynatrace — runs `monaco download` for the given schema and archives results as a Jenkins artifact.

| Parameter | Description | Default |
|---|---|---|
| `schema` | Settings 2.0 schema to download | `builtin:davis.anomaly-detectors` |
| `outputFolder` | subfolder under tasks/\<taskID\>/ to write downloaded configs | `output` |
