# anomaly-service-responsetime-fix

Service response time anomaly detection using **fixed thresholds**. Alerts when median RT or slowest-10% RT cross hard ms thresholds within a 5-minute observation window.

**Schema:** `builtin:anomaly-detection.services` (version 0.0.19 at the time this template was generated)
**Scope:** placeholder `SERVICE-0000000000000000` (edit `config.yaml` — set to a real Dynatrace SERVICE entity ID, or `environment` for tenant-wide defaults)
**Max objects per scope target:** 1
**Level:** app-specific
**Name template:** `[<AppName>-<Env>] <serviceName> response time fixed`

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `appName` | string | `myapp` | Application name used in the `[<AppName>-<Env>]` config-name prefix. Asked for by `/new-task`. |
| `env` | string | `prod` | Environment (e.g. `prod`, `staging`) used in the prefix. Asked for by `/new-task`. |
| `serviceName` | string | `myservice` | Human-readable service name shown in the config name. Does **not** affect targeting — that's `scope`. |
| `degradationMs` | float (ms) | `100` | Alert if the median response time across all requests degrades beyond this threshold within a 5-minute window. |
| `slowestDegradationMs` | float (ms) | `1000` | Alert if the response time of the slowest 10% of requests degrades beyond this threshold within a 5-minute window. |
| `requestsPerMinute` | float | `10` | Over-alerting protection — only alert when the service receives at least this many requests per minute. |
| `minutesAbnormalState` | integer (1-60) | `1` | Only alert if the abnormal state persists for at least this many minutes. |
| `sensitivity` | enum (`low` / `medium` / `high`) | `"low"` | How aggressively Dynatrace fires alerts. `low` = fewer false positives; `high` = noisier. |

## Example deployment outcome

After deploy, the configured service uses **fixed-threshold** response time anomaly detection: Dynatrace raises a problem when the median request RT crosses `degradationMs` or the slowest-10% RT crosses `slowestDegradationMs` for `minutesAbnormalState` minutes straight (with at least `requestsPerMinute` traffic), gated by the chosen `sensitivity`. Failure rate detection, service load spikes, and service load drops are **disabled** in this template.

## Notes

- `failureRate`, `loadDrops`, and `loadSpikes` are set to `enabled: false` in `template.json`. To turn any of them on, edit `template.json` directly — note that enabling them also requires filling in their required sub-objects (see `schema.json`).
- `maxObjects` is 1 per scope target; re-deploying overwrites the prior config for the same scope.
- Refresh the stored schema with `/refresh-schema` if Dynatrace updates the tenant.
