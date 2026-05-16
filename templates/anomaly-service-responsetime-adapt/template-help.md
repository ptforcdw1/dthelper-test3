# anomaly-service-responsetime-adapt

Service response time anomaly detection using **adaptive (auto) thresholds**. Dynatrace learns the service's baseline RT and alerts only when the observed RT exceeds **both** an absolute ms threshold AND a relative % threshold above baseline.

**Schema:** `builtin:anomaly-detection.services` (version 0.0.19 at the time this template was generated)
**Scope:** placeholder `SERVICE-0000000000000000` (edit `config.yaml` — set to a real Dynatrace SERVICE entity ID, or `environment` for tenant-wide defaults)
**Max objects per scope target:** 1
**Level:** app-specific
**Name template:** `[<AppName>-<Env>] <serviceName> response time adaptive`

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `appName` | string | `myapp` | Application name used in the `[<AppName>-<Env>]` config-name prefix. Asked for by `/new-task`. |
| `env` | string | `prod` | Environment (e.g. `prod`, `staging`) used in the prefix. Asked for by `/new-task`. |
| `serviceName` | string | `myservice` | Human-readable service name shown in the config name. Does **not** affect targeting — that's `scope`. |
| `degradationMs` | float (ms) | `100` | Absolute median-RT threshold. Together with `degradationPercent`, both must be exceeded to alert. |
| `degradationPercent` | float (%) | `50` | Relative median-RT threshold above the learned baseline. |
| `slowestDegradationMs` | float (ms) | `1000` | Absolute slowest-10% RT threshold. Together with `slowestDegradationPercent`, both must be exceeded to alert. |
| `slowestDegradationPercent` | float (%) | `100` | Relative slowest-10% RT threshold above the learned baseline. |
| `requestsPerMinute` | float | `10` | Over-alerting protection — only alert when the service receives at least this many requests per minute. |
| `minutesAbnormalState` | integer (1-60) | `1` | Only alert if the abnormal state persists for at least this many minutes. |

## Example deployment outcome

After deploy, the configured service uses **adaptive-baseline** response time anomaly detection: Dynatrace observes the service for at least 20% of a week, learns the typical RT, then raises a problem when **both** the absolute ms threshold AND the relative % threshold are exceeded (separately for median and slowest-10%) for `minutesAbnormalState` minutes, gated by the `requestsPerMinute` minimum traffic. Failure rate, load spikes, and load drops detection are **disabled** in this template.

## Notes

- Auto mode requires at least 20% of a week of observed traffic to establish a baseline. Before that, no anomaly alerts will fire.
- Both the ms and % thresholds must be crossed simultaneously to alert — tune one to make the rule more sensitive without falsely tripping the other.
- `failureRate`, `loadDrops`, and `loadSpikes` are set to `enabled: false`. To turn any of them on, edit `template.json` directly.
- `maxObjects` is 1 per scope target; re-deploying overwrites the prior config.
- Refresh the stored schema with `/refresh-schema` if Dynatrace updates the tenant.
