# Template Index

One section per template. Lists `Level` (`app-specific` or `global`), `Name template`, and a one-line description. **Parameter tables live in `template-param.md`.**

## Naming convention

- **app-specific** templates must use a name template of the form `[<AppName>-<Env>] <description>`, where `AppName` and `Env` are filled in by `/new-task` and `<description>` may include other parameter placeholders (e.g. `<serviceName>`, `<namespace>`).
- **global** templates use a plain `<description>` with no `[AppName-Env]` prefix.
- Placeholders use `<paramName>` syntax in this file (documentation only). In `config.yaml` they become Monaco's `{{ .paramName }}`.

---

## anomaly-service-responsetime-fix
- **Level:** app-specific
- **Name template:** `[<AppName>-<Env>] <serviceName> response time fixed`
- Service response time anomaly detection — fixed-threshold alerts on median RT and slowest-10% RT.

## anomaly-service-responsetime-adapt
- **Level:** app-specific
- **Name template:** `[<AppName>-<Env>] <serviceName> response time adaptive`
- Service response time anomaly detection — adaptive baseline alerts (both absolute ms and relative % must be exceeded).

## anomaly-service-failure-fix
- **Level:** app-specific
- **Name template:** `[<AppName>-<Env>] <serviceName> failure rate fixed`
- Service failure rate anomaly detection — fixed-threshold alerts when failure rate exceeds a percentage.

## log-ingest-k8s-namespace
- **Level:** app-specific
- **Name template:** `[<AppName>-<Env>] log ingest - <namespaceName> namespace`
- Log ingest rule that stores logs from a specific Kubernetes namespace (matches k8s.namespace.name).

## anomaly-detectors-download
- **Level:** global
- **Task type:** download (export-only, no deployment)
- Download all Davis anomaly detectors from Dynatrace.
