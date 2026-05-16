# anomaly-service-failure-adapt

Service failure rate anomaly detection using **adaptive (auto) thresholds**. Dynatrace learns the service's baseline failure rate and alerts only when the observed increase exceeds **both** an absolute % threshold AND a relative % threshold above baseline.

**Schema:** `builtin:anomaly-detection.services` (version 0.0.19 at the time this template was generated)
**Scope:** placeholder `SERVICE-0000000000000000` (edit `config.yaml` — set to a real Dynatrace SERVICE entity ID, or `environment` for tenant-wide defaults)
**Max objects per scope target:** 1

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `absoluteIncreasePercent` | float (%) | `0` | Absolute failure-rate increase threshold. Together with `relativeIncreasePercent`, both must be exceeded to alert. |
| `relativeIncreasePercent` | float (%) | `50` | Relative failure-rate increase threshold above the learned baseline. |
| `requestsPerMinute` | float | `10` | Over-alerting protection — only alert when the service receives at least this many requests per minute. |
| `minutesAbnormalState` | integer (1-60) | `1` | Only alert if the abnormal state persists for at least this many minutes. |

## Example deployment outcome

After deploy, the configured service uses **adaptive-baseline** failure rate anomaly detection: Dynatrace observes the service for at least 20% of a week, learns the typical failure rate, then raises a problem when **both** the absolute and relative increase thresholds are exceeded for `minutesAbnormalState` minutes (with at least `requestsPerMinute` traffic). Response time, service load spikes, and service load drops detection are **disabled** in this template.

## Notes

- Auto mode requires at least 20% of a week of observed traffic to establish a baseline. Before that, no failure-rate alerts will fire.
- Both `absoluteIncreasePercent` and `relativeIncreasePercent` must be exceeded simultaneously to alert.
- `responseTime`, `loadDrops`, and `loadSpikes` are set to `enabled: false` in `template.json`. To enable them, edit `template.json` directly.
- `maxObjects` is 1 per scope target; re-deploying overwrites the prior config.
- Refresh the stored schema with `/refresh-schema` if Dynatrace updates the tenant.
