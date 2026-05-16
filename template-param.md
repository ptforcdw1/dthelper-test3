# Template Parameters

Parameter definitions for each template. The template's `levelFlag` and `nameTemplate` live in `template-index.md`.

For **app-specific** templates, `appName` and `env` are **implicit** parameters that `/new-task` prompts for automatically — they do not appear in the tables below.

## anomaly-service-responsetime-fix

Single source of truth for prompts and defaults is `templates/anomaly-service-responsetime-fix/request-schema.json`. The table below is a human-readable mirror; keep it in sync with the schema.

| Parameter | Required? | Description | Default |
|---|---|---|---|
| `serviceName` | yes | Which Dynatrace service to monitor. Use the display name shown in Dynatrace (e.g. `Tomcat/localhost`). `resolve.py` looks this up and writes the matching SERVICE-id into `scope`. | `myservice` |
| `degradationMs` | suggested | Alert when median response time goes above this many milliseconds (5-min window). | `100` |
| `slowestDegradationMs` | suggested | Alert when the slowest 10% of requests go above this many milliseconds (5-min window). | `1000` |
| `requestsPerMinute` | suggested | Minimum traffic (requests/min) before the alert is allowed to fire — suppresses false alarms on idle services. | `10` |
| `minutesAbnormalState` | suggested | How many minutes the threshold must be exceeded before alerting (1-60). | `1` |
| `sensitivity` | suggested | Alert sensitivity: `low`, `medium`, or `high`. | `low` |

## anomaly-service-responsetime-adapt

| Parameter | Description | Default |
|---|---|---|
| `serviceName` | Which Dynatrace service to monitor (display name in Dynatrace, e.g. `Tomcat/localhost`). | `myservice` |
| `degradationMs` | Alert when median response time goes above this many milliseconds. | `100` |
| `degradationPercent` | Alert when median is this % above the learned baseline. | `50` |
| `slowestDegradationMs` | Alert when the slowest 10% of requests go above this many milliseconds. | `1000` |
| `slowestDegradationPercent` | Alert when slowest-10% is this % above baseline. | `100` |
| `requestsPerMinute` | Minimum traffic (requests/min) before alerting fires — suppresses noise on idle services. | `10` |
| `minutesAbnormalState` | How many minutes the threshold must be exceeded before alerting (1-60). | `1` |

## anomaly-service-failure-fix

| Parameter | Description | Default |
|---|---|---|
| `serviceName` | Which Dynatrace service to monitor (display name in Dynatrace, e.g. `Tomcat/localhost`). | `myservice` |
| `thresholdPercent` | Alert when failure rate (% of failing calls) exceeds this value. | `10` |
| `requestsPerMinute` | Minimum traffic (requests/min) before alerting fires. | `10` |
| `minutesAbnormalState` | How many minutes the threshold must be exceeded before alerting (1-60). | `1` |
| `sensitivity` | Alert sensitivity: `low`, `medium`, or `high`. | `low` |

## anomaly-service-failure-adapt

| Parameter | Description | Default |
|---|---|---|
| `serviceName` | Which Dynatrace service to monitor (display name in Dynatrace, e.g. `Tomcat/localhost`). | `myservice` |
| `absoluteIncreasePercent` | Absolute increase in failure rate (%) that triggers an alert. | `0` |
| `relativeIncreasePercent` | Failure-rate increase relative to baseline (%) that triggers an alert. | `50` |
| `requestsPerMinute` | Minimum traffic (requests/min) before alerting fires. | `10` |
| `minutesAbnormalState` | How many minutes the threshold must be exceeded before alerting (1-60). | `1` |
