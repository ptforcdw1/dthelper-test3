# Template Parameters

Parameter definitions for each template. The template's `levelFlag` and `nameTemplate` live in `template-index.md`.

For **app-specific** templates, `appName` and `env` are **implicit** parameters that `/new-task` prompts for automatically — they do not appear in the tables below.

## anomaly-service-responsetime-fix

| Parameter | Description | Default |
|---|---|---|
| `serviceName` | human-readable service name (used in the config name) | `myservice` |
| `degradationMs` | median RT threshold in ms (5-min window) | `100` |
| `slowestDegradationMs` | slowest-10% RT threshold in ms (5-min window) | `1000` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |
| `sensitivity` | alert sensitivity (`low` / `medium` / `high`) | `low` |

## anomaly-service-responsetime-adapt

| Parameter | Description | Default |
|---|---|---|
| `serviceName` | human-readable service name (used in the config name) | `myservice` |
| `degradationMs` | absolute median RT threshold (ms) | `100` |
| `degradationPercent` | relative median RT threshold (% above baseline) | `50` |
| `slowestDegradationMs` | absolute slowest-10% RT threshold (ms) | `1000` |
| `slowestDegradationPercent` | relative slowest-10% RT threshold (% above baseline) | `100` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |

## anomaly-service-failure-fix

| Parameter | Description | Default |
|---|---|---|
| `serviceName` | human-readable service name (used in the config name) | `myservice` |
| `thresholdPercent` | failure rate threshold (% of failing calls) | `10` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |
| `sensitivity` | alert sensitivity (`low` / `medium` / `high`) | `low` |

## anomaly-service-failure-adapt

| Parameter | Description | Default |
|---|---|---|
| `serviceName` | human-readable service name (used in the config name) | `myservice` |
| `absoluteIncreasePercent` | absolute failure-rate increase threshold (%) | `0` |
| `relativeIncreasePercent` | relative failure-rate increase threshold (% above baseline) | `50` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |
