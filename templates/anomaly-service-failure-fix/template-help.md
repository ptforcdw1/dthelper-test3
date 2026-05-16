# anomaly-service-failure-fix

Service failure rate anomaly detection using a **fixed threshold**. Alerts when the percentage of failing service calls exceeds the configured threshold in any 5-minute period.

**Schema:** `builtin:anomaly-detection.services` (version 0.0.19 at the time this template was generated)
**Scope:** placeholder `SERVICE-0000000000000000` (edit `config.yaml` — set to a real Dynatrace SERVICE entity ID, or `environment` for tenant-wide defaults)
**Max objects per scope target:** 1

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `thresholdPercent` | float (%) | `10` | Alert if the failure rate exceeds this percentage during any 5-minute period. Schema default is `0` (alert on any failure); `10` is used here as a more practical starting point. |
| `requestsPerMinute` | float | `10` | Over-alerting protection — only alert when the service receives at least this many requests per minute. |
| `minutesAbnormalState` | integer (1-60) | `1` | Only alert if the abnormal state persists for at least this many minutes. |
| `sensitivity` | enum (`low` / `medium` / `high`) | `"low"` | How aggressively Dynatrace fires alerts. `low` = fewer false positives; `high` = noisier. |

## Example deployment outcome

After deploy, the configured service uses **fixed-threshold** failure rate anomaly detection: Dynatrace raises a problem when the failure rate exceeds `thresholdPercent` over a 5-minute window for at least `minutesAbnormalState` minutes (with at least `requestsPerMinute` traffic), gated by `sensitivity`. Response time detection, service load spikes, and service load drops are **disabled** in this template.

## Notes

- The schema default for `threshold` is `0.0`. This template ships with `10` because alerting on any failure is rarely useful in production — tune per service.
- `responseTime`, `loadDrops`, and `loadSpikes` are set to `enabled: false` in `template.json`. To enable them, edit `template.json` directly.
- `maxObjects` is 1 per scope target; re-deploying overwrites the prior config.
- Refresh the stored schema with `/refresh-schema` if Dynatrace updates the tenant.
