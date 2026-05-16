"""Streamlit webform: pick a template, fill params, submit -> git + Jenkins.

Run with:
    streamlit run webform/app.py

Env vars (see .env.example):
    REPO_URL              https://github.com/<org>/<repo>.git
    REPO_BRANCH           main
    GITHUB_PAT            personal access token with repo write
    WORK_DIR              /tmp/dthelper-webform  (where the repo gets cloned)
    JENKINS_URL           http://jenkins:8080
    JENKINS_USER          your-jenkins-user
    JENKINS_API_TOKEN     your-jenkins-api-token
    JENKINS_JOB           DTHelper-v3-monaco-mvp2
    TARGET_ENVIRONMENT    ylq89164
"""

import os
from pathlib import Path
from typing import Any, Dict

import streamlit as st

from git_ops import (
    GitError,
    commit_and_push,
    ensure_repo,
    next_task_id,
    write_task,
)
from jenkins_ops import JenkinsError, trigger_build, wait_for_build_url
from schema_loader import list_templates, load_params


# --- config from env -------------------------------------------------------

REPO_URL           = os.environ.get("REPO_URL",           "https://github.com/ptforcdw1/dthelper-test3.git")
REPO_BRANCH        = os.environ.get("REPO_BRANCH",        "main")
GITHUB_PAT         = os.environ.get("GITHUB_PAT")
WORK_DIR           = Path(os.environ.get("WORK_DIR",      "/tmp/dthelper-webform"))
JENKINS_URL        = os.environ.get("JENKINS_URL",        "http://localhost:8080")
JENKINS_USER       = os.environ.get("JENKINS_USER")
JENKINS_API_TOKEN  = os.environ.get("JENKINS_API_TOKEN")
JENKINS_JOB        = os.environ.get("JENKINS_JOB",        "DTHelper-v3-monaco-mvp2")
TARGET_ENVIRONMENT = os.environ.get("TARGET_ENVIRONMENT", "ylq89164")


# --- page ------------------------------------------------------------------

st.set_page_config(page_title="Monaco task creator", page_icon=":wrench:", layout="centered")
st.title("Monaco task creator")
st.caption(
    "Pick a template, fill the parameters, hit submit. This creates "
    "`tasks/<id>/`, commits to GitHub, and triggers Jenkins."
)


@st.cache_resource(show_spinner="Fetching latest repo state...")
def _repo() -> Path:
    return ensure_repo(WORK_DIR, REPO_URL, REPO_BRANCH, GITHUB_PAT)


# Pull fresh on every reload of this Python module.
repo_path = _repo()
templates = list_templates(repo_path)

if not templates:
    st.error(f"No templates found under {repo_path}/templates/. Check REPO_URL.")
    st.stop()

template_name = st.sidebar.selectbox("Template", templates)
st.sidebar.markdown(f"`tasks/` will get a new entry named like `task011`.")

st.header(template_name)
help_md = repo_path / "templates" / template_name / "template-help.md"
if help_md.exists():
    with st.expander("Template documentation"):
        st.markdown(help_md.read_text(encoding="utf-8"))


# --- render form -----------------------------------------------------------

params = load_params(repo_path, template_name)

# Build the list of params to show: required + suggested. Skip purely optional.
visible = [
    (name, spec)
    for name, spec in params.items()
    if spec.get("required") or spec.get("suggested")
]

if not visible:
    st.warning("This template has no required or suggested parameters to ask about.")
    st.stop()

with st.form("task-form"):
    values: Dict[str, Any] = {}
    for name, spec in visible:
        label = spec["prompt"] or name
        if spec.get("required"):
            label = f"{label}  *(required)*"
        default = spec.get("default")
        enum = spec.get("enum")
        t = spec.get("type")

        if enum:
            options = list(enum)
            idx = options.index(default) if default in options else 0
            values[name] = st.selectbox(label, options, index=idx, key=name)
        elif t == "integer":
            min_v = spec.get("min") or 0
            max_v = spec.get("max") or 10**9
            default_int = int(default) if default is not None else min_v
            values[name] = st.number_input(
                label,
                min_value=int(min_v),
                max_value=int(max_v),
                value=default_int,
                step=1,
                key=name,
            )
        elif t == "boolean":
            values[name] = st.checkbox(label, value=bool(default), key=name)
        else:  # string
            values[name] = st.text_input(label, value=default or "", key=name)

    submitted = st.form_submit_button("Create task & deploy")


# --- handle submit ---------------------------------------------------------

if submitted:
    # Validate required fields
    missing = [
        n for n, spec in visible
        if spec.get("required") and (values.get(n) is None or values.get(n) == "")
    ]
    if missing:
        st.error("Required: " + ", ".join(missing))
        st.stop()

    if not (JENKINS_USER and JENKINS_API_TOKEN):
        st.error("JENKINS_USER and JENKINS_API_TOKEN must be set in the form's environment.")
        st.stop()

    # Pull fresh again right before write to minimise race with manual commits
    with st.spinner("Pulling latest repo state..."):
        _repo.clear()
        repo_path = _repo()

    task_id = next_task_id(repo_path)
    st.info(f"Generated task id: **{task_id}**")

    try:
        with st.spinner(f"Writing tasks/{task_id}/ ..."):
            task_dir = write_task(repo_path, template_name, task_id, values)
        with st.spinner("Committing and pushing..."):
            sha = commit_and_push(repo_path, task_id, template_name, REPO_BRANCH)
        st.success(f"Pushed commit `{sha}` with `tasks/{task_id}/`.")

        with st.spinner("Triggering Jenkins..."):
            queue_url = trigger_build(
                JENKINS_URL,
                JENKINS_JOB,
                JENKINS_USER,
                JENKINS_API_TOKEN,
                params={"TASK_ID": task_id, "TARGET_ENVIRONMENT": TARGET_ENVIRONMENT},
            )
        st.info(f"Queued at: {queue_url}")

        with st.spinner("Waiting for Jenkins to pick it up..."):
            build_url = wait_for_build_url(queue_url, JENKINS_USER, JENKINS_API_TOKEN)
        if build_url:
            st.success(f"Build started: [open in Jenkins]({build_url})")
        else:
            st.warning(
                "Build hasn't been picked up yet -- check Jenkins manually at the queue URL above."
            )

        st.markdown("---")
        st.subheader(f"Final `tasks/{task_id}/config.yaml`")
        st.code((task_dir / "config.yaml").read_text(encoding="utf-8"), language="yaml")

    except GitError as e:
        st.error(f"Git error:\n```\n{e}\n```")
    except JenkinsError as e:
        st.error(f"Jenkins error:\n```\n{e}\n```")
    except Exception as e:  # noqa: BLE001
        st.exception(e)
