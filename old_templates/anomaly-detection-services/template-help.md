# anomaly-detection-services

Custom response time anomaly detection for service endpoints.

**Schema:** `builtin:anomaly-detection.services` (version 0.0.19 at the time this template was generated)
**Scope:** `SERVICE` (a specific Dynatrace service entity — set the entity ID in `config.yaml`)
**Max objects per environment:** 1 per scope target

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `degradationMs` | integer (ms) | `100` | Alert if the median response time across all requests degrades beyond this threshold within a 5-minute observation window. |
| `slowestDegradationMs` | integer (ms) | `1000` | Alert if the response time of the slowest 10% of requests degrades beyond this threshold within a 5-minute observation window. |
| `sensitivity` | enum (`low` / `medium` / `high`) | `low` | How aggressively Dynatrace fires alerts. `low` = fewer false positives; `high` = more alerts. |

You also need to edit `scope:` in `config.yaml` to point at your target service. Set it to a real Dynatrace SERVICE entity ID (e.g. `SERVICE-1234567890ABCDEF`) or `environment` for the tenant-wide default.

## Example deployment outcome

After deploy, the configured service uses **fixed-threshold** response time anomaly detection: Dynatrace raises a problem when the median request RT crosses `degradationMs` or the slowest-10% RT crosses `slowestDegradationMs` for 5 minutes straight, gated by the chosen `sensitivity`. Failure rate detection stays on the schema defaults (auto mode); load drop/spike detection is disabled in this template.

## Notes

- The non-parameterized fields in `template.json` use defaults from the schema. Edit `template.json` directly if you need to change them — for example, set `failureRate.enabled` to `false` to silence failure-rate alerts, or switch `detectionMode` back to `auto` to use Dynatrace's auto-baseline mode.
- The `overAlertingProtection` thresholds (10 requests/min minimum, 1 minute abnormal state) are hardcoded in `template.json`; change them there if you want per-deploy overrides expose them as parameters.
- `maxObjects` is 1 per scope target — you can only have one config object per service. Re-deploying overwrites the prior config.
- Refresh the stored schema with `/refresh-schema` if Dynatrace updates the tenant.
