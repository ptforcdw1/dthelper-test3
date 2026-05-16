# Template Index

## anomaly-service-responsetime-fix
Service response time anomaly detection — fixed-threshold alerts on median RT and slowest-10% RT.

| Parameter | Description | Default |
|---|---|---|
| `degradationMs` | median RT threshold in ms (5-min window) | `100` |
| `slowestDegradationMs` | slowest-10% RT threshold in ms (5-min window) | `1000` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |
| `sensitivity` | alert sensitivity (`low` / `medium` / `high`) | `low` |

## anomaly-service-responsetime-adapt
Service response time anomaly detection — adaptive baseline alerts (both absolute ms and relative % must be exceeded).

| Parameter | Description | Default |
|---|---|---|
| `degradationMs` | absolute median RT threshold (ms) | `100` |
| `degradationPercent` | relative median RT threshold (% above baseline) | `50` |
| `slowestDegradationMs` | absolute slowest-10% RT threshold (ms) | `1000` |
| `slowestDegradationPercent` | relative slowest-10% RT threshold (% above baseline) | `100` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |

## anomaly-service-failure-fix
Service failure rate anomaly detection — fixed-threshold alerts when failure rate exceeds a percentage.

| Parameter | Description | Default |
|---|---|---|
| `thresholdPercent` | failure rate threshold (% of failing calls) | `10` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |
| `sensitivity` | alert sensitivity (`low` / `medium` / `high`) | `low` |

## anomaly-service-failure-adapt
Service failure rate anomaly detection — adaptive alerts (both absolute and relative increases must be exceeded).

| Parameter | Description | Default |
|---|---|---|
| `absoluteIncreasePercent` | absolute failure-rate increase threshold (%) | `0` |
| `relativeIncreasePercent` | relative failure-rate increase threshold (% above baseline) | `50` |
| `requestsPerMinute` | minimum traffic before alerting | `10` |
| `minutesAbnormalState` | minutes abnormal state must persist (1-60) | `1` |
