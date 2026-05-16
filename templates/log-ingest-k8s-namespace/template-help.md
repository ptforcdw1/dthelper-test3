# log-ingest-k8s-namespace

Log ingest rule that stores logs from a specific Kubernetes namespace (matches `k8s.namespace.name`).

**Schema:** `builtin:logmonitoring.log-storage-settings` (version 1.0.18 at the time this template was generated)
**Scope:** `environment` (tenant-wide). The schema also allows `KUBERNETES_CLUSTER`, `HOST_GROUP`, and `HOST` scopes — edit `config.yaml` if you want to narrow to a specific cluster.
**Max objects per environment:** 1000
**Level:** app-specific
**Name template:** `[<AppName>-<Env>] log ingest - <namespaceName> namespace`

## Parameters

| Parameter | Type | Default | Controls |
|---|---|---|---|
| `appName` | string | `myapp` | Application name used in the `[<AppName>-<Env>]` config-name prefix. |
| `env` | string | `prod` | Environment used in the prefix. |
| `namespaceName` | string | `my-namespace` | Kubernetes namespace to match. Written into `matchers[0].values[0]` in `template.json`. `matchers[0].attribute` is hardcoded to `k8s.namespace.name`. |
| `ruleTitle` | string | `Ingest logs from k8s namespace` | Rule name displayed in the Dynatrace UI (written into `config-item-title`). |

## Example deployment outcome

After deploy, Dynatrace has a new log ingest rule named (in Monaco) `[petclinic-dev] log ingest - kube-system namespace` and shown in the Dynatrace UI as `Ingest logs from k8s namespace` (or whatever your `ruleTitle` resolves to). The rule has `send-to-storage: true` with a single matcher: `k8s.namespace.name MATCHES ["kube-system"]`. All log records OneAgent already collects that carry that namespace tag will be stored; logs not matching this (or any other) ingest rule are dropped per Dynatrace's defaults.

## Notes

- `send-to-storage` is hardcoded to `true` in `template.json` — i.e. this template **stores** matching logs. To create a **drop** rule, flip it to `false`.
- `enabled` is hardcoded to `true`. Flip it in `template.json` if you want disabled-by-default tasks.
- `matchers` is hardcoded to a single matcher on `k8s.namespace.name`. To match additional attributes (e.g. also filter by `k8s.deployment.name` or `loglevel`), add more entries to the `matchers` array in `template.json`. The matcher attributes available include: `dt.entity.process_group`, `log.source`, `log.content`, `loglevel`, `host.tag`, `k8s.container.name`, `k8s.deployment.name`, `k8s.pod.annotation`, `k8s.pod.label`, `k8s.workload.name`, `k8s.workload.kind`, `container.name`, `journald.unit`.
- To match multiple namespaces in one rule, add more strings to `matchers[0].values`. The `values` array accepts up to 1024 chars per entry.
- The scope is currently `environment` (tenant-wide). To narrow to a specific cluster, change `scope:` in `config.yaml` to a `KUBERNETES_CLUSTER-xxxxxxxxxxxxxxxx` entity ID.
- This template handles the *store/drop* decision per namespace. To shape, parse, or redact those logs once stored, pair with `builtin:openpipeline.logs.routing` + `builtin:openpipeline.logs.pipelines`.
- Refresh the stored schema with `/refresh-schema log-ingest-k8s-namespace` if Dynatrace updates the schema version.
