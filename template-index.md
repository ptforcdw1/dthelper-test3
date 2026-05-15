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
