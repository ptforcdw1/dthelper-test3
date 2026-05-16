"""Discover templates and load their parameter schemas.

Each template under templates/<name>/ may have a request-schema.json (preferred)
or fall back to template-param.md. This module presents a uniform shape:

    {
      "appName":    {"type": "string", "required": True,  "default": None, ...},
      "env":        {"type": "string", "required": True,  "enum": [...],   ...},
      "serviceName":{"type": "string", "required": True,  "lookup": {...}, ...},
      ...
    }

The form code never reads template-param.md or request-schema.json directly --
it calls list_templates() and load_params(template_name).
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional


def list_templates(repo_root: Path) -> List[str]:
    """Return template folder names, sorted."""
    return sorted(
        p.name for p in (repo_root / "templates").iterdir()
        if p.is_dir() and (p / "config.yaml").exists()
    )


def load_params(repo_root: Path, template_name: str) -> Dict[str, Dict[str, Any]]:
    """Return the param dict for a template. Prefers request-schema.json."""
    tpl_dir = repo_root / "templates" / template_name
    schema_path = tpl_dir / "request-schema.json"
    if schema_path.exists():
        return _from_request_schema(schema_path)
    return _from_template_param_md(repo_root / "template-param.md", template_name)


def _from_request_schema(path: Path) -> Dict[str, Dict[str, Any]]:
    """Parse the canonical request-schema.json."""
    data = json.loads(path.read_text(encoding="utf-8"))
    out: Dict[str, Dict[str, Any]] = {}
    for name, spec in data.get("params", {}).items():
        out[name] = {
            "type":        spec.get("type", "string"),
            "required":    bool(spec.get("required")),
            "suggested":   bool(spec.get("suggested")),
            "default":     spec.get("default"),
            "enum":        spec.get("enum"),
            "min":         spec.get("min"),
            "max":         spec.get("max"),
            "prompt":      spec.get("prompt") or spec.get("description") or name,
            "description": spec.get("description", ""),
            "lookup":      spec.get("lookup"),
        }
    return out


_TABLE_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*`([^`]*)`\s*\|\s*$")


def _from_template_param_md(md_path: Path, template_name: str) -> Dict[str, Dict[str, Any]]:
    """Fallback parser. Treats every row as 'suggested' with no enum/min/max."""
    if not md_path.exists():
        return {}
    lines = md_path.read_text(encoding="utf-8").splitlines()
    out: Dict[str, Dict[str, Any]] = {}
    in_section = False
    for line in lines:
        if line.startswith("## "):
            in_section = (line[3:].strip() == template_name)
            continue
        if not in_section:
            continue
        m = _TABLE_ROW.match(line)
        if not m:
            continue
        name, desc, default = m.group(1), m.group(2), m.group(3)
        if name.lower() == "parameter":
            continue  # header row
        out[name] = {
            "type":        _guess_type(default),
            "required":    False,
            "suggested":   True,
            "default":     _coerce(default, _guess_type(default)),
            "enum":        None,
            "min":         None,
            "max":         None,
            "prompt":      desc,
            "description": desc,
            "lookup":      None,
        }
    return out


def _guess_type(raw: str) -> str:
    if raw == "":
        return "string"
    if raw.lower() in ("true", "false"):
        return "boolean"
    try:
        int(raw)
        return "integer"
    except ValueError:
        return "string"


def _coerce(raw: str, t: str) -> Any:
    if t == "integer":
        return int(raw)
    if t == "boolean":
        return raw.lower() == "true"
    return raw
