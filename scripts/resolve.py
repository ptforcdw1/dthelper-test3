#!/usr/bin/env python3
"""
resolve.py -- translate human-readable params in a task's config.yaml into
Dynatrace entity IDs, in place.

Flow:
  1. Read tasks/<task-id>/config.yaml.
  2. Determine the template name from configs[0].id.
  3. Load templates/<template>/request-schema.json.
  4. For each schema param with a "lookup" block, take the value from
     configs[0].config.parameters[<param>], call /api/v2/entities with an
     exact-name selector, and write the resolved entityId into the path
     given by lookup.writeTo (e.g. "type.settings.scope").
  5. Save the modified config.yaml back to disk.

If the template has no request-schema.json, or the schema has no lookup
params, the script exits 0 without touching config.yaml.

Exit non-zero with a clear message on:
  - missing required param in config.yaml
  - 0 or >1 entities matching a lookup
  - Dynatrace API error
  - missing/unwritable writeTo target

Env:
  DT_API_TOKEN -- API token with `entities.read`.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required.  pip install pyyaml", file=sys.stderr)
    sys.exit(1)


def fail(msg: str) -> None:
    print(f"\nERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def dt_get(env_url: str, path: str, token: str) -> dict:
    url = f"{env_url}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Api-Token {token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        fail(f"Dynatrace API {e.code} on {url}\n{body}")
    except urllib.error.URLError as e:
        fail(f"Dynatrace API unreachable ({url}): {e.reason}")


def lookup_entity(env_url: str, token: str, entity_type: str, name: str) -> str:
    qs = urllib.parse.urlencode({
        "entitySelector": f'type("{entity_type}"),entityName.equals("{name}")',
        "fields": "displayName",
        "pageSize": 50,
    })
    data = dt_get(env_url, f"/api/v2/entities?{qs}", token)
    entities = data.get("entities", [])

    if not entities:
        fail(
            f"No {entity_type} found with name '{name}'.\n"
            f"  Check spelling, the target environment, and that the entity "
            f"has been monitored recently."
        )

    if len(entities) > 1:
        listing = "\n    ".join(
            f"{e['entityId']}  ({e.get('displayName', 'no displayName')})"
            for e in entities
        )
        fail(
            f"{len(entities)} {entity_type} entities match '{name}':\n    {listing}\n"
            f"  Names must be unique. Add a tag/host filter to the selector in "
            f"request-schema.json, or ask your Dynatrace admin to rename one."
        )

    return entities[0]["entityId"]


def set_by_path(obj: dict, dotted_path: str, value: str) -> None:
    """Set obj[a][b][c] = value given dotted_path 'a.b.c'. All keys must exist."""
    parts = dotted_path.split(".")
    cursor = obj
    for part in parts[:-1]:
        if part not in cursor:
            fail(f"writeTo path '{dotted_path}' invalid: '{part}' not found in config.yaml")
        cursor = cursor[part]
    cursor[parts[-1]] = value


def resolve(task_id: str, env_url: str) -> None:
    token = os.environ.get("DT_API_TOKEN")
    if not token:
        fail("DT_API_TOKEN env var is required.")

    config_path = f"tasks/{task_id}/config.yaml"
    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        fail(f"Task config not found: {config_path}")
    except yaml.YAMLError as e:
        fail(f"Could not parse {config_path}: {e}")

    if not config or "configs" not in config or not config["configs"]:
        fail(f"{config_path} has no 'configs' entries.")

    cfg = config["configs"][0]
    template_name = cfg.get("id")
    if not template_name:
        fail(f"{config_path} configs[0] has no 'id' field.")

    schema_path = f"templates/{template_name}/request-schema.json"
    if not os.path.exists(schema_path):
        print(f"  no request-schema.json for template '{template_name}' -- nothing to resolve")
        return

    with open(schema_path) as f:
        schema = json.load(f)

    params = cfg.get("config", {}).get("parameters", {}) or {}
    lookups = {
        name: spec["lookup"]
        for name, spec in schema.get("params", {}).items()
        if "lookup" in spec
    }

    if not lookups:
        print(f"  template '{template_name}' has no lookup params -- nothing to resolve")
        return

    print(f"Resolving names -> IDs for task {task_id} (template: {template_name})")
    changed = False
    for param_name, lookup in lookups.items():
        value = params.get(param_name)
        if value is None:
            fail(
                f"Parameter '{param_name}' is missing from {config_path} "
                f"but is required for lookup."
            )

        entity_type = lookup["entityType"]
        write_to    = lookup["writeTo"]
        print(f"  looking up {entity_type} '{value}' ...", end=" ", flush=True)
        entity_id = lookup_entity(env_url, token, entity_type, str(value))
        print(f"-> {entity_id}  (writing to {write_to})")

        set_by_path(cfg, write_to, entity_id)
        changed = True

    if changed:
        with open(config_path, "w") as f:
            yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)
        print(f"\nUpdated {config_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--task-id", required=True,
                    help="Task subdirectory under tasks/ (e.g. task007)")
    ap.add_argument("--env-url", required=True,
                    help="Dynatrace base URL, e.g. https://ylq89164.live.dynatrace.com")
    args = ap.parse_args()
    resolve(args.task_id, args.env_url)


if __name__ == "__main__":
    main()
