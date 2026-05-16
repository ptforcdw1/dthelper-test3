"""Clone the repo, scaffold a new task directory, commit and push.

The form runs on a server with its own checkout under WORK_DIR. We pull
fresh on every request so we don't drift from main.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional, Tuple


GIT_USER_NAME  = os.environ.get("GIT_USER_NAME", "monaco-webform")
GIT_USER_EMAIL = os.environ.get("GIT_USER_EMAIL", "monaco-webform@example.com")


class GitError(RuntimeError):
    pass


def _run(cmd: list, cwd: Path) -> str:
    """Run a git command, return stdout, raise GitError on failure."""
    result = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise GitError(
            f"`{' '.join(cmd)}` failed (exit {result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result.stdout


def _remote_url(repo_url: str, pat: Optional[str]) -> str:
    """Inject the PAT into the URL for HTTPS auth."""
    if not pat:
        return repo_url
    if repo_url.startswith("https://"):
        return repo_url.replace("https://", f"https://x-access-token:{pat}@", 1)
    return repo_url


def ensure_repo(work_dir: Path, repo_url: str, branch: str, pat: Optional[str]) -> Path:
    """Clone the repo if needed; pull latest otherwise. Return the repo path."""
    work_dir.mkdir(parents=True, exist_ok=True)
    repo_path = work_dir / "repo"
    if not (repo_path / ".git").exists():
        if repo_path.exists():
            shutil.rmtree(repo_path)
        _run(["git", "clone", "--branch", branch, _remote_url(repo_url, pat), str(repo_path)], work_dir)
    else:
        # Repoint remote in case PAT rotated.
        _run(["git", "remote", "set-url", "origin", _remote_url(repo_url, pat)], repo_path)
        _run(["git", "fetch", "origin", branch], repo_path)
        _run(["git", "checkout", branch], repo_path)
        _run(["git", "reset", "--hard", f"origin/{branch}"], repo_path)
    return repo_path


def next_task_id(repo_path: Path) -> str:
    """Find the highest taskNNN under tasks/ and return the next one."""
    tasks_dir = repo_path / "tasks"
    if not tasks_dir.exists():
        return "task001"
    nums = [
        int(p.name[4:]) for p in tasks_dir.iterdir()
        if p.is_dir() and re.fullmatch(r"task\d+", p.name)
    ]
    return f"task{(max(nums) + 1 if nums else 1):03d}"


def write_task(
    repo_path: Path,
    template_name: str,
    task_id: str,
    user_values: Dict[str, Any],
) -> Path:
    """Create tasks/<task_id>/ from the template and apply user-provided values.

    Mirrors /new-task Step 7: only edits lines for params the user supplied.
    Params left blank keep the template default. Lines marked with `# EDIT:`
    comments preserve those comments.
    """
    src = repo_path / "templates" / template_name
    dst = repo_path / "tasks" / task_id
    dst.mkdir(parents=True, exist_ok=False)
    shutil.copy2(src / "config.yaml", dst / "config.yaml")
    shutil.copy2(src / "template.json", dst / "template.json")

    cfg_path = dst / "config.yaml"
    cfg_text = cfg_path.read_text(encoding="utf-8")
    for name, value in user_values.items():
        if value is None or value == "":
            continue  # user skipped -- leave template default in place
        cfg_text = _replace_param_line(cfg_text, name, value)
    cfg_path.write_text(cfg_text, encoding="utf-8")
    return dst


_PARAM_LINE = re.compile(
    r"^(?P<indent>\s+)(?P<name>[A-Za-z_][A-Za-z0-9_-]*):\s*"
    r"(?P<value>\".*?\"|[^\s#]+)(?P<trailing>\s*(?:#.*)?)$",
    re.MULTILINE,
)


def _replace_param_line(text: str, name: str, value: Any) -> str:
    """Replace the value on the `name: ...` line, keeping indent + trailing comment."""
    rendered = _render_value(value)
    def repl(m):
        if m.group("name") != name:
            return m.group(0)
        return f'{m.group("indent")}{name}: {rendered}{m.group("trailing")}'
    return _PARAM_LINE.sub(repl, text)


def _render_value(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    # quote strings
    s = str(v).replace('"', '\\"')
    return f'"{s}"'


def commit_and_push(
    repo_path: Path,
    task_id: str,
    template_name: str,
    branch: str,
) -> str:
    """Stage tasks/<task_id>/, commit, push. Return the commit sha."""
    _run(["git", "config", "user.name",  GIT_USER_NAME],  repo_path)
    _run(["git", "config", "user.email", GIT_USER_EMAIL], repo_path)
    _run(["git", "add", f"tasks/{task_id}/"], repo_path)
    _run(
        ["git", "commit", "-m", f"Add {task_id}: {template_name} task (via webform)"],
        repo_path,
    )
    _run(["git", "push", "origin", branch], repo_path)
    return _run(["git", "rev-parse", "HEAD"], repo_path).strip()
